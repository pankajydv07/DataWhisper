import os
import time

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend.auth import get_current_user  # noqa: E402
from backend.cache import cache_get, cache_set, make_key, normalise_question  # noqa: E402
from backend.formatter import dataframe_to_records, dataframe_to_table, infer_chart  # noqa: E402
from backend.insights import (  # noqa: E402
    build_comparison_payload,
    classify_intent,
    metric_refs_for_question,
)
from backend.intent import is_greeting, looks_like_data_question  # noqa: E402
from backend.llm_client import correct_sql, generate_sql  # noqa: E402
from backend.logger import logger  # noqa: E402
from backend.models import (  # noqa: E402
    AuthenticatedUser,
    CreateSessionRequest,
    MetricDictionaryResponse,
    QueryRequest,
    QueryResponse,
    SessionDetailResponse,
    SessionListResponse,
    UpdateSessionRequest,
)
from backend.query_executor import execute_sql, extract_data_sources  # noqa: E402
from backend.semantic_layer import (  # noqa: E402
    build_semantic_context,
    get_allowed_tables,
    get_metric_definitions,
    load_schema,
)
from backend.session_store import (  # noqa: E402
    append_message,
    create_session,
    delete_session,
    ensure_session,
    ensure_session_tables,
    get_history_text,
    get_session_detail,
    list_sessions,
    rename_session,
)
from backend.sql_explainer import append_trust_suffix, explain_sql, summarize_result  # noqa: E402
from backend.sql_safety import validate_sql  # noqa: E402

SUGGESTED_QUERIES = [
    "Why did revenue drop last month?",
    "Compare North vs South region this month",
    "Break down sales by category",
    "Give me a weekly summary for customer metrics",
    "Show top 5 customers by order value",
]

MAX_ROWS = int(os.getenv("MAX_ROWS", "100"))
CACHE_TTL_NL_SQL = int(os.getenv("CACHE_TTL_NL_SQL", "3600"))
CACHE_TTL_RESULTS = int(os.getenv("CACHE_TTL_RESULTS", "300"))
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

app = FastAPI(title="DataWhisper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_intent_instructions(intent_info: object) -> str:
    instructions: list[str] = []
    current_period = getattr(intent_info, "current_period_label", None)
    previous_period = getattr(intent_info, "previous_period_label", None)
    dimension = getattr(intent_info, "dimension", None)

    if current_period:
        instructions.append(f"Use the current analysis period: {current_period}.")
    if previous_period:
        instructions.append(f"Use the prior comparison period: {previous_period}.")
    if dimension:
        instructions.append(f"Prefer grouping by {dimension}.")

    intent = getattr(intent_info, "intent", "general")
    if intent == "change":
        instructions.append("Return current-period results and include enough detail to explain the biggest drivers.")
    elif intent == "compare":
        instructions.append("Return comparison-friendly columns, ideally period or segment with metric values.")
    elif intent == "breakdown":
        instructions.append("Return a ranked composition table with one dimension column and one main metric column.")
    elif intent == "summarize":
        instructions.append("Return recent trend rows with dates, metrics, and any clear anomalies.")

    assumptions = getattr(intent_info, "assumptions", None) or []
    if assumptions:
        instructions.append("Resolved assumptions: " + "; ".join(assumptions))
    return " ".join(instructions)


@app.on_event("startup")
async def startup() -> None:
    ensure_session_tables()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/metrics", response_model=MetricDictionaryResponse)
async def get_metrics(
    user: AuthenticatedUser = Depends(get_current_user),
) -> MetricDictionaryResponse:
    del user
    schema = load_schema()
    return MetricDictionaryResponse(metrics=get_metric_definitions(schema))


@app.get("/api/sessions", response_model=SessionListResponse)
async def get_sessions(
    user: AuthenticatedUser = Depends(get_current_user),
) -> SessionListResponse:
    return SessionListResponse(sessions=list_sessions(user.user_id))


@app.get("/api/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
) -> SessionDetailResponse:
    detail = get_session_detail(user.user_id, session_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return detail


@app.post("/api/sessions", response_model=SessionDetailResponse)
async def post_session(
    request: CreateSessionRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> SessionDetailResponse:
    session = create_session(user.user_id, request.title)
    return SessionDetailResponse(session=session, messages=[])


@app.patch("/api/sessions/{session_id}", response_model=SessionDetailResponse)
async def patch_session(
    session_id: str,
    request: UpdateSessionRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> SessionDetailResponse:
    session = rename_session(user.user_id, session_id, request.title)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    detail = get_session_detail(user.user_id, session_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return detail


@app.delete("/api/sessions/{session_id}")
async def remove_session(
    session_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, bool]:
    deleted = delete_session(user.user_id, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"deleted": True}


@app.post("/api/query", response_model=QueryResponse)
async def query_data(
    request: QueryRequest,
    refresh: bool = Query(default=False),
    user: AuthenticatedUser = Depends(get_current_user),
) -> QueryResponse:
    started_at = time.perf_counter()
    schema = load_schema()
    semantic_context = build_semantic_context(schema)
    allowed_tables = get_allowed_tables(schema)

    try:
        cached = False
        normalized_question = normalise_question(request.question)
        session = ensure_session(user.user_id, request.session_id, request.question)
        append_message(user.user_id, session.session_id, "user", request.question)

        if is_greeting(request.question):
            response = QueryResponse(
                session_id=session.session_id,
                session_title=session.title,
                intent="general",
                result_summary=(
                    "Ask about changes, comparisons, breakdowns, or summaries in your retail data."
                ),
                suggested_queries=SUGGESTED_QUERIES,
                execution_time_ms=int((time.perf_counter() - started_at) * 1000),
            )
            append_message(
                user.user_id,
                session.session_id,
                "assistant",
                response.result_summary,
                response,
            )
            return response

        if not looks_like_data_question(request.question):
            response = QueryResponse(
                session_id=session.session_id,
                session_title=session.title,
                intent="clarify",
                error=(
                    "I can answer questions about your retail data. Ask about revenue, orders, customers, products, regions, comparisons, or summaries."
                ),
                clarification_question=(
                    "What metric or business area do you want to explore?"
                ),
                suggested_queries=SUGGESTED_QUERIES[:3],
                execution_time_ms=int((time.perf_counter() - started_at) * 1000),
            )
            append_message(
                user.user_id,
                session.session_id,
                "assistant",
                response.error or "",
                response,
            )
            return response

        intent_info = classify_intent(request.question, schema)
        if intent_info.intent == "clarify":
            response = QueryResponse(
                session_id=session.session_id,
                session_title=session.title,
                intent="clarify",
                result_summary="I need one more detail before I answer confidently.",
                clarification_question=intent_info.clarification_question,
                assumptions=intent_info.assumptions,
                suggested_queries=SUGGESTED_QUERIES[:3],
                execution_time_ms=int((time.perf_counter() - started_at) * 1000),
            )
            append_message(
                user.user_id,
                session.session_id,
                "assistant",
                response.clarification_question or response.result_summary,
                response,
            )
            return response

        cache_identity = "|".join(
            [
                normalized_question,
                intent_info.intent,
                intent_info.current_period_label or "",
                intent_info.previous_period_label or "",
                intent_info.dimension or "",
            ]
        )

        nl_sql_key = make_key(user.user_id, cache_identity)
        sql = None if refresh else cache_get(nl_sql_key)

        if sql is None:
            sql = await generate_sql(
                question=request.question,
                user_id=user.user_id,
                semantic_layer_context=semantic_context,
                conversation_history=get_history_text(user.user_id, session.session_id),
                intent=intent_info.intent,
                intent_instructions=build_intent_instructions(intent_info),
            )
            cache_set(nl_sql_key, sql, CACHE_TTL_NL_SQL)
        else:
            cached = True

        validated_sql, validation_error = validate_sql(sql, MAX_ROWS, allowed_tables)
        if validation_error:
            logger.info(
                "unsafe_sql_blocked user_id=%s question=%s error=%s sql=%s",
                user.user_id,
                request.question,
                validation_error,
                sql,
            )
            response = QueryResponse(
                session_id=session.session_id,
                session_title=session.title,
                intent=intent_info.intent,
                error="That type of query isn't supported. Try asking a question about your data instead.",
                assumptions=intent_info.assumptions,
                suggested_queries=SUGGESTED_QUERIES[:3],
                execution_time_ms=int((time.perf_counter() - started_at) * 1000),
            )
            append_message(
                user.user_id,
                session.session_id,
                "assistant",
                response.error or "",
                response,
            )
            return response

        results_key = make_key(user.user_id, f"{intent_info.intent}|{validated_sql}")
        df = None if refresh else cache_get(results_key)

        if df is None:
            try:
                df = execute_sql(validated_sql, user.user_id, allowed_tables)
            except Exception as db_error:
                corrected_sql_raw = await correct_sql(
                    user_question=request.question,
                    user_id=user.user_id,
                    failed_sql=validated_sql,
                    error_message=str(db_error),
                    semantic_layer_context=semantic_context,
                )
                corrected_sql, corrected_error = validate_sql(
                    corrected_sql_raw,
                    MAX_ROWS,
                    allowed_tables,
                )
                if corrected_error:
                    raise db_error

                validated_sql = corrected_sql
                df = execute_sql(validated_sql, user.user_id, allowed_tables)

            cache_set(results_key, df, CACHE_TTL_RESULTS)
        else:
            cached = True

        data_sources = extract_data_sources(validated_sql)
        metric_definitions = metric_refs_for_question(
            request.question,
            schema,
            data_sources,
        )
        records = dataframe_to_records(df)
        sql_explanation = await explain_sql(validated_sql)
        raw_summary = (
            "No data matched your query. Try a broader date range or different filter."
            if df.empty
            else await summarize_result(request.question, records)
        )
        result_summary = append_trust_suffix(
            raw_summary,
            data_sources=data_sources,
            assumptions=intent_info.assumptions,
        )
        comparison = (
            build_comparison_payload(df)
            if intent_info.intent in {"compare", "change"}
            else None
        )

        logger.info(
            "query_success user_id=%s rows=%s cached=%s intent=%s sql=%s",
            user.user_id,
            len(df),
            cached,
            intent_info.intent,
            validated_sql,
        )

        response = QueryResponse(
            session_id=session.session_id,
            session_title=session.title,
            intent=intent_info.intent,
            sql=validated_sql,
            sql_explanation=sql_explanation,
            result_summary=result_summary,
            table=dataframe_to_table(df),
            chart=infer_chart(df, intent_info.intent),
            comparison=comparison,
            data_sources=data_sources,
            metric_definitions=metric_definitions,
            assumptions=intent_info.assumptions,
            cached=cached,
            execution_time_ms=int((time.perf_counter() - started_at) * 1000),
        )
        append_message(
            user.user_id,
            session.session_id,
            "assistant",
            response.error or response.result_summary,
            response,
        )
        return response

    except httpx.HTTPStatusError as error:
        logger.exception("groq_http_error user_id=%s", user.user_id)
        status_code = error.response.status_code
        message = (
            "The AI is a bit busy right now. Please wait a few seconds and try again."
            if status_code == 429
            else "I couldn't quite understand that. Try rephrasing your question."
        )
        response = QueryResponse(
            session_id=request.session_id,
            intent="general",
            error=message,
            suggested_queries=SUGGESTED_QUERIES[:3],
            execution_time_ms=int((time.perf_counter() - started_at) * 1000),
        )
        append_message(user.user_id, request.session_id, "assistant", message, response)
        return response

    except Exception:
        logger.exception(
            "query_error user_id=%s question=%s", user.user_id, request.question
        )
        response = QueryResponse(
            session_id=request.session_id,
            intent="general",
            error="Having trouble reaching the database. Please try again in a moment.",
            suggested_queries=SUGGESTED_QUERIES[:3],
            execution_time_ms=int((time.perf_counter() - started_at) * 1000),
        )
        append_message(
            user.user_id,
            request.session_id,
            "assistant",
            response.error or "",
            response,
        )
        return response

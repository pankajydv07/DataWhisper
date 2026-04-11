import os
import time

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend.auth import get_current_user  # noqa: E402
from backend.cache import cache_get, cache_set, make_key, normalise_question  # noqa: E402
from backend.conversation import add_turn, get_history_text  # noqa: E402
from backend.formatter import dataframe_to_records, dataframe_to_table, infer_chart  # noqa: E402
from backend.llm_client import correct_sql, generate_sql  # noqa: E402
from backend.logger import logger  # noqa: E402
from backend.models import AuthenticatedUser, QueryRequest, QueryResponse  # noqa: E402
from backend.query_executor import execute_sql  # noqa: E402
from backend.semantic_layer import build_semantic_context, load_schema  # noqa: E402
from backend.sql_explainer import explain_sql, summarize_result  # noqa: E402
from backend.sql_safety import validate_sql  # noqa: E402

SUGGESTED_QUERIES = [
    "What was total revenue last month?",
    "Show top 5 customers by order value",
    "Which product category has the highest sales?",
    "Compare revenue by region for 2025",
    "How many orders were cancelled this quarter?",
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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/query", response_model=QueryResponse)
async def query_data(
    request: QueryRequest,
    refresh: bool = Query(default=False),
    user: AuthenticatedUser = Depends(get_current_user),
) -> QueryResponse:
    started_at = time.perf_counter()
    schema = load_schema()
    semantic_context = build_semantic_context(schema)

    try:
        cached = False
        normalized_question = normalise_question(request.question)
        nl_sql_key = make_key(user.user_id, normalized_question)
        sql = None if refresh else cache_get(nl_sql_key)

        if sql is None:
            sql = await generate_sql(
                question=request.question,
                user_id=user.user_id,
                semantic_layer_context=semantic_context,
                conversation_history=get_history_text(user.user_id, request.session_id),
            )
            cache_set(nl_sql_key, sql, CACHE_TTL_NL_SQL)
        else:
            cached = True

        validated_sql, validation_error = validate_sql(sql, MAX_ROWS)
        if validation_error:
            logger.info(
                "unsafe_sql_blocked user_id=%s question=%s error=%s sql=%s",
                user.user_id,
                request.question,
                validation_error,
                sql,
            )
            return QueryResponse(
                error="That type of query isn't supported. Try asking a question about your data instead.",
                suggested_queries=SUGGESTED_QUERIES[:3],
                execution_time_ms=int((time.perf_counter() - started_at) * 1000),
            )

        results_key = make_key(user.user_id, validated_sql)
        df = None if refresh else cache_get(results_key)

        if df is None:
            try:
                df = execute_sql(validated_sql, user.user_id)
            except Exception as db_error:
                corrected_sql_raw = await correct_sql(
                    user_question=request.question,
                    user_id=user.user_id,
                    failed_sql=validated_sql,
                    error_message=str(db_error),
                    semantic_layer_context=semantic_context,
                )
                corrected_sql, corrected_error = validate_sql(
                    corrected_sql_raw, MAX_ROWS
                )
                if corrected_error:
                    raise db_error

                validated_sql = corrected_sql
                df = execute_sql(validated_sql, user.user_id)

            cache_set(results_key, df, CACHE_TTL_RESULTS)
        else:
            cached = True

        records = dataframe_to_records(df)
        sql_explanation = await explain_sql(validated_sql)
        result_summary = (
            "No data matched your query. Try a broader date range or different filter."
            if df.empty
            else await summarize_result(request.question, records)
        )

        add_turn(user.user_id, request.session_id, request.question, validated_sql)

        logger.info(
            "query_success user_id=%s rows=%s cached=%s sql=%s",
            user.user_id,
            len(df),
            cached,
            validated_sql,
        )

        return QueryResponse(
            sql=validated_sql,
            sql_explanation=sql_explanation,
            result_summary=result_summary,
            table=dataframe_to_table(df),
            chart=infer_chart(df),
            cached=cached,
            execution_time_ms=int((time.perf_counter() - started_at) * 1000),
        )

    except httpx.HTTPStatusError as error:
        logger.exception("groq_http_error user_id=%s", user.user_id)
        status_code = error.response.status_code
        message = (
            "The AI is a bit busy right now. Please wait a few seconds and try again."
            if status_code == 429
            else "I couldn't quite understand that. Try rephrasing your question."
        )
        return QueryResponse(
            error=message,
            suggested_queries=SUGGESTED_QUERIES[:3],
            execution_time_ms=int((time.perf_counter() - started_at) * 1000),
        )

    except Exception:
        logger.exception(
            "query_error user_id=%s question=%s", user.user_id, request.question
        )
        return QueryResponse(
            error="Having trouble reaching the database. Please try again in a moment.",
            suggested_queries=SUGGESTED_QUERIES[:3],
            execution_time_ms=int((time.perf_counter() - started_at) * 1000),
        )

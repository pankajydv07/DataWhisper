from decimal import Decimal
from backend.session_store import DEFAULT_SESSION_TITLE, auto_title_from_question, messages_to_history_text
from backend.models import QueryResponse, StoredChatMessage
from datetime import datetime, UTC


def test_auto_title_trims_and_shortens() -> None:
    title = auto_title_from_question("   Show me revenue by region for 2025 please   ")
    assert title.startswith("Show me revenue")
    assert len(title) <= 80


def test_auto_title_defaults_when_blank() -> None:
    assert auto_title_from_question("   ") == DEFAULT_SESSION_TITLE


def test_messages_to_history_text_uses_assistant_sql() -> None:
    now = datetime.now(UTC)
    messages = [
        StoredChatMessage(
            message_id="1",
            session_id="s1",
            user_id="u1",
            role="user",
            content="What was total revenue last month?",
            created_at=now,
        ),
        StoredChatMessage(
            message_id="2",
            session_id="s1",
            user_id="u1",
            role="assistant",
            content="Revenue was 100.",
            response=QueryResponse(sql="SELECT 100", result_summary="Revenue was 100."),
            created_at=now,
        ),
    ]

    history = messages_to_history_text(messages)
    assert "User: What was total revenue last month?" in history
    assert "SQL: SELECT 100" in history


def test_query_response_json_mode_serializes_decimal_rows() -> None:
    response = QueryResponse(
        sql="SELECT 1",
        sql_explanation="test",
        result_summary="test",
        table={
            "columns": ["revenue"],
            "rows": [[Decimal("123.45")]],
        },
    )

    payload = response.model_dump(mode="json")
    assert payload["table"]["rows"][0][0] == "123.45"

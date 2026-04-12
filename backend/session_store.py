import os
import uuid
from typing import Any, Iterable

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from backend.models import ChatSession, QueryResponse, SessionDetailResponse, StoredChatMessage

DATABASE_URL = os.getenv("SUPABASE_DB_URL", "")
DEFAULT_SESSION_TITLE = "New chat"


def get_connection() -> psycopg.Connection:
    if not DATABASE_URL:
        raise RuntimeError("SUPABASE_DB_URL is not configured.")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def ensure_session_tables() -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS chat_sessions (
      session_id text PRIMARY KEY,
      user_id text NOT NULL,
      title text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now(),
      last_message_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS chat_messages (
      message_id text PRIMARY KEY,
      session_id text NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
      user_id text NOT NULL,
      role text NOT NULL CHECK (role IN ('user', 'assistant')),
      content text NOT NULL,
      response_json jsonb NULL,
      created_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_last_message
      ON chat_sessions(user_id, last_message_at DESC);
    CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created
      ON chat_messages(session_id, created_at ASC);
    CREATE INDEX IF NOT EXISTS idx_chat_messages_user_session
      ON chat_messages(user_id, session_id);
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(ddl)
        connection.commit()


def auto_title_from_question(question: str) -> str:
    normalized = " ".join(question.strip().split())
    if not normalized:
        return DEFAULT_SESSION_TITLE
    return normalized[:80]


def _row_to_session(row: dict[str, Any]) -> ChatSession:
    return ChatSession.model_validate(row)


def _row_to_message(row: dict[str, Any]) -> StoredChatMessage:
    response_payload = row.get("response_json")
    return StoredChatMessage(
        message_id=row["message_id"],
        session_id=row["session_id"],
        user_id=row["user_id"],
        role=row["role"],
        content=row["content"],
        response=QueryResponse.model_validate(response_payload) if response_payload else None,
        created_at=row["created_at"],
    )


def create_session(user_id: str, title: str | None = None) -> ChatSession:
    session_id = str(uuid.uuid4())
    session_title = title.strip() if title else DEFAULT_SESSION_TITLE

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO chat_sessions (session_id, user_id, title)
                VALUES (%s, %s, %s)
                RETURNING session_id, user_id, title, created_at, updated_at, last_message_at
                """,
                (session_id, user_id, session_title),
            )
            row = cursor.fetchone()
        connection.commit()

    return _row_to_session(row)


def ensure_session(user_id: str, session_id: str, initial_question: str | None = None) -> ChatSession:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT session_id, user_id, title, created_at, updated_at, last_message_at
                FROM chat_sessions
                WHERE session_id = %s AND user_id = %s
                """,
                (session_id, user_id),
            )
            row = cursor.fetchone()

            if row is None:
                title = auto_title_from_question(initial_question or "")
                cursor.execute(
                    """
                    INSERT INTO chat_sessions (session_id, user_id, title)
                    VALUES (%s, %s, %s)
                    RETURNING session_id, user_id, title, created_at, updated_at, last_message_at
                    """,
                    (session_id, user_id, title),
                )
                row = cursor.fetchone()
            elif row["title"] == DEFAULT_SESSION_TITLE and initial_question:
                cursor.execute(
                    """
                    UPDATE chat_sessions
                    SET title = %s, updated_at = now()
                    WHERE session_id = %s AND user_id = %s
                    RETURNING session_id, user_id, title, created_at, updated_at, last_message_at
                    """,
                    (auto_title_from_question(initial_question), session_id, user_id),
                )
                row = cursor.fetchone()
        connection.commit()

    return _row_to_session(row)


def list_sessions(user_id: str) -> list[ChatSession]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT session_id, user_id, title, created_at, updated_at, last_message_at
                FROM chat_sessions
                WHERE user_id = %s
                ORDER BY last_message_at DESC, created_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()

    return [_row_to_session(row) for row in rows]


def get_session_detail(user_id: str, session_id: str) -> SessionDetailResponse | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT session_id, user_id, title, created_at, updated_at, last_message_at
                FROM chat_sessions
                WHERE session_id = %s AND user_id = %s
                """,
                (session_id, user_id),
            )
            session_row = cursor.fetchone()
            if session_row is None:
                return None

            cursor.execute(
                """
                SELECT message_id, session_id, user_id, role, content, response_json, created_at
                FROM chat_messages
                WHERE session_id = %s AND user_id = %s
                ORDER BY created_at ASC
                """,
                (session_id, user_id),
            )
            message_rows = cursor.fetchall()

    return SessionDetailResponse(
        session=_row_to_session(session_row),
        messages=[_row_to_message(row) for row in message_rows],
    )


def rename_session(user_id: str, session_id: str, title: str) -> ChatSession | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE chat_sessions
                SET title = %s, updated_at = now()
                WHERE session_id = %s AND user_id = %s
                RETURNING session_id, user_id, title, created_at, updated_at, last_message_at
                """,
                (title.strip(), session_id, user_id),
            )
            row = cursor.fetchone()
        connection.commit()

    return _row_to_session(row) if row else None


def delete_session(user_id: str, session_id: str) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM chat_sessions WHERE session_id = %s AND user_id = %s",
                (session_id, user_id),
            )
            deleted = cursor.rowcount > 0
        connection.commit()

    return deleted


def append_message(
    user_id: str,
    session_id: str,
    role: str,
    content: str,
    response: QueryResponse | None = None,
) -> StoredChatMessage:
    message_id = str(uuid.uuid4())
    response_payload = response.model_dump(mode="json") if response else None

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO chat_messages (message_id, session_id, user_id, role, content, response_json)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                RETURNING message_id, session_id, user_id, role, content, response_json, created_at
                """,
                (
                    message_id,
                    session_id,
                    user_id,
                    role,
                    content,
                    Jsonb(response_payload) if response_payload is not None else None,
                ),
            )
            row = cursor.fetchone()

            cursor.execute(
                """
                UPDATE chat_sessions
                SET updated_at = now(), last_message_at = now()
                WHERE session_id = %s AND user_id = %s
                """,
                (session_id, user_id),
            )
        connection.commit()

    return _row_to_message(row)


def messages_to_history_text(messages: Iterable[StoredChatMessage]) -> str:
    lines: list[str] = []
    pending_user_question: str | None = None

    for message in messages:
        if message.role == "user":
            pending_user_question = message.content
            continue

        if pending_user_question:
            sql = message.response.sql if message.response else ""
            lines.append(f"User: {pending_user_question}\nSQL: {sql}")
            pending_user_question = None

    return "\n".join(lines) if lines else "No prior turns."


def get_history_text(user_id: str, session_id: str, max_turns: int = 3) -> str:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT message_id, session_id, user_id, role, content, response_json, created_at
                FROM chat_messages
                WHERE session_id = %s AND user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (session_id, user_id, max_turns * 2),
            )
            rows = cursor.fetchall()

    messages = [_row_to_message(row) for row in reversed(rows)]
    return messages_to_history_text(messages)

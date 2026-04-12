from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    session_id: str = Field(min_length=1, max_length=128)


class TablePayload(BaseModel):
    columns: list[str]
    rows: list[list[Any]]


class ChartPayload(BaseModel):
    type: Literal["bar", "line"]
    x: str
    y: str


class QueryResponse(BaseModel):
    session_id: str | None = None
    session_title: str | None = None
    sql: str = ""
    sql_explanation: str = ""
    result_summary: str = ""
    table: TablePayload | None = None
    chart: ChartPayload | None = None
    cached: bool = False
    execution_time_ms: int = 0
    error: str | None = None
    suggested_queries: list[str] | None = None


class AuthenticatedUser(BaseModel):
    user_id: str
    email: str | None = None


class ChatSession(BaseModel):
    session_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime


class StoredChatMessage(BaseModel):
    message_id: str
    session_id: str
    user_id: str
    role: Literal["user", "assistant"]
    content: str
    response: QueryResponse | None = None
    created_at: datetime


class SessionListResponse(BaseModel):
    sessions: list[ChatSession]


class SessionDetailResponse(BaseModel):
    session: ChatSession
    messages: list[StoredChatMessage]


class CreateSessionRequest(BaseModel):
    title: str | None = Field(default=None, max_length=120)


class UpdateSessionRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)

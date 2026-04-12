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
    type: Literal["bar", "line", "pie", "stacked_bar"]
    x: str
    y: str
    series: list[str] = Field(default_factory=list)


class MetricDefinitionRef(BaseModel):
    key: str
    label: str
    definition: str
    formula: str | None = None
    source_tables: list[str] = Field(default_factory=list)
    default_time_grain: str | None = None


class ComparisonPayload(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    focus: str | None = None


QueryIntent = Literal[
    "change",
    "compare",
    "breakdown",
    "summarize",
    "general",
    "clarify",
]


class QueryResponse(BaseModel):
    session_id: str | None = None
    session_title: str | None = None
    intent: QueryIntent = "general"
    sql: str = ""
    sql_explanation: str = ""
    result_summary: str = ""
    table: TablePayload | None = None
    chart: ChartPayload | None = None
    comparison: ComparisonPayload | None = None
    data_sources: list[str] = Field(default_factory=list)
    metric_definitions: list[MetricDefinitionRef] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    clarification_question: str | None = None
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


class MetricDictionaryResponse(BaseModel):
    metrics: list[MetricDefinitionRef]

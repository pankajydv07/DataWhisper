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

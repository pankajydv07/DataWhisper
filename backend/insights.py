import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import pandas as pd

from backend.models import ComparisonPayload, MetricDefinitionRef

COMPARE_PATTERN = re.compile(r"\b(compare|vs|versus|against)\b", re.IGNORECASE)
CHANGE_PATTERN = re.compile(
    r"\b(why did|why has|what changed|drop|decline|increase|decrease|grew|grew by|fell)\b",
    re.IGNORECASE,
)
BREAKDOWN_PATTERN = re.compile(
    r"\b(breakdown|break down|decompose|make up|makes up|composition|contribution)\b",
    re.IGNORECASE,
)
SUMMARY_PATTERN = re.compile(
    r"\b(summary|summarize|digest|what happened|weekly summary|monthly summary)\b",
    re.IGNORECASE,
)
TIME_PATTERNS = {
    "this week": ("week", 0),
    "last week": ("week", -1),
    "this month": ("month", 0),
    "last month": ("month", -1),
    "this quarter": ("quarter", 0),
    "last quarter": ("quarter", -1),
    "year to date": ("ytd", 0),
}
DIMENSION_HINTS = {
    "region": "customers.region",
    "category": "products.category",
    "sub-category": "products.sub_category",
    "subcategory": "products.sub_category",
    "product": "products.name",
    "segment": "customers.segment",
    "customer": "customers.name",
    "status": "orders.status",
}


@dataclass
class IntentInfo:
    intent: str
    assumptions: list[str] = field(default_factory=list)
    clarification_question: str | None = None
    metric_key: str = "revenue"
    dimension: str | None = None
    current_period_label: str | None = None
    previous_period_label: str | None = None
    date_filter_sql: str | None = None
    compare_filter_sql: str | None = None


def _start_of_week(today: date) -> date:
    return today - timedelta(days=today.weekday())


def _shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    total = (year * 12 + (month - 1)) + offset
    return total // 12, total % 12 + 1


def resolve_period_range(label: str, today: date | None = None) -> tuple[date, date]:
    today = today or date.today()
    if label == "this week":
        start = _start_of_week(today)
        return start, start + timedelta(days=7)
    if label == "last week":
        end = _start_of_week(today)
        return end - timedelta(days=7), end
    if label == "this month":
        start = today.replace(day=1)
        year, month = _shift_month(start.year, start.month, 1)
        return start, date(year, month, 1)
    if label == "last month":
        end = today.replace(day=1)
        year, month = _shift_month(end.year, end.month, -1)
        return date(year, month, 1), end
    if label == "this quarter":
        quarter_month = ((today.month - 1) // 3) * 3 + 1
        start = date(today.year, quarter_month, 1)
        year, month = _shift_month(start.year, start.month, 3)
        return start, date(year, month, 1)
    if label == "last quarter":
        current_start = resolve_period_range("this quarter", today)[0]
        year, month = _shift_month(current_start.year, current_start.month, -3)
        start = date(year, month, 1)
        return start, current_start
    if label == "year to date":
        return date(today.year, 1, 1), today + timedelta(days=1)
    raise ValueError(f"Unsupported period label: {label}")


def _sql_date_range(label: str, today: date | None = None) -> str:
    start, end = resolve_period_range(label, today)
    return (
        f"orders.order_date >= DATE '{start.isoformat()}' "
        f"AND orders.order_date < DATE '{end.isoformat()}'"
    )


def _detect_metric(question: str, schema: dict[str, Any]) -> str:
    lowered = question.lower()
    for metric in schema.get("metrics", []):
        candidates = [metric["key"], *metric.get("synonyms", [])]
        if any(candidate.lower() in lowered for candidate in candidates):
            return metric["key"]
    if "complaint" in lowered:
        return "cancelled_orders"
    return "revenue"


def _detect_dimension(question: str) -> str | None:
    lowered = question.lower()
    for hint, dimension in DIMENSION_HINTS.items():
        if hint in lowered:
            return dimension
    return None


def classify_intent(question: str, schema: dict[str, Any]) -> IntentInfo:
    lowered = question.lower()
    metric_key = _detect_metric(question, schema)
    dimension = _detect_dimension(question)

    if SUMMARY_PATTERN.search(question):
        intent = "summarize"
    elif BREAKDOWN_PATTERN.search(question):
        intent = "breakdown"
    elif COMPARE_PATTERN.search(question):
        intent = "compare"
    elif CHANGE_PATTERN.search(question):
        intent = "change"
    else:
        intent = "general"

    info = IntentInfo(intent=intent, metric_key=metric_key, dimension=dimension)

    matched_periods = [label for label in TIME_PATTERNS if label in lowered]
    if matched_periods:
        info.current_period_label = matched_periods[0]
        info.date_filter_sql = _sql_date_range(matched_periods[0])
        if matched_periods[0].startswith("this "):
            info.previous_period_label = matched_periods[0].replace("this ", "last ", 1)
        elif matched_periods[0] == "year to date":
            info.previous_period_label = None

    if intent == "change" and info.current_period_label is None:
        info.intent = "clarify"
        info.clarification_question = (
            "Which time period should I analyze for the change: this week, last week, this month, or last month?"
        )
    elif intent == "compare" and "vs" not in lowered and "versus" not in lowered and dimension is None and info.current_period_label is None:
        info.intent = "clarify"
        info.clarification_question = (
            "What should I compare: time periods, regions, products, or customer segments?"
        )
    elif intent == "breakdown" and dimension is None:
        info.assumptions.append("Used region as the default breakdown because no dimension was specified.")
        info.dimension = "customers.region"
    elif intent == "summarize" and info.current_period_label is None:
        info.assumptions.append("Assumed you wanted a weekly summary.")
        info.current_period_label = "this week"
        info.date_filter_sql = _sql_date_range("this week")

    if intent in {"change", "compare"} and info.current_period_label and info.previous_period_label:
        info.compare_filter_sql = _sql_date_range(info.previous_period_label)

    return info


def metric_refs_for_question(
    question: str, schema: dict[str, Any], data_sources: list[str]
) -> list[MetricDefinitionRef]:
    lowered = question.lower()
    refs: list[MetricDefinitionRef] = []
    for metric in schema.get("metrics", []):
        candidates = [metric["key"], *metric.get("synonyms", [])]
        if any(candidate.lower() in lowered for candidate in candidates):
            refs.append(
                MetricDefinitionRef(
                    key=metric["key"],
                    label=metric.get("label", metric["key"].replace("_", " ").title()),
                    definition=metric["definition"],
                    formula=metric.get("formula"),
                    source_tables=metric.get("source_tables", []),
                    default_time_grain=metric.get("default_time_grain"),
                )
            )

    if not refs:
        for metric in schema.get("metrics", []):
            if set(metric.get("source_tables", [])) & set(data_sources):
                refs.append(
                    MetricDefinitionRef(
                        key=metric["key"],
                        label=metric.get("label", metric["key"].replace("_", " ").title()),
                        definition=metric["definition"],
                        formula=metric.get("formula"),
                        source_tables=metric.get("source_tables", []),
                        default_time_grain=metric.get("default_time_grain"),
                    )
                )
                if len(refs) == 2:
                    break
    return refs


def build_comparison_payload(df: pd.DataFrame) -> ComparisonPayload | None:
    if df.empty:
        return None

    lowered_columns = {str(column).lower(): str(column) for column in df.columns}
    if "period" in lowered_columns and len(df.columns) >= 2:
        focus = next((column for column in df.columns if str(column).lower() != "period"), None)
        if focus is None:
            return None
        rows = dataframe_preview(df)
        return ComparisonPayload(columns=[str(column) for column in df.columns], rows=rows, focus=str(focus))

    delta_column = next(
        (str(column) for column in df.columns if "delta" in str(column).lower()),
        None,
    )
    if delta_column:
        return ComparisonPayload(
            columns=[str(column) for column in df.columns],
            rows=dataframe_preview(df),
            focus=delta_column,
        )

    return None


def dataframe_preview(df: pd.DataFrame, limit: int = 8) -> list[dict[str, Any]]:
    safe_df = df.head(limit).astype(object).where(pd.notnull(df.head(limit)), None)
    return safe_df.to_dict(orient="records")

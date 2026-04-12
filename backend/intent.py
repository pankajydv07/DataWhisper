import re

GREETING_PATTERN = re.compile(
    r"^\s*(hi|hello|hey|yo|namaste|good\s+(morning|afternoon|evening))[\s!.]*$",
    re.IGNORECASE,
)

DATA_TERMS = {
    "revenue",
    "sales",
    "orders",
    "customers",
    "products",
    "category",
    "region",
    "segment",
    "cancelled",
    "completed",
    "pending",
    "top",
    "compare",
    "average",
    "count",
    "total",
    "compare",
    "versus",
    "vs",
    "summary",
    "summarize",
    "breakdown",
    "break down",
    "what changed",
    "why did",
    "last month",
    "this month",
    "this week",
    "last week",
    "quarter",
    "2025",
}


def is_greeting(question: str) -> bool:
    return bool(GREETING_PATTERN.match(question))


def looks_like_data_question(question: str) -> bool:
    lowered = question.lower()
    return any(term in lowered for term in DATA_TERMS)

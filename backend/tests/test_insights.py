from datetime import date

from backend.insights import classify_intent, resolve_period_range
from backend.query_executor import extract_data_sources
from backend.semantic_layer import load_schema


def test_classifies_change_query() -> None:
    schema = load_schema()
    info = classify_intent("Why did revenue drop last month?", schema)
    assert info.intent == "change"
    assert info.metric_key == "revenue"
    assert info.current_period_label == "last month"


def test_classifies_breakdown_and_defaults_dimension() -> None:
    schema = load_schema()
    info = classify_intent("What makes up total sales?", schema)
    assert info.intent == "breakdown"
    assert info.dimension == "customers.region"
    assert info.assumptions


def test_returns_clarification_for_ambiguous_change() -> None:
    schema = load_schema()
    info = classify_intent("Why did revenue drop?", schema)
    assert info.intent == "clarify"
    assert info.clarification_question is not None


def test_resolves_last_month_period() -> None:
    start, end = resolve_period_range("last month", today=date(2026, 4, 12))
    assert start.isoformat() == "2026-03-01"
    assert end.isoformat() == "2026-04-01"


def test_extracts_data_sources() -> None:
    sql = """
    SELECT customers.region, SUM(order_items.quantity)
    FROM orders
    JOIN customers ON customers.customer_id = orders.customer_id
    JOIN order_items ON order_items.order_id = orders.order_id
    """
    assert extract_data_sources(sql) == ["orders", "customers", "order_items"]

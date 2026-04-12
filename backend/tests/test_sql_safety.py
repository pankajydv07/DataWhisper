from backend.sql_safety import validate_sql

ALLOWED_TABLES = {"orders", "customers", "order_items", "products"}


def test_rejects_delete() -> None:
    _, error = validate_sql("DELETE FROM orders", allowed_tables=ALLOWED_TABLES)
    assert error is not None


def test_rejects_markdown_unsafe_sql() -> None:
    _, error = validate_sql("```sql\nDROP TABLE orders\n```", allowed_tables=ALLOWED_TABLES)
    assert error is not None


def test_accepts_select_and_adds_limit() -> None:
    sql, error = validate_sql("SELECT * FROM orders", allowed_tables=ALLOWED_TABLES)
    assert error is None
    assert "LIMIT 100" in sql


def test_preserves_existing_limit() -> None:
    sql, error = validate_sql("SELECT * FROM orders LIMIT 5", allowed_tables=ALLOWED_TABLES)
    assert error is None
    assert sql.endswith("LIMIT 5")


def test_rejects_semicolon() -> None:
    _, error = validate_sql(
        "SELECT * FROM orders; SELECT * FROM customers",
        allowed_tables=ALLOWED_TABLES,
    )
    assert error is not None


def test_rejects_constant_only_select() -> None:
    _, error = validate_sql(
        "SELECT 'Hello, user_123' AS greeting",
        allowed_tables=ALLOWED_TABLES,
    )
    assert error is not None


def test_rejects_unknown_table() -> None:
    _, error = validate_sql(
        "SELECT * FROM payments",
        allowed_tables=ALLOWED_TABLES,
    )
    assert error is not None

from backend.sql_safety import validate_sql


def test_rejects_delete() -> None:
    _, error = validate_sql("DELETE FROM orders")
    assert error is not None


def test_rejects_markdown_unsafe_sql() -> None:
    _, error = validate_sql("```sql\nDROP TABLE orders\n```")
    assert error is not None


def test_accepts_select_and_adds_limit() -> None:
    sql, error = validate_sql("SELECT * FROM orders")
    assert error is None
    assert "LIMIT 100" in sql


def test_preserves_existing_limit() -> None:
    sql, error = validate_sql("SELECT * FROM orders LIMIT 5")
    assert error is None
    assert sql.endswith("LIMIT 5")


def test_rejects_semicolon() -> None:
    _, error = validate_sql("SELECT * FROM orders; SELECT * FROM customers")
    assert error is not None


def test_rejects_constant_only_select() -> None:
    _, error = validate_sql("SELECT 'Hello, user_123' AS greeting")
    assert error is not None

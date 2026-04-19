from backend.query_executor import enforce_user_scope

ALLOWED_TABLES = {"orders", "customers", "order_items", "products"}
USER_ID = "user_3CDmRritRk2iiHMxrRvijsrwn6y"


def test_accepts_simple_alias_user_scope() -> None:
    sql = f"""
    SELECT SUM(oi.quantity * p.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.user_id = '{USER_ID}'
      AND oi.user_id = '{USER_ID}'
      AND p.user_id = '{USER_ID}'
    LIMIT 100
    """

    assert enforce_user_scope(sql, USER_ID, ALLOWED_TABLES) == sql


def test_accepts_alias_user_scope_without_spaces() -> None:
    sql = f"SELECT * FROM orders o WHERE o.user_id='{USER_ID}' LIMIT 100"

    assert enforce_user_scope(sql, USER_ID, ALLOWED_TABLES) == sql


def test_appends_missing_alias_user_scope() -> None:
    sql = f"""
    SELECT *
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.user_id = '{USER_ID}'
    LIMIT 100
    """

    scoped_sql = enforce_user_scope(sql, USER_ID, ALLOWED_TABLES)

    assert f"AND oi.user_id = '{USER_ID}'" in scoped_sql
    assert scoped_sql.strip().endswith("LIMIT 100")


def test_appends_all_missing_scopes_before_order_by_and_limit() -> None:
    sql = """
    SELECT *
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    ORDER BY o.order_date DESC
    LIMIT 100
    """

    scoped_sql = enforce_user_scope(sql, USER_ID, ALLOWED_TABLES)

    assert f"WHERE o.user_id = '{USER_ID}' AND oi.user_id = '{USER_ID}'" in scoped_sql
    assert scoped_sql.index("WHERE") < scoped_sql.index("ORDER BY")

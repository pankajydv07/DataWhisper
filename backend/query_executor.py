import os

import pandas as pd
import psycopg

DATABASE_URL = os.getenv("SUPABASE_DB_URL", "")


def enforce_user_scope(sql: str, user_id: str) -> str:
    # TODO: Replace this MVP guard with SQL AST validation before production.
    # Supabase service-role database connections can bypass RLS, so generated SQL
    # must be explicitly scoped to the authenticated Clerk user_id.
    lowered_sql = sql.lower()

    if "user_id" not in lowered_sql:
        raise ValueError("Generated SQL is missing user_id scope.")

    if user_id not in sql:
        raise ValueError("Generated SQL does not include authenticated user_id.")

    return sql


def execute_sql(sql: str, user_id: str) -> pd.DataFrame:
    if not DATABASE_URL:
        raise RuntimeError("SUPABASE_DB_URL is not configured.")

    scoped_sql = enforce_user_scope(sql, user_id)

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(scoped_sql)
            rows = cursor.fetchall()
            columns = [description.name for description in cursor.description]

    return pd.DataFrame(rows, columns=columns)

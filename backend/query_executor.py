import os
import re

import pandas as pd
import psycopg

DATABASE_URL = os.getenv("SUPABASE_DB_URL", "")
TABLE_PATTERN = re.compile(r"\b(?:from|join)\s+([a-zA-Z_][\w]*)", re.IGNORECASE)
ALIAS_PATTERN = re.compile(
    r"\b(?:from|join)\s+([a-zA-Z_][\w]*)(?:\s+(?:as\s+)?([a-zA-Z_][\w]*))?",
    re.IGNORECASE,
)
USER_SCOPE_PATTERN = "({alias}.user_id = '{user_id}' OR {alias}.user_id='{user_id}')"


def extract_data_sources(sql: str) -> list[str]:
    sources: list[str] = []
    for match in TABLE_PATTERN.finditer(sql):
        table_name = match.group(1)
        if table_name not in sources:
            sources.append(table_name)
    return sources


def _extract_table_aliases(sql: str) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for match in ALIAS_PATTERN.finditer(sql):
        table_name = match.group(1)
        alias = match.group(2) or table_name
        if alias.lower() == "on":
            alias = table_name
        aliases[alias] = table_name
    return aliases


def enforce_user_scope(sql: str, user_id: str, allowed_tables: set[str] | None = None) -> str:
    aliases = _extract_table_aliases(sql)

    if not aliases:
        raise ValueError("Generated SQL must reference approved data tables.")

    if allowed_tables is not None:
        unknown_tables = {table for table in aliases.values() if table not in allowed_tables}
        if unknown_tables:
            raise ValueError(f"Generated SQL references unsupported tables: {sorted(unknown_tables)}")

    if user_id not in sql:
        raise ValueError("Generated SQL does not include authenticated user_id.")

    for alias in aliases:
        pattern = USER_SCOPE_PATTERN.format(alias=re.escape(alias), user_id=re.escape(user_id))
        if not re.search(pattern, sql, flags=re.IGNORECASE):
            raise ValueError(f"Generated SQL is missing user scope for table alias '{alias}'.")

    return sql


def execute_sql(sql: str, user_id: str, allowed_tables: set[str] | None = None) -> pd.DataFrame:
    if not DATABASE_URL:
        raise RuntimeError("SUPABASE_DB_URL is not configured.")

    scoped_sql = enforce_user_scope(sql, user_id, allowed_tables)

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(scoped_sql)
            rows = cursor.fetchall()
            columns = [description.name for description in cursor.description]

    return pd.DataFrame(rows, columns=columns)

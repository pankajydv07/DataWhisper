import re

import pandas as pd

from backend.db import connect

TABLE_PATTERN = re.compile(r"\b(?:from|join)\s+([a-zA-Z_][\w]*)", re.IGNORECASE)
ALIAS_PATTERN = re.compile(
    r"\b(?:from|join)\s+([a-zA-Z_][\w]*)(?:\s+(?:as\s+)?([a-zA-Z_][\w]*))?",
    re.IGNORECASE,
)
RESERVED_ALIAS_KEYWORDS = {
    "as",
    "cross",
    "full",
    "group",
    "having",
    "inner",
    "join",
    "left",
    "limit",
    "on",
    "order",
    "outer",
    "right",
    "where",
}


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
        if alias.lower() in RESERVED_ALIAS_KEYWORDS:
            alias = table_name
        aliases[alias] = table_name
    return aliases


def _has_alias_user_scope(sql: str, alias: str, user_id: str) -> bool:
    pattern = (
        rf"\b{re.escape(alias)}\s*\.\s*user_id\s*=\s*"
        rf"'{re.escape(user_id)}'"
    )
    return re.search(pattern, sql, flags=re.IGNORECASE) is not None


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _find_top_level_clause(sql: str, clause: str, start: int = 0) -> int:
    clause = clause.lower()
    depth = 0
    index = start

    while index < len(sql):
        character = sql[index]
        if character == "'":
            index += 1
            while index < len(sql):
                if sql[index] == "'" and index + 1 < len(sql) and sql[index + 1] == "'":
                    index += 2
                    continue
                if sql[index] == "'":
                    break
                index += 1
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
        elif depth == 0 and sql[index : index + len(clause)].lower() == clause:
            before = sql[index - 1] if index > 0 else " "
            after_index = index + len(clause)
            after = sql[after_index] if after_index < len(sql) else " "
            if not (before.isalnum() or before == "_") and not (
                after.isalnum() or after == "_"
            ):
                return index
        index += 1

    return -1


def _find_scope_insert_position(sql: str) -> int:
    positions = [
        position
        for clause in ("group by", "having", "order by", "limit")
        if (position := _find_top_level_clause(sql, clause)) >= 0
    ]
    return min(positions) if positions else len(sql)


def _append_missing_user_scopes(sql: str, aliases: dict[str, str], user_id: str) -> str:
    missing_aliases = [
        alias for alias in aliases if not _has_alias_user_scope(sql, alias, user_id)
    ]
    if not missing_aliases:
        return sql

    conditions = [
        f"{alias}.user_id = {_sql_literal(user_id)}" for alias in missing_aliases
    ]
    insert_position = _find_scope_insert_position(sql)
    base = sql[:insert_position].rstrip()
    suffix = sql[insert_position:].lstrip()
    where_position = _find_top_level_clause(base, "where")
    scope_clause = " AND ".join(conditions)
    separator = " AND " if where_position >= 0 else " WHERE "

    return f"{base}{separator}{scope_clause}" + (f" {suffix}" if suffix else "")


def enforce_user_scope(sql: str, user_id: str, allowed_tables: set[str] | None = None) -> str:
    aliases = _extract_table_aliases(sql)

    if not aliases:
        raise ValueError("Generated SQL must reference approved data tables.")

    if allowed_tables is not None:
        unknown_tables = {table for table in aliases.values() if table not in allowed_tables}
        if unknown_tables:
            raise ValueError(f"Generated SQL references unsupported tables: {sorted(unknown_tables)}")

    return _append_missing_user_scopes(sql, aliases, user_id)


def execute_sql(sql: str, user_id: str, allowed_tables: set[str] | None = None) -> pd.DataFrame:
    scoped_sql = enforce_user_scope(sql, user_id, allowed_tables)

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(scoped_sql)
            rows = cursor.fetchall()
            columns = [description.name for description in cursor.description]

    return pd.DataFrame(rows, columns=columns)

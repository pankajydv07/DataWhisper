import re

from backend.query_executor import extract_data_sources

BLOCKED_KEYWORDS = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "TRUNCATE",
    "ALTER",
    "CREATE",
    "EXEC",
    "EXECUTE",
    "--",
    ";",
]

LIMIT_PATTERN = re.compile(r"\blimit\s+\d+\b", re.IGNORECASE)
FROM_PATTERN = re.compile(r"\bfrom\b", re.IGNORECASE)


def strip_markdown_fences(sql: str) -> str:
    cleaned_sql = sql.strip()
    cleaned_sql = re.sub(r"^```(?:sql)?", "", cleaned_sql, flags=re.IGNORECASE).strip()
    cleaned_sql = re.sub(r"```$", "", cleaned_sql).strip()
    return cleaned_sql


def has_balanced_parentheses(sql: str) -> bool:
    depth = 0
    for character in sql:
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1

        if depth < 0:
            return False

    return depth == 0


def validate_sql(
    sql: str,
    max_rows: int = 100,
    allowed_tables: set[str] | None = None,
) -> tuple[str, str | None]:
    cleaned_sql = strip_markdown_fences(sql).strip()

    if not cleaned_sql.upper().startswith("SELECT"):
        return cleaned_sql, "Only SELECT queries are allowed."

    for keyword in BLOCKED_KEYWORDS:
        if keyword in {"--", ";"}:
            if keyword in cleaned_sql:
                return cleaned_sql, f"Query contains blocked token: {keyword}"
            continue

        if re.search(rf"\b{keyword}\b", cleaned_sql, flags=re.IGNORECASE):
            return cleaned_sql, f"Query contains blocked keyword: {keyword}"

    if not has_balanced_parentheses(cleaned_sql):
        return cleaned_sql, "Query has unbalanced parentheses."

    cleaned_sql = cleaned_sql.rstrip(";").strip()

    if not FROM_PATTERN.search(cleaned_sql):
        return cleaned_sql, "Query must read from an approved data table."

    if re.search(r"\b(with|union|intersect|except)\b", cleaned_sql, flags=re.IGNORECASE):
        return cleaned_sql, "Query contains an unsupported SQL pattern."

    referenced_tables = extract_data_sources(cleaned_sql)
    if not referenced_tables:
        return cleaned_sql, "Query must read from an approved data table."

    if allowed_tables is not None:
        unknown_tables = [table for table in referenced_tables if table not in allowed_tables]
        if unknown_tables:
            return cleaned_sql, f"Query references unsupported tables: {', '.join(unknown_tables)}"

    if not LIMIT_PATTERN.search(cleaned_sql):
        cleaned_sql = f"{cleaned_sql} LIMIT {max_rows}"

    return cleaned_sql, None

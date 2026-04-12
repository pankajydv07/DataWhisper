import json
from typing import Any

from backend.llm_client import call_groq

SQL_EXPLANATION_SYSTEM_PROMPT = """You are a data analyst assistant.
Explain SQL queries to business users in plain English.
Do not repeat the SQL.
Do not use technical jargon.
"""

SQL_EXPLANATION_USER_PROMPT = """Explain what this SQL query does in 1-2 sentences.
Be specific about tables, filters, joins, and aggregations.

SQL:
{generated_sql}

Explanation:"""

RESULT_SUMMARY_SYSTEM_PROMPT = """You are a data analyst.
Summarise query results for a business user.
Be concise, quantitative, and specific.
"""

RESULT_SUMMARY_USER_PROMPT = """Summarise the following query results in 2-3 sentences.
Highlight the most interesting number, trend, or outlier.

Original question:
{user_question}

Query results, first 10 rows:
{result_sample}

Summary:"""


async def explain_sql(generated_sql: str) -> str:
    return await call_groq(
        [
            {"role": "system", "content": SQL_EXPLANATION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": SQL_EXPLANATION_USER_PROMPT.format(
                    generated_sql=generated_sql
                ),
            },
        ],
        max_tokens=300,
    )


async def summarize_result(user_question: str, rows: list[dict[str, Any]]) -> str:
    result_sample = json.dumps(rows[:10], default=str, ensure_ascii=False)

    return await call_groq(
        [
            {"role": "system", "content": RESULT_SUMMARY_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": RESULT_SUMMARY_USER_PROMPT.format(
                    user_question=user_question,
                    result_sample=result_sample,
                ),
            },
        ],
        max_tokens=400,
    )


def append_trust_suffix(
    summary: str,
    *,
    data_sources: list[str],
    assumptions: list[str],
) -> str:
    fragments = [summary.strip()]
    if data_sources:
        fragments.append(f"Based on {', '.join(data_sources)}.")
    if assumptions:
        fragments.append("Assumptions: " + "; ".join(assumptions) + ".")
    return " ".join(fragment for fragment in fragments if fragment)

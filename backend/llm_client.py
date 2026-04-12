import os
from typing import Any

import httpx

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

NL_TO_SQL_SYSTEM_PROMPT = """You are a senior PostgreSQL analyst.
Your job is to translate natural language analytics questions into safe SQL SELECT queries.

Rules:
- Return ONLY SQL.
- Use ONLY SELECT queries.
- Never return markdown, backticks, comments, or explanations.
- Never use DROP, DELETE, UPDATE, INSERT, TRUNCATE, ALTER, CREATE, EXEC, EXECUTE, semicolons, or SQL comments.
- Do not add a LIMIT clause; the backend will add it.
- Use only tables and columns present in the semantic schema.
- Every table has a user_id column. Restrict data to the authenticated user_id exactly.
- Use PostgreSQL syntax.
- For revenue, use: SUM(order_items.quantity * products.unit_price * (1 - order_items.discount)).
- Prefer completed orders for revenue and sales unless the user asks for cancelled or pending orders.
"""

NL_TO_SQL_USER_PROMPT = """Semantic schema:
{semantic_layer_context}

Authenticated user_id:
{user_id}

Conversation history, last 3 turns:
{conversation_history}

User question:
{user_question}

SQL:"""

ERROR_CORRECTION_SYSTEM_PROMPT = """You fix PostgreSQL SELECT queries.
Return ONLY one corrected SQL SELECT query.
Do not include markdown, comments, explanation, or semicolons.
Do not use unsafe SQL keywords.
Ensure the query is scoped to the authenticated user_id.
"""

ERROR_CORRECTION_USER_PROMPT = """Semantic schema:
{semantic_layer_context}

Authenticated user_id:
{user_id}

Original user question:
{user_question}

Failed SQL:
{failed_sql}

Error:
{error_message}

Corrected SQL:"""


async def call_groq(messages: list[dict[str, str]], max_tokens: int = 1024) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    payload: dict[str, Any] = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"].strip()


async def generate_sql(
    *,
    question: str,
    user_id: str,
    semantic_layer_context: str,
    conversation_history: str,
    intent: str = "general",
    intent_instructions: str = "",
) -> str:
    user_prompt = NL_TO_SQL_USER_PROMPT.format(
        semantic_layer_context=semantic_layer_context,
        user_id=user_id,
        conversation_history=conversation_history,
        user_question=(
            f"Intent: {intent}\n"
            f"Additional guidance: {intent_instructions or 'None'}\n\n"
            f"{question}"
        ),
    )

    return await call_groq(
        [
            {"role": "system", "content": NL_TO_SQL_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    )


async def correct_sql(
    *,
    user_question: str,
    user_id: str,
    failed_sql: str,
    error_message: str,
    semantic_layer_context: str,
) -> str:
    user_prompt = ERROR_CORRECTION_USER_PROMPT.format(
        semantic_layer_context=semantic_layer_context,
        user_id=user_id,
        user_question=user_question,
        failed_sql=failed_sql,
        error_message=error_message,
    )

    return await call_groq(
        [
            {"role": "system", "content": ERROR_CORRECTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    )

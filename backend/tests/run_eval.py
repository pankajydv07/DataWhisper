import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.llm_client import generate_sql  # noqa: E402
from backend.semantic_layer import build_semantic_context, load_schema  # noqa: E402
from backend.sql_safety import validate_sql  # noqa: E402

QUESTIONS_PATH = Path(__file__).parent / "test_questions.json"
RESULTS_PATH = Path(__file__).parent / "eval_results.json"


def contains_expected_tables(sql: str, expected_tables: list[str]) -> bool:
    lowered_sql = sql.lower()
    return all(table.lower() in lowered_sql for table in expected_tables)


async def main() -> None:
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    semantic_context = build_semantic_context(load_schema())

    passed = 0
    results = []

    for item in questions:
        raw_sql = await generate_sql(
            question=item["question"],
            user_id="eval-user",
            semantic_layer_context=semantic_context,
            conversation_history="No prior turns.",
        )
        validated_sql, error = validate_sql(raw_sql)

        if item["should_succeed"]:
            ok = error is None and contains_expected_tables(
                validated_sql, item["expected_tables"]
            )
        else:
            ok = error is not None or item.get("expected_blocked", False)

        passed += int(ok)
        results.append(
            {
                "id": item["id"],
                "ok": ok,
                "raw_sql": raw_sql,
                "validated_sql": validated_sql,
                "error": error,
            }
        )

    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Passed {passed}/{len(questions)} eval checks")
    print(f"Wrote {RESULTS_PATH}")


if __name__ == "__main__":
    asyncio.run(main())

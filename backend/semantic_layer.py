from pathlib import Path
from typing import Any

import yaml

SCHEMA_PATH = Path(__file__).parent / "data" / "schema.yaml"


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_semantic_context(schema: dict[str, Any]) -> str:
    lines: list[str] = [
        f"Domain: {schema['domain']}",
        f"SQL dialect: {schema['dialect']}",
        f"Currency: {schema['currency']}",
        "",
        "Tables:",
    ]

    for table in schema["tables"]:
        lines.append(f"- {table['name']}: {table['description']}")
        for column in table["columns"]:
            lines.append(
                f"  - {table['name']}.{column['name']} "
                f"({column['type']}): {column['description']}"
            )

    lines.append("")
    lines.append("Relationships:")
    for relationship in schema["relationships"]:
        lines.append(f"- {relationship['from']} -> {relationship['to']}")

    lines.append("")
    lines.append("Business terms:")
    for term, mapping in schema["business_terms"].items():
        lines.append(f"- {term}: {mapping}")

    return "\n".join(lines)

from pathlib import Path
from typing import Any

import yaml

from backend.models import MetricDefinitionRef

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
    lines.append("Metrics:")
    for metric in schema.get("metrics", []):
        lines.append(
            f"- {metric['key']}: {metric['definition']} "
            f"(formula: {metric.get('formula', 'n/a')}; "
            f"sources: {', '.join(metric.get('source_tables', []))})"
        )

    lines.append("")
    lines.append("Business terms:")
    for term, mapping in schema["business_terms"].items():
        lines.append(f"- {term}: {mapping}")

    return "\n".join(lines)


def get_metric_definitions(schema: dict[str, Any]) -> list[MetricDefinitionRef]:
    metrics: list[MetricDefinitionRef] = []
    for metric in schema.get("metrics", []):
        metrics.append(
            MetricDefinitionRef(
                key=metric["key"],
                label=metric.get("label", metric["key"].replace("_", " ").title()),
                definition=metric["definition"],
                formula=metric.get("formula"),
                source_tables=metric.get("source_tables", []),
                default_time_grain=metric.get("default_time_grain"),
            )
        )
    return metrics


def get_allowed_tables(schema: dict[str, Any]) -> set[str]:
    return {table["name"] for table in schema.get("tables", [])}

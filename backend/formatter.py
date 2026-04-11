from typing import Any

import pandas as pd

from backend.models import ChartPayload, TablePayload


def dataframe_to_table(df: pd.DataFrame) -> TablePayload:
    safe_df = df.astype(object).where(pd.notnull(df), None)
    return TablePayload(
        columns=[str(column) for column in safe_df.columns],
        rows=safe_df.values.tolist(),
    )


def dataframe_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    safe_df = df.astype(object).where(pd.notnull(df), None)
    return safe_df.to_dict(orient="records")


def infer_chart(df: pd.DataFrame) -> ChartPayload | None:
    if df.empty or len(df.columns) < 2:
        return None

    numeric_columns = [
        column for column in df.columns if pd.api.types.is_numeric_dtype(df[column])
    ]
    if not numeric_columns:
        return None

    y_column = numeric_columns[0]
    x_candidates = [column for column in df.columns if column != y_column]
    if not x_candidates:
        return None

    x_column = x_candidates[0]
    x_name = str(x_column).lower()
    chart_type = "line" if "date" in x_name or "month" in x_name else "bar"

    return ChartPayload(type=chart_type, x=str(x_column), y=str(y_column))

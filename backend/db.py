import os

import psycopg
from psycopg.rows import dict_row

DEFAULT_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
DEFAULT_SSLMODE = os.getenv("DB_SSLMODE", "require")


def get_database_url() -> str:
    database_url = os.getenv("SUPABASE_DB_URL", "").strip()
    if not database_url:
        raise RuntimeError("SUPABASE_DB_URL is not configured.")
    return database_url


def connect(
    *,
    row_factory: object | None = None,
    connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
) -> psycopg.Connection:
    kwargs: dict[str, object] = {"connect_timeout": connect_timeout}

    if DEFAULT_SSLMODE:
        kwargs["sslmode"] = DEFAULT_SSLMODE
    if row_factory is not None:
        kwargs["row_factory"] = row_factory

    return psycopg.connect(get_database_url(), **kwargs)


def connect_dict(*, connect_timeout: int = DEFAULT_CONNECT_TIMEOUT) -> psycopg.Connection:
    return connect(row_factory=dict_row, connect_timeout=connect_timeout)

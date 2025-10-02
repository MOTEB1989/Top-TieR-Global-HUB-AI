"""PostgreSQL adapter example.

This module demonstrates how to create a connection using ``psycopg2``
and run a lightweight ``SELECT`` query.  The helper raises a clear error
message when the optional dependency is not installed so that the caller
can handle the failure gracefully.
"""
from __future__ import annotations

import os
from typing import Iterable, Tuple

try:
    import psycopg2
    from psycopg2.extensions import connection as PgConnection
except ImportError as exc:  # pragma: no cover - optional dependency
    psycopg2 = None
    PgConnection = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


DEFAULT_DSN = "dbname=postgres user=postgres password=postgres host=localhost port=5432"


def get_connection(dsn: str | None = None) -> PgConnection:
    """Return a PostgreSQL connection.

    Parameters
    ----------
    dsn:
        A PostgreSQL DSN string. If omitted, the function falls back to
        the ``DATABASE_URL`` environment variable and finally a sensible
        local default.
    """

    if psycopg2 is None:  # pragma: no cover - dependency optional
        raise RuntimeError(
            "psycopg2 is required for the PostgreSQL adapter. Install it with 'pip install psycopg2-binary'."
        ) from _IMPORT_ERROR

    final_dsn = dsn or os.getenv("DATABASE_URL") or DEFAULT_DSN
    return psycopg2.connect(final_dsn)


def simple_healthcheck(dsn: str | None = None) -> Iterable[Tuple[int]]:
    """Execute a ``SELECT 1`` query to validate connectivity."""

    with get_connection(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchall()


if __name__ == "__main__":  # pragma: no cover - demonstration script
    try:
        print(simple_healthcheck())
    except RuntimeError as error:
        print(error)

"""ClickHouse adapter example using ``clickhouse-driver``."""
from __future__ import annotations

import os
from typing import Iterable, Tuple

try:
    from clickhouse_driver import Client
except ImportError as exc:  # pragma: no cover - optional dependency
    Client = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


DEFAULT_SETTINGS = {
    "host": os.getenv("CLICKHOUSE_HOST", "localhost"),
    "port": int(os.getenv("CLICKHOUSE_PORT", "9000")),
    "user": os.getenv("CLICKHOUSE_USER", "default"),
    "password": os.getenv("CLICKHOUSE_PASSWORD", ""),
    "database": os.getenv("CLICKHOUSE_DB", "default"),
}


def query_version(**overrides) -> Iterable[Tuple[str]]:
    """Return the server version to validate connectivity."""

    if Client is None:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "clickhouse-driver is required for the ClickHouse adapter. Install it with 'pip install clickhouse-driver'."
        ) from _IMPORT_ERROR

    client = Client(**{**DEFAULT_SETTINGS, **overrides})
    try:
        return client.execute("SELECT version()")
    finally:
        client.disconnect()


if __name__ == "__main__":  # pragma: no cover - demo helper
    try:
        print(query_version())
    except RuntimeError as error:
        print(error)

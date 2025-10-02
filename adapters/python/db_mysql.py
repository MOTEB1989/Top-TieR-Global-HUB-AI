"""MySQL adapter example using ``mysql-connector-python``.

The helpers in this module demonstrate how to run a trivial query while
providing descriptive errors when the optional dependency is missing.
"""
from __future__ import annotations

import os
from typing import Iterable, Tuple

try:
    import mysql.connector
    from mysql.connector.connection import MySQLConnection
except ImportError as exc:  # pragma: no cover - optional dependency
    mysql = None
    MySQLConnection = None
    _IMPORT_ERROR = exc
else:
    mysql = mysql.connector
    _IMPORT_ERROR = None


DEFAULT_CONFIG = {
    "user": "root",
    "password": "root",
    "host": "127.0.0.1",
    "port": 3306,
    "database": os.getenv("MYSQL_DATABASE", "mysql"),
}


def get_connection(**overrides) -> MySQLConnection:
    """Create and return a MySQL connection."""

    if mysql is None:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "mysql-connector-python is required for the MySQL adapter. Install it with 'pip install mysql-connector-python'."
        ) from _IMPORT_ERROR

    config = {**DEFAULT_CONFIG, **overrides}
    return mysql.connect(**config)


def simple_healthcheck(**overrides) -> Iterable[Tuple[int]]:
    """Execute ``SELECT 1`` as a connectivity check."""

    with get_connection(**overrides) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        rows = cursor.fetchall()
        cursor.close()
    return rows


if __name__ == "__main__":  # pragma: no cover - demo helper
    try:
        print(simple_healthcheck())
    except RuntimeError as error:
        print(error)

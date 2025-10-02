"""SQLite adapter example for quick local testing.

This module provides a helper that initialises an in-memory database, 
creates a sample table, and returns both the connection and query result
so it can be used as a minimal smoke test when wiring the adapter into
pipelines or demos.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable, Tuple


def initialise_sqlite(db_path: str = ":memory:") -> Tuple[sqlite3.Connection, Iterable[Tuple[int, str]]]:
    """Initialise a SQLite database and run a sample query.

    Parameters
    ----------
    db_path:
        Path to the SQLite database. Defaults to an in-memory database so
        the example can run without touching the filesystem.

    Returns
    -------
    tuple
        A tuple containing the connection and an iterable of rows fetched
        from a demonstration query.
    """

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("DELETE FROM projects")
    cursor.executemany(
        "INSERT INTO projects (id, name) VALUES (?, ?)",
        [(1, "Vision API"), (2, "Security Toolkit"), (3, "Analytics Pipeline")],
    )

    cursor.execute("SELECT id, name FROM projects ORDER BY id")
    rows = cursor.fetchall()

    connection.commit()
    return connection, rows


if __name__ == "__main__":
    _, sample_rows = initialise_sqlite()
    for project_id, project_name in sample_rows:
        print(f"Project #{project_id}: {project_name}")

"""Neo4j adapter example using the official driver."""
from __future__ import annotations

import os
from typing import Iterable

try:
    from neo4j import GraphDatabase, basic_auth
except ImportError as exc:  # pragma: no cover - optional dependency
    GraphDatabase = None
    basic_auth = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


DEFAULT_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
DEFAULT_USER = os.getenv("NEO4J_USER", "neo4j")
DEFAULT_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")


def query_example(cypher: str = "MATCH (n) RETURN n LIMIT 5", *, uri: str | None = None) -> Iterable[dict]:
    """Run a simple Cypher query and yield the records."""

    if GraphDatabase is None:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "neo4j-driver is required for the Neo4j adapter. Install it with 'pip install neo4j'."
        ) from _IMPORT_ERROR

    driver = GraphDatabase.driver(uri or DEFAULT_URI, auth=basic_auth(DEFAULT_USER, DEFAULT_PASSWORD))
    try:
        with driver.session() as session:
            result = session.run(cypher)
            for record in result:
                yield record.data()
    finally:
        driver.close()


if __name__ == "__main__":  # pragma: no cover - demo helper
    try:
        for row in query_example():
            print(row)
    except RuntimeError as error:
        print(error)

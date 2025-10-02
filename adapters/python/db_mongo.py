"""MongoDB adapter example using ``pymongo``."""
from __future__ import annotations

import os
from typing import Iterable

try:
    from pymongo import MongoClient
except ImportError as exc:  # pragma: no cover - optional dependency
    MongoClient = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


DEFAULT_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")


def get_client(uri: str | None = None) -> MongoClient:
    """Return a :class:`~pymongo.mongo_client.MongoClient` instance."""

    if MongoClient is None:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "pymongo is required for the MongoDB adapter. Install it with 'pip install pymongo'."
        ) from _IMPORT_ERROR

    return MongoClient(uri or DEFAULT_URI)


def list_databases(uri: str | None = None) -> Iterable[str]:
    """Return the available database names to verify connectivity."""

    client = get_client(uri)
    try:
        yield from client.list_database_names()
    finally:
        client.close()


if __name__ == "__main__":  # pragma: no cover - demo helper
    try:
        for name in list_databases():
            print(name)
    except RuntimeError as error:
        print(error)

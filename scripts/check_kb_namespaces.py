"""Utility script to inspect knowledge base namespaces stored in ChromaDB."""

from __future__ import annotations

import argparse
from typing import Any, Iterable

import chromadb


def _format_namespaces(collections: Iterable[Any]) -> str:
    names = [getattr(collection, "name", str(collection)) for collection in collections]
    if not names:
        return "No namespaces found in the knowledge base store."
    lines = ["Detected namespaces:"]
    lines.extend(f"- {name}" for name in sorted(names))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List namespaces that exist in the local knowledge base store.",
    )
    parser.add_argument(
        "--store-path",
        default=".kb_store",
        help="Filesystem path where the ChromaDB persistent store is located.",
    )
    args = parser.parse_args()

    client = chromadb.PersistentClient(path=args.store_path)
    collections = client.list_collections()
    print(_format_namespaces(collections))


if __name__ == "__main__":
    main()

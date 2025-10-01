#!/usr/bin/env python3
"""Ingest repository files into a Weaviate collection."""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import Iterable

import weaviate
from sentence_transformers import SentenceTransformer
from weaviate.exceptions import WeaviateBaseError

SUPPORTED_SUFFIXES = (".py", ".md", ".yml", ".yaml")
IGNORED_DIRECTORIES = {".git", "__pycache__", "node_modules", "venv", ".venv", "dist", "build"}
DEFAULT_CLASS_NAME = "RepoFile"


logger = logging.getLogger(__name__)


def walk_repository(root: Path, suffixes: Iterable[str]) -> Iterable[Path]:
    """Yield files within ``root`` that match the provided suffixes."""
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRECTORIES]
        for filename in filenames:
            path = Path(current_root, filename)
            if path.suffix.lower() in suffixes:
                yield path


def ensure_class_exists(client: weaviate.Client, class_name: str) -> None:
    """Create the collection if it is missing and configured for manual vectors."""
    try:
        schema = client.schema.get()
    except WeaviateBaseError as err:  # pragma: no cover - network failure
        raise SystemExit(f"Unable to retrieve schema from Weaviate: {err}") from err

    classes = {c.get("class") for c in schema.get("classes", [])}
    if class_name in classes:
        return

    definition = {
        "class": class_name,
        "vectorizer": "none",
        "properties": [
            {"name": "path", "dataType": ["text"], "description": "Repository-relative file path."},
            {"name": "content", "dataType": ["text"], "description": "Full contents of the file."},
        ],
    }

    try:
        client.schema.create_class(definition)
        logger.info("Created Weaviate class %s", class_name)
    except WeaviateBaseError as err:  # pragma: no cover - network failure
        raise SystemExit(f"Failed to create class '{class_name}' in Weaviate: {err}") from err


def embed_files(
    client: weaviate.Client,
    model: SentenceTransformer,
    class_name: str,
    files: Iterable[Path],
    root: Path,
    batch_size: int,
    dry_run: bool,
) -> None:
    total = 0
    with client.batch as batch:
        batch.batch_size = batch_size
        for path in files:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError as err:  # pragma: no cover - depends on environment
                logger.warning("Skipping %s: %s", path, err)
                continue

            if not text.strip():
                logger.debug("Skipping empty file %s", path)
                continue

            vector = model.encode([text])[0].tolist()
            data_object = {
                "path": str(path.relative_to(root)),
                "content": text,
            }

            total += 1
            if dry_run:
                logger.info("[dry-run] Would upload %s", data_object["path"])
                continue

            batch.add_data_object(data_object=data_object, class_name=class_name, vector=vector)
            logger.debug("Queued %s", data_object["path"])

    logger.info("Processed %s files", total)



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        default="http://localhost:8080",
        help="Weaviate host URL (default: %(default)s)",
    )
    parser.add_argument(
        "--class-name",
        default=DEFAULT_CLASS_NAME,
        help="Weaviate class name to upsert (default: %(default)s)",
    )
    parser.add_argument(
        "--model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="SentenceTransformers model to load (default: %(default)s)",
    )
    parser.add_argument(
        "--root",
        default=Path.cwd(),
        type=Path,
        help="Repository root to scan (default: current working directory)",
    )
    parser.add_argument(
        "--suffixes",
        nargs="*",
        default=SUPPORTED_SUFFIXES,
        help="File suffixes to ingest (default: %(default)s)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Weaviate batch size (default: %(default)s)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log the files that would be uploaded without sending them to Weaviate",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: %(default)s)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")

    root = args.root.resolve()
    suffixes = tuple(s if s.startswith(".") else f".{s}" for s in args.suffixes)

    logger.info("Connecting to Weaviate at %s", args.host)
    try:
        client = weaviate.Client(args.host)
    except WeaviateBaseError as err:  # pragma: no cover - network failure
        raise SystemExit(f"Failed to connect to Weaviate at {args.host}: {err}") from err

    ensure_class_exists(client, args.class_name)

    logger.info("Loading model %s", args.model)
    model = SentenceTransformer(args.model)

    files = walk_repository(root, suffixes)
    embed_files(client, model, args.class_name, files, root, args.batch_size, args.dry_run)


if __name__ == "__main__":
    main()

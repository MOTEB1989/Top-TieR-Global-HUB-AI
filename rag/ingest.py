import argparse
from pathlib import Path
from typing import List

from .config import CHUNK_SIZE, CHUNK_OVERLAP, DB_PATH
from .embed import get_embedding
from .store import add_chunk, init_db


def chunk_text(text: str, size: int, overlap: int) -> List[str]:
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + size, length)
        chunks.append(text[start:end])
        if end == length:
            break
        start = end - overlap
    return chunks


def ingest_path(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    for idx, chunk in enumerate(chunks):
        emb = get_embedding(chunk)
        add_chunk(str(path), idx, chunk, emb)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest .txt/.md documents into local RAG store.")
    parser.add_argument("root", type=str, help="Root directory containing documents.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    init_db(DB_PATH)

    for path in root.rglob("*"):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        print(f"[INGEST] {path}")
        ingest_path(path)


if __name__ == "__main__":
    main()

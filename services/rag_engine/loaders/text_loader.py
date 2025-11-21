from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Iterator, List

from ..config import DocChunk, get_settings


def _iter_text_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*"):
        if path.suffix.lower() in {".txt", ".md"} and path.is_file():
            yield path


def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += max(chunk_size - overlap, 1)
    return [c for c in chunks if c.strip()]


def load_text_files(root: Path) -> Iterable[DocChunk]:
    """Load text and markdown files under ``root`` as chunks.

    This function is intentionally IO-bound and should not be used in CI; tests
    should mock it.
    """

    settings = get_settings()
    chunk_size = int(settings["RAG_CHUNK_SIZE"])
    overlap = int(settings["RAG_CHUNK_OVERLAP"])

    for path in _iter_text_files(root):
        content = path.read_text(encoding="utf-8", errors="ignore")
        chunks = _chunk_text(content, chunk_size, overlap)
        for idx, chunk in enumerate(chunks):
            yield DocChunk(
                path=str(path),
                chunk_index=idx,
                content=chunk,
                metadata={
                    "source": os.path.relpath(path, root),
                    "type": "text",
                },
            )


__all__ = ["load_text_files"]

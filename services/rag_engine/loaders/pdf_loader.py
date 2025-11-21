from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Iterator, List

from ..config import DocChunk, get_settings


class PDFValidationError(RuntimeError):
    pass


def _validate_pdf(path: Path, max_mb: int) -> None:
    if path.suffix.lower() != ".pdf":
        raise PDFValidationError(f"Unsupported file extension for {path}")
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_mb:
        raise PDFValidationError(
            f"{path} is too large ({size_mb:.2f}MB). Max allowed: {max_mb}MB"
        )
    sanitized = path.name
    if ".." in sanitized or sanitized.startswith("/"):
        raise PDFValidationError("Unsafe PDF filename detected")


def _iter_pdfs(root: Path) -> Iterator[Path]:
    for path in root.rglob("*.pdf"):
        if path.is_file():
            yield path


def _chunk_page_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += max(chunk_size - overlap, 1)
    return [c for c in chunks if c.strip()]


def load_pdf_files(root: Path) -> Iterable[DocChunk]:
    settings = get_settings()
    chunk_size = int(settings["RAG_CHUNK_SIZE"])
    overlap = int(settings["RAG_CHUNK_OVERLAP"])
    max_mb = int(settings["RAG_MAX_PDF_MB"])

    for path in _iter_pdfs(root):
        _validate_pdf(path, max_mb)
        try:
            import fitz  # PyMuPDF
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "PyMuPDF (fitz) is required for PDF ingestion. Install via PyMuPDF."
            ) from exc

        doc = fitz.open(path)
        page_count = len(doc)
        for page_index in range(page_count):
            page = doc.load_page(page_index)
            text = page.get_text()
            for chunk_idx, chunk in enumerate(_chunk_page_text(text, chunk_size, overlap)):
                metadata = {
                    "title": os.path.basename(path),
                    "source": os.path.relpath(path, root),
                    "page_number": str(page_index + 1),
                    "page_count": str(page_count),
                    "type": "pdf",
                }
                yield DocChunk(
                    path=str(path),
                    chunk_index=chunk_idx,
                    content=chunk,
                    metadata=metadata,
                )


__all__ = ["load_pdf_files", "PDFValidationError"]

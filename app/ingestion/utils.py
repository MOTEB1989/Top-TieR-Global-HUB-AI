"""Utility helpers shared across ingestion sources."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
from typing import Dict

try:  # pragma: no cover - optional dependency guard
    import fitz  # type: ignore
except ImportError as exc:  # pragma: no cover - handled lazily
    fitz = None  # type: ignore
    _FITZ_IMPORT_ERROR = exc
else:
    _FITZ_IMPORT_ERROR = None


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def sha1_bytes(payload: bytes) -> str:
    return hashlib.sha1(payload).hexdigest()


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def slugify(title: str) -> str:
    safe = re.sub(r"[\\/:*?\"<>|]+", "_", title.strip())
    safe = re.sub(r"\s+", "_", safe)
    return safe[:150]


def pdf_to_text(pdf_path: str) -> str:
    if fitz is None:  # pragma: no cover - executed only when dependency missing
        raise ImportError("PyMuPDF is required for PDF parsing") from _FITZ_IMPORT_ERROR

    parts = []
    with fitz.open(pdf_path) as doc:  # type: ignore[attr-defined]
        for page in doc:
            parts.append(page.get_text("text"))
    text = "\n".join(parts).strip()
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def save_json(path: str, data: Dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)

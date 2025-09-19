"""Utility functions for logging GPT request traces."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

TRACE_FILE = Path("logs/ai_trace.jsonl")


def log_trace(user: str, query: str, source: dict[str, Any] | None = None, model: str = "gpt-5-mini") -> None:
    """Append a trace record to ``logs/ai_trace.jsonl``.

    Args:
        user: Identifier of the caller (username, service name, etc.).
        query: The input text sent to GPT.
        source: Optional information about the data source (e.g. ``{"type": "repo", "path": "file.py"}``).
        model: Model name used for the request.
    """
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "user": user,
        "query": query,
        "source": source or {},
        "model": model,
    }

    TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with TRACE_FILE.open("a", encoding="utf-8") as trace_file:
        trace_file.write(json.dumps(record, ensure_ascii=False) + "\n")

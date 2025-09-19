"""Registry of available ingestion sources."""

from __future__ import annotations

from typing import Dict, Type

from app.ingestion.base import BaseIngestor
from app.ingestion.sources.sama import SamaIngestor

REGISTRY: Dict[str, Type[BaseIngestor]] = {
    "sama": SamaIngestor,
    # Future sources can be registered here, e.g. "committees": CommitteesIngestor,
}


def get_ingestor(name: str) -> BaseIngestor:
    try:
        ingestor_cls = REGISTRY[name]
    except KeyError as exc:  # pragma: no cover - sanity guard
        raise ValueError(f"Unknown ingestion source: {name}") from exc
    return ingestor_cls()

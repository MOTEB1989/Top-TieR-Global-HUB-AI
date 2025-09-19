"""Base classes for ingestion sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseIngestor(ABC):
    """Abstract base class for ingestion pipelines."""

    name: str = "base"

    @abstractmethod
    def discover(self) -> List[Dict]:
        """Return a list of discovery items (title, url, metadata)."""
        raise NotImplementedError

    @abstractmethod
    def fetch_and_parse(self, item: Dict) -> Dict:
        """Fetch a single discovery item and convert it to a structured record."""
        raise NotImplementedError

    def run(self, limit: Optional[int] = None) -> List[Dict]:
        """Execute the ingestion pipeline for the configured source."""

        items = self.discover()
        if limit is not None:
            items = items[:limit]
        results: List[Dict] = []
        for candidate in items:
            try:
                record = self.fetch_and_parse(candidate)
                if record:
                    results.append(record)
            except Exception as exc:  # pragma: no cover - defensive logging
                print(f"[{self.name}] خطأ في {candidate.get('url')}: {exc}")
        return results

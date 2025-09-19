"""Ingestor for Saudi Arabian Monetary Authority circulars."""

from __future__ import annotations

import os
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests

try:  # pragma: no cover - optional dependency guard
    from bs4 import BeautifulSoup
except ImportError as exc:  # pragma: no cover - handled lazily
    BeautifulSoup = None  # type: ignore
    _BS4_IMPORT_ERROR = exc
else:
    _BS4_IMPORT_ERROR = None

from app.ingestion.base import BaseIngestor
from app.ingestion.utils import (
    ensure_dir,
    now_iso,
    pdf_to_text,
    save_json,
    sha1_bytes,
    sha1_text,
    slugify,
)

BASE_URL = "https://www.sama.gov.sa"
CIRCULARS_URL = os.getenv(
    "SAMA_CIRCULARS_URL",
    "https://www.sama.gov.sa/ar-sa/RulesInstructions/Pages/Circulars.aspx",
)
OUT_DIR = os.getenv("SAMA_OUT_DIR", "data/sama_regulations")
HEADERS = {"User-Agent": "MotebAI-Ingestor/1.0"}


class SamaIngestor(BaseIngestor):
    """Ingestor responsible for SAMA circular documents."""

    name = "sama"

    def discover(self) -> List[Dict]:
        if BeautifulSoup is None:  # pragma: no cover - executed only when dependency missing
            raise ImportError("beautifulsoup4 is required for discovery") from _BS4_IMPORT_ERROR

        response = requests.get(CIRCULARS_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        found: List[Dict] = []
        for anchor in soup.select("a"):
            href = (anchor.get("href") or "").strip()
            title = anchor.get_text(strip=True)
            if not href or not title:
                continue
            if href.lower().endswith(".pdf") or "تعميم" in title or "Circular" in title:
                url = urljoin(BASE_URL, href)
                found.append({"title": title, "url": url})

        unique: List[Dict] = []
        seen: set[str] = set()
        for candidate in found:
            if candidate["url"] in seen:
                continue
            seen.add(candidate["url"])
            unique.append(candidate)
        return unique

    def _download_pdf(
        self, session: requests.Session, url: str, pdf_path: str
    ) -> Optional[bytes]:
        response = session.get(url, headers=HEADERS, timeout=60, stream=True)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()
        if "pdf" in content_type or url.lower().endswith(".pdf"):
            payload = response.content
            with open(pdf_path, "wb") as handle:
                handle.write(payload)
            return payload
        return None

    def fetch_and_parse(self, item: Dict) -> Dict:
        ensure_dir(OUT_DIR)
        base_name = slugify(item["title"]) or sha1_text(item["url"])
        pdf_path = os.path.join(OUT_DIR, f"{base_name}.pdf")
        json_path = os.path.join(OUT_DIR, f"{base_name}.json")

        with requests.Session() as session:
            if not os.path.exists(pdf_path):
                content = self._download_pdf(session, item["url"], pdf_path)
                if content is None:
                    raise RuntimeError("ليس PDF")
                pdf_sha1 = sha1_bytes(content)
            else:
                with open(pdf_path, "rb") as source:
                    pdf_sha1 = sha1_bytes(source.read())

        text = pdf_to_text(pdf_path)
        record = {
            "doc_id": sha1_text(item["url"]),
            "title": item["title"],
            "source_url": item["url"],
            "source_type": "pdf",
            "language": "ar",
            "ingested_at": now_iso(),
            "pdf_sha1": pdf_sha1,
            "text_sha1": sha1_text(text),
            "content": text,
            "regulatory_guess": {"jurisdiction": "KSA", "regulator": "SAMA"},
        }
        save_json(json_path, record)
        return record

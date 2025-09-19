"""Command-line entry point for ingestion workflows."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List, Optional

from app.ingestion.registry import REGISTRY, get_ingestor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified ingestion runner")
    parser.add_argument("--source", choices=REGISTRY.keys(), default="sama")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--index-jsonl",
        default=os.getenv(
            "CIRCULARS_INDEX",
            "data/sama_regulations/sama_circulars.index.jsonl",
        ),
        help="Path to the JSONL index file",
    )
    return parser


def run_ingestion(
    source: str, limit: Optional[int] = None, index_jsonl: Optional[str] = None
) -> Dict[str, Any]:
    if index_jsonl is None:
        index_jsonl = os.getenv(
            "CIRCULARS_INDEX",
            "data/sama_regulations/sama_circulars.index.jsonl",
        )

    ingestor = get_ingestor(source)
    records = ingestor.run(limit=limit)

    directory = os.path.dirname(index_jsonl)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(index_jsonl, "a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "source": ingestor.name,
        "count": len(records),
        "index_path": index_jsonl,
        "records": records,
    }


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = run_ingestion(args.source, args.limit, args.index_jsonl)
    print(
        f"[{result['source']}] تم حفظ {result['count']} سجل/سجلات في {result['index_path']}"
    )


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()

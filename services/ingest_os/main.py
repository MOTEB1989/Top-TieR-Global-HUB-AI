from __future__ import annotations

import glob
import json
from pathlib import Path

from opensearchpy import OpenSearch


def load_documents(pattern: str) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    for path in glob.glob(pattern, recursive=True):
        file_path = Path(path)
        if not file_path.is_file():
            continue
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        documents.append({"path": str(file_path), "text": text})
    return documents


def main() -> None:
    client = OpenSearch(hosts=[{"host": "opensearch", "port": 9200}], http_compress=True)
    index = "lexcode_kb"
    client.indices.create(index=index, ignore=400)

    docs = load_documents("**/*.md")
    for doc in docs:
        client.index(index=index, body=doc)

    print(json.dumps({"indexed": len(docs)}))


if __name__ == "__main__":
    main()

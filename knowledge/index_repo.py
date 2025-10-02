from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def iter_markdown_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        if path.is_file():
            yield path


def build_index(repo_root: Path, kb_path: Path) -> dict[str, int]:
    kb_path.mkdir(parents=True, exist_ok=True)
    count = 0
    for md_file in iter_markdown_files(repo_root):
        target = kb_path / md_file.name
        target.write_text(md_file.read_text(encoding="utf-8"), encoding="utf-8")
        count += 1
    return {"documents": count}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", help="Repository root to index")
    parser.add_argument("--kb-path", default=".kb_store", help="Destination for KB artifacts")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    kb_path = Path(args.kb_path).resolve()

    stats = build_index(repo_root, kb_path)
    print(json.dumps(stats))


if __name__ == "__main__":
    main()

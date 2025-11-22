import argparse
import hashlib
import json
import os
from typing import Iterable, List


def file_hash(path: str) -> str:
    """Calculate the SHA-256 hash for a file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def scan_repository(root: str, excludes: Iterable[str]) -> List[dict]:
    """Walk the repository and collect file metadata."""
    repo_data = []
    for current_root, dirs, files in os.walk(root, topdown=True):
        dirs[:] = [d for d in dirs if d not in excludes]
        for file_name in files:
            full_path = os.path.join(current_root, file_name)
            try:
                size = os.path.getsize(full_path)
                sha = file_hash(full_path)
                repo_data.append(
                    {
                        "path": full_path,
                        "size_bytes": size,
                        "sha256": sha,
                    }
                )
            except Exception as exc:  # pylint: disable=broad-except
                repo_data.append({"path": full_path, "error": str(exc)})
    return repo_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Scan the repository and create a JSON file with file paths, sizes, "
            "and SHA-256 hashes."
        )
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to scan (default: current working directory)",
    )
    parser.add_argument(
        "--output",
        default="repo_structure.json",
        help="Output JSON file path (default: repo_structure.json)",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[".git", "__pycache__", "node_modules", "dist", "target"],
        help="Directories to exclude from scanning",
    )
    args = parser.parse_args()

    repo_data = scan_repository(args.root, set(args.exclude))
    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(repo_data, file, indent=2)

    print(f"Scan complete. Output saved to {args.output}")


if __name__ == "__main__":
    main()

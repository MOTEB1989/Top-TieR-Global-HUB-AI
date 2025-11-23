import argparse
import datetime as dt
import json
import os
import subprocess
from collections import Counter
from typing import Dict, Iterable, List, Optional


EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    ".idea",
    ".vscode",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ultra Agent OS - lightweight repo scanner")
    parser.add_argument(
        "--mode",
        choices=["full-scan"],
        default="full-scan",
        help="Scan mode (currently only full-scan is supported).",
    )
    parser.add_argument("--out-json", required=True, help="Path to write JSON report")
    parser.add_argument("--out-md", required=True, help="Path to write Markdown report")
    return parser.parse_args()


def get_git_metadata() -> Dict[str, Optional[str]]:
    def _run(cmd: List[str]) -> Optional[str]:
        try:
            completed = subprocess.run(
                cmd, check=True, capture_output=True, text=True
            )
            return completed.stdout.strip() or None
        except subprocess.CalledProcessError:
            return None

    return {
        "branch": _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "commit": _run(["git", "rev-parse", "HEAD"]),
        "status": _run(["git", "status", "--short"]),
    }


def walk_repository(root: str) -> Iterable[str]:
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file_name in files:
            yield os.path.relpath(os.path.join(current, file_name), root)


def collect_file_metadata(root: str, limit: int = 200):
    files: List[str] = []
    counter: Counter = Counter()
    total_files = 0
    total_dirs = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        total_dirs += 1
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(dirpath, filename), root)
            total_files += 1
            extension = os.path.splitext(filename)[1].lower() or "<none>"
            counter[extension] += 1
            if len(files) < limit:
                try:
                    size = os.path.getsize(os.path.join(dirpath, filename))
                except OSError:
                    size = None
                files.append({
                    "path": rel_path,
                    "size_bytes": size,
                })

    return {
        "samples": files,
        "total_files": total_files,
        "total_dirs": total_dirs,
        "by_extension": counter,
    }


def detect_issues(root: str, git_meta: Dict[str, Optional[str]]):
    issues = []

    def add_issue(message: str, file: Optional[str] = None, severity: str = "info"):
        issues.append({"message": message, "file": file, "severity": severity})

    readme_path = os.path.join(root, "README.md")
    if not os.path.exists(readme_path):
        add_issue("README.md is missing", file="README.md", severity="warning")

    if git_meta.get("status"):
        add_issue(
            "Repository has uncommitted changes",
            file=None,
            severity="warning",
        )

    reports_dir = os.path.join(root, "reports")
    if not os.path.exists(reports_dir):
        add_issue("reports/ directory does not exist (will be created when running scans)", file="reports", severity="info")

    return issues


def build_report(root: str) -> Dict[str, object]:
    git_meta = get_git_metadata()
    file_meta = collect_file_metadata(root)
    issues = detect_issues(root, git_meta)

    return {
        "mode": "full-scan",
        "root": os.path.abspath(root),
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "git": git_meta,
        "stats": {
            "total_files": file_meta["total_files"],
            "total_dirs": file_meta["total_dirs"],
            "by_extension": file_meta["by_extension"],
        },
        "issues": issues,
        "files": file_meta["samples"],
    }


def write_json(report: Dict[str, object], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(report, fp, indent=2, default=str)


def write_markdown(report: Dict[str, object], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = []
    lines.append("# Ultra Agent OS Report")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Mode: {report['mode']}")
    lines.append("")

    git_meta = report.get("git", {})
    lines.append("## Git")
    lines.append(f"- Branch: {git_meta.get('branch') or 'unknown'}")
    lines.append(f"- Commit: {git_meta.get('commit') or 'unknown'}")
    status = git_meta.get("status") or "clean"
    lines.append(f"- Status: {status if status != 'clean' else 'clean'}")
    lines.append("")

    stats = report.get("stats", {})
    lines.append("## Repository Stats")
    lines.append(f"- Total files: {stats.get('total_files', 0)}")
    lines.append(f"- Total directories: {stats.get('total_dirs', 0)}")
    lines.append("- Files by extension:")
    by_ext = stats.get("by_extension", {})
    for ext, count in sorted(by_ext.items(), key=lambda item: item[0]):
        lines.append(f"  - {ext}: {count}")
    lines.append("")

    lines.append("## Issues")
    issues = report.get("issues", [])
    if not issues:
        lines.append("- No issues detected.")
    else:
        for issue in issues:
            location = f" ({issue['file']})" if issue.get("file") else ""
            severity = issue.get("severity", "info")
            lines.append(f"- [{severity.upper()}] {issue['message']}{location}")
    lines.append("")

    lines.append("## File samples")
    samples = report.get("files", [])
    if samples:
        for sample in samples:
            size = sample.get("size_bytes")
            size_text = f"{size} bytes" if size is not None else "unknown size"
            lines.append(f"- {sample['path']} ({size_text})")
    else:
        lines.append("- No files sampled.")

    with open(path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines))


def main():
    args = parse_args()
    report = build_report(root=".")
    write_json(report, args.out_json)
    write_markdown(report, args.out_md)
    print(f"Report written to {args.out_json} and {args.out_md}")


if __name__ == "__main__":
    main()

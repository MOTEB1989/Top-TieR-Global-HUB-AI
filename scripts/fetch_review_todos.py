#!/usr/bin/env python3
from __future__ import annotations

import os
import pathlib
import sys
from typing import Iterable, Set

import requests

OWNER = "MOTEB1989"
REPO = "Top-TieR-Global-HUB-AI"
GITHUB_TOKEN = os.getenv("LEXCODE_GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("\u274c Error: Please set LEXCODE_GITHUB_TOKEN in environment.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


def get_ignored_reviewers() -> Set[str]:
    """Return a set of reviewers to ignore based on env configuration."""
    ignored = os.getenv("LEXCODE_IGNORE_REVIEWERS", "").strip()
    if not ignored:
        return set()
    return {name.strip().lower() for name in ignored.split(",") if name.strip()}


def fetch_review_comments(pr_number: int) -> Iterable[dict]:
    """Fetch review comments for a given PR."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{pr_number}/comments"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def build_todo(pr_number: int, comments: Iterable[dict]) -> tuple[str, bool]:
    """Build the markdown TODO list from review comments.

    Returns a tuple of the markdown content and a flag indicating whether any
    actionable TODO items were found.
    """
    header = f"# \u2705 TODOs from PR #{pr_number}\n"
    todo_entries = []
    ignored_reviewers = get_ignored_reviewers()
    for comment in comments:
        user = comment["user"]["login"]
        if user.lower() in ignored_reviewers:
            continue
        path = comment["path"]
        body = (comment.get("body") or "").strip()
        if not body:
            continue
        url = comment["html_url"]
        todo_entries.append(f"- [{user}] **{path}** \u2192 {body}  \n  \ud83d\udd17 {url}\n")

    has_todos = bool(todo_entries)
    if not has_todos:
        todo_entries.append("_No actionable review comments found._\n")

    return "\n".join([header, *todo_entries]), has_todos


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: fetch_review_todos.py <PR_NUMBER>")
        sys.exit(1)

    try:
        pr_number = int(sys.argv[1])
    except ValueError as exc:
        print(f"\u274c Error: invalid PR number '{sys.argv[1]}': {exc}")
        sys.exit(1)

    comments = fetch_review_comments(pr_number)

    if not comments:
        print(f"\u2139\ufe0f No review comments found for PR #{pr_number}")
        return

    todo_md, has_todos = build_todo(pr_number, comments)
    pathlib.Path("ops").mkdir(exist_ok=True)
    outfile = pathlib.Path(f"ops/todo_from_reviews_pr{pr_number}.md")
    outfile.write_text(todo_md, encoding="utf-8")

    print(f"\u2705 TODO file generated: {outfile}")
    print(todo_md)
    if not has_todos:
        print("\u2139\ufe0f No actionable review comments after filtering.")


if __name__ == "__main__":
    main()

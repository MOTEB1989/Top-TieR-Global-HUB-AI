#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collect AI Bot Feedback from GitHub issues/comments.

- Scans recent issues and PR comments looking for:
  - label: ai-feedback
  - or lines containing markers like [AI] or [BOT]
- Aggregates findings into docs/AI_BOT_FEEDBACK.md.
- Prints a short summary to stdout.

Requires:
- GITHUB_TOKEN
- GITHUB_REPOSITORY (owner/repo), usually auto-set in GitHub Actions.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests

GITHUB_API = "https://api.github.com"
OUTPUT_PATH = Path("docs/AI_BOT_FEEDBACK.md")


def gh_get(url: str, token: str) -> Any:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()


def collect_feedback() -> List[Dict[str, Any]]:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not token or not repo:
        print("GITHUB_TOKEN or GITHUB_REPOSITORY missing; cannot collect feedback.")
        return []

    owner, name = repo.split("/", 1)
    base_url = f"{GITHUB_API}/repos/{owner}/{name}"

    issues = gh_get(base_url + "/issues?state=all&per_page=50", token)
    feedback_items: List[Dict[str, Any]] = []

    for issue in issues:
        labels = [lbl["name"] for lbl in issue.get("labels", [])]
        is_feedback_label = "ai-feedback" in labels or "AI-feedback" in labels
        body: str = issue.get("body") or ""
        body_lower = body.lower()

        has_marker = "[ai]" in body_lower or "[bot]" in body_lower

        if is_feedback_label or has_marker:
            feedback_items.append(
                {
                    "type": "issue",
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "url": issue.get("html_url"),
                    "body": body,
                }
            )

    return feedback_items


def write_markdown(feedback_items: List[Dict[str, Any]]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# 🤖 AI Bot Feedback Log\n")
    lines.append(f"_Last updated: {datetime.utcnow().isoformat()}Z_\n")

    if not feedback_items:
        lines.append("\nNo AI feedback items found (issues with label `ai-feedback` or markers [AI]/[BOT]).\n")
    else:
        for item in feedback_items:
            lines.append(f"## Issue #{item['number']}: {item['title']}\n")
            lines.append(f"- Link: {item['url']}\n")
            lines.append("```markdown")
            lines.append((item["body"] or "").strip())
            lines.append("```")
            lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(feedback_items)} feedback items to {OUTPUT_PATH}")


def main() -> None:
    items = collect_feedback()
    write_markdown(items)


if __name__ == "__main__":
    main()


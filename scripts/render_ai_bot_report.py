#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Render a human-readable AI bot feedback report in Markdown."""

import json
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "ai_bot_feedback"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_feedback(json_path: Path) -> dict[str, Any]:
    if not json_path.exists():
        raise FileNotFoundError(f"Feedback file not found: {json_path}")
    return json.loads(json_path.read_text())


def render_report(data: dict[str, Any]) -> str:
    owner = data.get("owner", "?")
    repo = data.get("repo", "?")
    pr_number = data.get("pr_number", "?")
    total_comments = data.get("total_comments", 0)
    bot_comments = data.get("bot_comments", 0)
    bots = data.get("bots", [])

    lines: list[str] = []
    lines.append(f"# AI Bot Feedback Report for {owner}/{repo} PR #{pr_number}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total comments scanned: **{total_comments}**")
    lines.append(f"- Bot-authored comments: **{bot_comments}**")
    lines.append("")

    lines.append("## Bot Comments")
    if not bots:
        lines.append("No bot comments were detected for this pull request.")
        return "\n".join(lines).strip() + "\n"

    for idx, comment in enumerate(bots, start=1):
        user = comment.get("user", "unknown")
        created_at = comment.get("created_at", "?")
        url = comment.get("url", "")
        body = comment.get("body", "").strip()

        lines.append(f"### {idx}. {user} — {created_at}")
        if url:
            lines.append(f"[View comment]({url})")
        lines.append("")
        if body:
            lines.append("> " + "\n> ".join(body.splitlines()))
        else:
            lines.append("> (No body provided)")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def write_report(markdown: str, pr_number: str) -> Path:
    output_path = OUTPUT_DIR / f"bot_feedback_pr_{pr_number}.md"
    output_path.write_text(markdown)
    return output_path


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python render_ai_bot_report.py <feedback_json_path>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    data = load_feedback(json_path)
    markdown = render_report(data)
    output_path = write_report(markdown, str(data.get("pr_number", "unknown")))
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()

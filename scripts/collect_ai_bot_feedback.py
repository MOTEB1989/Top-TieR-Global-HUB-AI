#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collect AI Bot Feedback Script
--------------------------------
This script collects PR feedback from:
- GitHub Bots (actions, dependabot, code-scanners)
- Copilot comments
- Any bot comments detected by the GitHub API

Output:
  ai_bot_feedback/bot_feedback_pr_<PR>.json
Requires:
  - GitHub Token (env: GITHUB_TOKEN)
"""

import os
import json
import sys
from pathlib import Path
import requests

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "ai_bot_feedback"
OUTPUT_DIR.mkdir(exist_ok=True)

GITHUB_API = "https://api.github.com"


def get_github_token():
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        raise RuntimeError("GitHub token missing. Set GITHUB_TOKEN or GH_TOKEN.")
    return token


def get_pr_comments(owner, repo, pr_number):
    """Return all PR comments from GitHub API."""
    token = get_github_token()
    headers = {"Authorization": f"Bearer {token}"}

    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()


def detect_bot(comment):
    """Return True if commenter looks like a bot."""
    user = comment.get("user", {})
    login = user.get("login", "").lower()

    bot_keywords = [
        "bot",
        "github-actions",
        "dependabot",
        "codecov",
        "codeql",
        "renovate",
        "copilot",
    ]

    return any(key in login for key in bot_keywords)


def collect_feedback(owner, repo, pr_number):
    comments = get_pr_comments(owner, repo, pr_number)
    bot_comments = [c for c in comments if detect_bot(c)]

    result = {
        "owner": owner,
        "repo": repo,
        "pr_number": pr_number,
        "total_comments": len(comments),
        "bot_comments": len(bot_comments),
        "bots": [],
    }

    for c in bot_comments:
        result["bots"].append(
            {
                "user": c["user"]["login"],
                "created_at": c["created_at"],
                "body": c["body"],
                "url": c["html_url"],
            }
        )

    output_path = OUTPUT_DIR / f"bot_feedback_pr_{pr_number}.json"
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return output_path


def main():
    if len(sys.argv) != 4:
        print("Usage: python collect_ai_bot_feedback.py <owner> <repo> <pr_number>")
        sys.exit(1)

    owner = sys.argv[1]
    repo = sys.argv[2]
    pr_number = sys.argv[3]

    out = collect_feedback(owner, repo, pr_number)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()

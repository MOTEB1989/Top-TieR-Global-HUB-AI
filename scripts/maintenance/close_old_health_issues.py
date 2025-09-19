#!/usr/bin/env python3
"""
One-time cleanup script (archival).

Closes all open issues with titles like:
    "❌ Veritas Health Failed …"
Replaced by the persistent health monitor workflow (PR #271).

Usage:
    export GITHUB_TOKEN=ghp_xxx...
    python scripts/maintenance/close_old_health_issues.py [--dry-run]

Notes:
- One-off archival script; kept in repo for historical reference.
- Safe to re-run; it will simply skip if none match.
"""

import os
import sys
import requests
import argparse
import time

REPO = "MOTEB1989/Top-TieR-Global-HUB-AI"
API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    print("❌ Missing GITHUB_TOKEN (set it in your environment)")
    sys.exit(1)

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "User-Agent": "health-cleanup-script"
}

def get_open_issues():
    page = 1
    results = []
    while True:
        url = f"{API}/repos/{REPO}/issues?state=open&per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        results.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.2)  # tiny delay to be polite
    # Exclude PRs
    return [i for i in results if "pull_request" not in i]

def close_issue(number):
    url = f"{API}/repos/{REPO}/issues/{number}"
    data = {"state": "closed"}
    r = requests.patch(url, headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json()

def comment_issue(number, body):
    url = f"{API}/repos/{REPO}/issues/{number}/comments"
    r = requests.post(url, headers=HEADERS, json={"body": body})
    r.raise_for_status()
    return r.json()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without modifying issues.")
    args = parser.parse_args()

    issues = get_open_issues()
    target_prefix = "❌ Veritas Health Failed"
    to_close = [i for i in issues if i["title"].startswith(target_prefix)]

    if not to_close:
        print("✅ No old health issues to close.")
        return

    print(f"Found {len(to_close)} issues to close...")
    for issue in to_close:
        num = issue["number"]
        title = issue["title"]
        if args.dry_run:
            print(f"[DRY-RUN] Would comment & close #{num} – {title}")
            continue
        try:
            comment_issue(
                num,
                "🔒 Closed in favor of the persistent Veritas Health Monitor (PR #271).\n"\
                "Replacement workflow now handles ongoing health tracking."
            )
            close_issue(num)
            print(f"✅ Closed issue #{num} – {title}")
        except Exception as e:
            print(f"⚠️ Failed to close #{num}: {e}")

if __name__ == "__main__":
    main()
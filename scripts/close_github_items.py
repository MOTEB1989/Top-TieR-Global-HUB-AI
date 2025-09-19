#!/usr/bin/env python3
"""
Utility script to close open issues and pull requests in a repository.

Enhancements in this version:
- User-Agent header & Bearer auth style
- Optional filters: --before, --exclude, --label-exclude
- Rate limit handling (wait until reset if needed)
- Basic retry logic on transient errors (5xx / connection issues)
- Summary + error reporting
- Optional exclusion lists
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import time
from collections.abc import Generator, Iterable
from typing import Any

import requests

API_ROOT = "https://api.github.com"
DEFAULT_PAGE_SIZE = 100
RETRY_MAX = 5
RETRY_BACKOFF_BASE = 1.5  # exponential backoff base seconds


class GitHubClient:
    """Minimal GitHub REST API helper with pagination, retry & rate limit awareness."""

    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("A GitHub token is required (env GITHUB_TOKEN or --token).")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "close-github-items-script/1.1",
            }
        )

    def _handle_rate_limit(self, response: requests.Response) -> None:
        if response.status_code != 403:
            return
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        if remaining == "0" and reset:
            reset_epoch = int(reset)
            wait_for = max(0, reset_epoch - int(time.time())) + 1
            print(f"[RATE LIMIT] Waiting {wait_for} seconds until reset...", flush=True)
            time.sleep(wait_for)

    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> requests.Response:
        attempt = 0
        while True:
            attempt += 1
            try:
                response = self.session.request(method, url, params=params, json=json, timeout=30)
            except (requests.ConnectionError, requests.Timeout) as exc:
                if attempt >= RETRY_MAX:
                    raise
                sleep_for = RETRY_BACKOFF_BASE ** attempt
                print(f"[WARN] {exc} – retrying in {sleep_for:.1f}s (attempt {attempt}/{RETRY_MAX})")
                time.sleep(sleep_for)
                continue

            if response.status_code in {500, 502, 503, 504} and attempt < RETRY_MAX:
                sleep_for = RETRY_BACKOFF_BASE ** attempt
                print(
                    f"[WARN] Server error {response.status_code} – retrying in "
                    f"{sleep_for:.1f}s (attempt {attempt}/{RETRY_MAX})"
                )
                time.sleep(sleep_for)
                continue

            if response.status_code == 403:
                self._handle_rate_limit(response)
                if attempt < RETRY_MAX:
                    continue

            response.raise_for_status()
            return response

    def paginate(self, url: str, *, params: dict[str, Any] | None = None) -> Generator[dict, None, None]:
        query: dict[str, Any] = {"per_page": DEFAULT_PAGE_SIZE}
        if params:
            query.update(params)

        page = 1
        while True:
            resp = self._request_with_retry("GET", url, params={**query, "page": page})
            payload = resp.json()
            if not payload:
                break
            yield from payload
            if len(payload) < query["per_page"]:
                break
            page += 1

    def patch(self, url: str, *, json: dict[str, Any]) -> dict:
        resp = self._request_with_retry("PATCH", url, json=json)
        return resp.json()


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Close all (or filtered) open issues & pull requests.")
    parser.add_argument("repo", help="GitHub repository in the form 'owner/name'.")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub token (or env GITHUB_TOKEN).")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without performing them.")
    parser.add_argument("--skip-issues", action="store_true", help="Do not close issues.")
    parser.add_argument("--skip-prs", action="store_true", help="Do not close pull requests.")
    parser.add_argument("--exclude", nargs="*", type=int, default=[], help="Specific issue/PR numbers to exclude.")
    parser.add_argument(
        "--label-exclude",
        nargs="*",
        default=[],
        help="Skip items containing ANY of these labels (case-insensitive).",
    )
    parser.add_argument(
        "--before",
        type=str,
        default=None,
        help="Only close items created before this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Skip the confirmation prompt and proceed immediately."
    )
    return parser.parse_args(argv)


def confirm_action(repo: str) -> bool:
    prompt = (
        f"This will CLOSE open issues/pull requests for '{repo}'.\n"
        "Type 'yes' to continue: "
    )
    return input(prompt).strip().lower() == "yes"


def parse_date(d: str | None) -> dt.datetime | None:
    if not d:
        return None
    return dt.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)


def iso_to_dt(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def label_set(item: dict) -> set[str]:
    return {lbl["name"].lower() for lbl in item.get("labels", [])}


def should_skip(
    number: int,
    created_at: str,
    labels: set[str],
    *,
    exclude_numbers: set[int],
    label_exclude: set[str],
    cutoff: dt.datetime | None,
) -> bool:
    if number in exclude_numbers:
        return True
    if cutoff and iso_to_dt(created_at) >= cutoff:
        return True
    if label_exclude and (labels & label_exclude):
        return True
    return False


def close_issue(client: GitHubClient, repo: str, number: int, *, dry_run: bool) -> bool:
    if dry_run:
        print(f"[DRY RUN] Would close issue #{number}")
        return True
    client.patch(f"{API_ROOT}/repos/{repo}/issues/{number}", json={"state": "closed"})
    print(f"Closed issue #{number}")
    return True


def close_pr(client: GitHubClient, repo: str, number: int, *, dry_run: bool) -> bool:
    if dry_run:
        print(f"[DRY RUN] Would close pull request #{number}")
        return True
    client.patch(f"{API_ROOT}/repos/{repo}/pulls/{number}", json={"state": "closed"})
    print(f"Closed pull request #{number}")
    return True


def process_issues(
    client: GitHubClient,
    repo: str,
    *,
    dry_run: bool,
    exclude_numbers: set[int],
    label_exclude: set[str],
    cutoff: dt.datetime | None,
) -> tuple[int, int]:
    url = f"{API_ROOT}/repos/{repo}/issues"
    closed = skipped = 0
    for issue in client.paginate(url, params={"state": "open"}):
        if "pull_request" in issue:
            continue
        number = issue["number"]
        labels = label_set(issue)
        if should_skip(
            number,
            issue["created_at"],
            labels,
            exclude_numbers=exclude_numbers,
            label_exclude=label_exclude,
            cutoff=cutoff,
        ):
            skipped += 1
            print(f"[SKIP] Issue #{number}")
            continue
        try:
            close_issue(client, repo, number, dry_run=dry_run)
            closed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] Failed closing issue #{number}: {exc}")
    return closed, skipped


def process_prs(
    client: GitHubClient,
    repo: str,
    *,
    dry_run: bool,
    exclude_numbers: set[int],
    label_exclude: set[str],
    cutoff: dt.datetime | None,
) -> tuple[int, int]:
    url = f"{API_ROOT}/repos/{repo}/pulls"
    closed = skipped = 0
    for pr in client.paginate(url, params={"state": "open"}):
        number = pr["number"]
        created_at = pr.get("created_at") or pr.get("createdAt")
        labels = {lbl["name"].lower() for lbl in pr.get("labels", [])}
        if should_skip(
            number,
            created_at,
            labels,
            exclude_numbers=exclude_numbers,
            label_exclude=label_exclude,
            cutoff=cutoff,
        ):
            skipped += 1
            print(f"[SKIP] PR #{number}")
            continue
        try:
            close_pr(client, repo, number, dry_run=dry_run)
            closed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] Failed closing PR #{number}: {exc}")
    return closed, skipped


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    if args.skip_issues and args.skip_prs:
        print("Both issues and pull requests are skipped; nothing to do.")
        return 0

    if not args.yes and not confirm_action(args.repo):
        print("Aborted.")
        return 1

    try:
        client = GitHubClient(args.token)
    except ValueError as exc:
        print(exc)
        return 1

    cutoff = parse_date(args.before)
    exclude_numbers = set(args.exclude)
    label_exclude = {l.lower() for l in args.label_exclude}

    total_closed = 0
    total_skipped = 0

    if not args.skip_issues:
        c, s = process_issues(
            client,
            args.repo,
            dry_run=args.dry_run,
            exclude_numbers=exclude_numbers,
            label_exclude=label_exclude,
            cutoff=cutoff,
        )
        total_closed += c
        total_skipped += s

    if not args.skip_prs:
        c, s = process_prs(
            client,
            args.repo,
            dry_run=args.dry_run,
            exclude_numbers=exclude_numbers,
            label_exclude=label_exclude,
            cutoff=cutoff,
        )
        total_closed += c
        total_skipped += s

    print(
        "\nSummary:\n"
        f"  Closed:  {total_closed}\n"
        f"  Skipped: {total_skipped}\n"
        f"  Mode:    {'DRY-RUN' if args.dry_run else 'EXECUTION'}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
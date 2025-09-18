#!/usr/bin/env python3

"""Utility script to close all open issues and pull requests for a repository.

The script requires a GitHub personal access token with the appropriate scopes.
Provide it via the ``GITHUB_TOKEN`` environment variable or the ``--token`` flag.
"""
from __future__ import annotations

import argparse
import os
from collections.abc import Generator, Iterable

import requests

API_ROOT = "https://api.github.com"
DEFAULT_PAGE_SIZE = 100


class GitHubClient:
    """Small helper around :mod:`requests` for talking to the GitHub REST API."""

    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("A GitHub token is required to authenticate API calls.")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"token {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def paginate(self, url: str, *, params: dict[str, object] | None = None) -> Generator[dict, None, None]:
        """Yield results across paginated GitHub API responses."""

        query = {"per_page": DEFAULT_PAGE_SIZE}
        if params:
            query.update(params)

        page = 1
        while True:
            response = self.session.get(url, params={**query, "page": page})
            response.raise_for_status()
            payload = response.json()
            if not payload:
                break

            yield from payload

            if len(payload) < query["per_page"]:
                break

            page += 1

    def patch(self, url: str, *, json: dict[str, object]) -> dict:
        response = self.session.patch(url, json=json)
        response.raise_for_status()
        return response.json()


def close_issue(client: GitHubClient, repo: str, number: int, *, dry_run: bool = False) -> None:
    if dry_run:
        print(f"[DRY RUN] Would close issue #{number}")
        return

    client.patch(f"{API_ROOT}/repos/{repo}/issues/{number}", json={"state": "closed"})
    print(f"Closed issue #{number}")


def close_pr(client: GitHubClient, repo: str, number: int, *, dry_run: bool = False) -> None:
    if dry_run:
        print(f"[DRY RUN] Would close pull request #{number}")
        return

    client.patch(f"{API_ROOT}/repos/{repo}/pulls/{number}", json={"state": "closed"})
    print(f"Closed pull request #{number}")


def close_all_issues(client: GitHubClient, repo: str, *, dry_run: bool = False) -> None:
    issues_url = f"{API_ROOT}/repos/{repo}/issues"
    for issue in client.paginate(issues_url, params={"state": "open"}):
        if "pull_request" in issue:
            continue
        close_issue(client, repo, issue["number"], dry_run=dry_run)


def close_all_prs(client: GitHubClient, repo: str, *, dry_run: bool = False) -> None:
    pulls_url = f"{API_ROOT}/repos/{repo}/pulls"
    for pull in client.paginate(pulls_url, params={"state": "open"}):
        close_pr(client, repo, pull["number"], dry_run=dry_run)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="GitHub repository in the form 'owner/name'.")
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub token. Defaults to the value of the GITHUB_TOKEN environment variable.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without performing them.")
    parser.add_argument("--skip-issues", action="store_true", help="Do not close issues.")
    parser.add_argument("--skip-prs", action="store_true", help="Do not close pull requests.")
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt and proceed immediately.",
    )
    return parser.parse_args(argv)


def confirm_action(repo: str) -> bool:
    prompt = (
        "This will close all open issues and pull requests for "
        f"'{repo}'.\nType 'yes' to continue: "
    )
    response = input(prompt)
    return response.strip().lower() == "yes"


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

    if not args.skip_issues:
        close_all_issues(client, args.repo, dry_run=args.dry_run)

    if not args.skip_prs:
        close_all_prs(client, args.repo, dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

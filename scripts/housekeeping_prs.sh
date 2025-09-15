#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   GH_TOKEN=xxxx ./scripts/housekeeping_prs.sh "70 77 78" "53 54 55"
# The priority list will be labeled with 'priority'.
# The supersede list will be closed with a standard comment.

OWNER="MOTEB1989"
REPO="Top-TieR-Global-HUB-AI"

PRIORITY="${1:-}"
SUPERSEDE="${2:-}"

has(){ command -v "$1" >/dev/null 2>&1; }

if ! has gh; then
  echo "Install GitHub CLI (gh) first."
  exit 1
fi

if [[ -n "$PRIORITY" ]]; then
  for n in $PRIORITY; do
    echo "[priority] PR #$n"
    gh pr edit "$n" -R "$OWNER/$REPO" --add-label "priority"
    gh pr comment "$n" -R "$OWNER/$REPO" --body "Marking as **priority** for merge window."
  done
fi

if [[ -n "$SUPERSEDE" ]]; then
  for n in $SUPERSEDE; do
    echo "[close] PR #$n"
    gh pr close "$n" -R "$OWNER/$REPO" --delete-branch=false --comment "Closed as **superseded** by priority PRs."
  done
fi

echo "✓ Done."
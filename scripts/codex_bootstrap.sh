#!/usr/bin/env bash
set -euo pipefail

REPO_SLUG="${REPO_SLUG:-MOTEB1989/Top-TieR-Global-HUB-AI}"
: "${LEXCODE_GITHUB_TOKEN:?❌ متغير LEXCODE_GITHUB_TOKEN غير موجود في البيئة. وفّر السر من GitHub Secrets.}"

echo "🔐 Authenticating Codex with GitHub…"
codex auth github --token "$LEXCODE_GITHUB_TOKEN"

echo "🔗 Connecting Codex to repo: $REPO_SLUG"
codex connect github --repo "$REPO_SLUG"

echo "🩺 Checking connection status…"
codex status github --repo "$REPO_SLUG"

echo "✅ Done."

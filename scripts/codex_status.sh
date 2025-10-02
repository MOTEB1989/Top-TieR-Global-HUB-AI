#!/usr/bin/env bash
set -euo pipefail

REPO_SLUG="${REPO_SLUG:-MOTEB1989/Top-TieR-Global-HUB-AI}"
: "${LEXCODE_GITHUB_TOKEN:?❌ متغير LEXCODE_GITHUB_TOKEN غير موجود في البيئة.}"

codex auth github --token "$LEXCODE_GITHUB_TOKEN"
codex status github --repo "$REPO_SLUG" | tee codex_status.txt

echo "📄 Saved status to codex_status.txt"

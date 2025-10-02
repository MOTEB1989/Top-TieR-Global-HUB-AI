#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

STATUS_FILE="${REPO_ROOT}/codex_status.txt"

: "${LEXCODE_GITHUB_TOKEN:?LEXCODE_GITHUB_TOKEN environment variable is required}"

CODEX_CLI="codex"

log() {
  echo "[codex-bootstrap] $1"
}

run_codex() {
  local cmd=("${CODEX_CLI}" "$@")
  if ! "${cmd[@]}"; then
    log "Command failed: ${cmd[*]}"
    return 1
  fi
}

if ! command -v "${CODEX_CLI}" >/dev/null 2>&1; then
  log "Codex CLI is not installed or not on PATH"
  exit 1
fi

log "Authenticating Codex CLI"
run_codex auth login --github-token "${LEXCODE_GITHUB_TOKEN}" --non-interactive

log "Connecting repository"
run_codex connect --path "${REPO_ROOT}"

log "Checking Codex status"
run_codex status --path "${REPO_ROOT}" | tee "${STATUS_FILE}"

log "Status written to ${STATUS_FILE}"

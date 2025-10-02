#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STATUS_FILE="${REPO_ROOT}/codex_status.txt"

CODEX_CLI="codex"

log() {
  echo "[codex-status] $1"
}

if ! command -v "${CODEX_CLI}" >/dev/null 2>&1; then
  log "Codex CLI is not installed or not on PATH"
  exit 1
fi

log "Gathering Codex status for ${REPO_ROOT}"
"${CODEX_CLI}" status --path "${REPO_ROOT}" | tee "${STATUS_FILE}"

log "Status written to ${STATUS_FILE}"

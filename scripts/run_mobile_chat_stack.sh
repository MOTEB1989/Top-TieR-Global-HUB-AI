#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${REPO_ROOT}/docker-compose.rag.yml"

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "docker-compose.rag.yml not found at ${COMPOSE_FILE}" >&2
  exit 1
fi

echo "Validating compose file..."
docker compose -f "${COMPOSE_FILE}" config >/dev/null

detect_local_ip() {
  local ip=""
  if command -v ipconfig >/dev/null 2>&1; then
    ip=$(ipconfig getifaddr en0 2>/dev/null || true)
  fi
  if [[ -z "${ip}" ]]; then
    if command -v hostname >/dev/null 2>&1; then
      ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi
  fi
  if [[ -z "${ip}" ]]; then
    if command -v ip >/dev/null 2>&1; then
      ip=$(ip route get 1 2>/dev/null | awk '{print $7; exit}')
    fi
  fi
  echo "${ip}"
}

LOCAL_IP=$(detect_local_ip)
if [[ -n "${LOCAL_IP}" ]]; then
  echo "Open on your iPhone: http://${LOCAL_IP}:8501"
else
  echo "Open on your iPhone: http://<YOUR-LAN-IP>:8501"
fi

echo "Starting local mobile chat stack (qdrant, rag_engine, phi3, gateway, web_ui)..."
docker compose -f "${COMPOSE_FILE}" up --build qdrant rag_engine phi3 gateway web_ui

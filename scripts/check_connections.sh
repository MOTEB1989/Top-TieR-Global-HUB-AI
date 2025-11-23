#!/usr/bin/env bash
set -euo pipefail

# scripts/check_connections.sh
# Comprehensive preflight: validate docker-compose, services, ports, models, and secrets.
# Sends a compact report to Telegram if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set.
#
# Usage:
#   chmod +x scripts/check_connections.sh
#   API_PORT=3000 TELEGRAM_BOT_TOKEN="..." TELEGRAM_CHAT_ID="..." ./scripts/check_connections.sh

REPO="MOTEB1989/Top-TieR-Global-HUB-AI"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# ---------- Configuration ----------
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
TELEGRAM_ALLOWLIST="${TELEGRAM_ALLOWLIST:-}"   # optional, e.g. "8256840669,6090738107"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
API_PORT="${API_PORT:-3000}"
ULTRA_PREFLIGHT_PATH="${ULTRA_PREFLIGHT_PATH:-scripts/ultra_preflight.sh}"
FULL_SCAN_SCRIPT="${FULL_SCAN_SCRIPT:-scripts/execute_full_scan.sh}"
LOG_FILE_PATH="${LOG_FILE_PATH:-analysis/ULTRA_REPORT.md}"
REPORT_OUT="${REPORT_OUT:-reports/check_connections.json}"

# ---------- Helpers ----------
log() { printf "%s %s\n" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"; }
exists() { command -v "$1" >/dev/null 2>&1; }

# ---------- 0. Environment quick-check ----------
log "Starting repository preflight check: $REPO"
mkdir -p "$(dirname "$REPORT_OUT")"

declare -A status
status[time]="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# ---------- 1. Files & structure ----------
log "Checking key files..."
status[has_docker_compose]="false"
if [[ -f "docker-compose.yml" ]]; then
  status[has_docker_compose]="true"
  status[dcompose_path]="docker-compose.yml"
fi

status[has_ultra_preflight]="false"
if [[ -f "$ULTRA_PREFLIGHT_PATH" ]]; then
  status[has_ultra_preflight]="true"
fi

status[has_full_scan_script]="false"
if [[ -f "$FULL_SCAN_SCRIPT" ]]; then
  status[has_full_scan_script]="true"
fi

status[has_log_file]="false"
if [[ -f "$LOG_FILE_PATH" ]]; then
  status[has_log_file]="true"
fi

# ---------- 2. Docker Compose services & ports ----------
services_list=""
ports_list=""
if [[ "${status[has_docker_compose]}" == "true" ]]; then
  if exists docker-compose || (exists docker && docker compose version >/dev/null 2>&1); then
    services_list="$(docker compose config --services 2>/dev/null || docker-compose config --services 2>/dev/null || true)"
    status[dcompose_services]="$services_list"
    # Extract published ports (works with compose v1/legacy); fallback to parsing file if jq missing
    if exists docker && docker compose version >/dev/null 2>&1; then
      # docker compose native
      ports_list="$(docker compose -f docker-compose.yml config | sed -n 's/.*- \"\([0-9]*:[0-9]*\)\".*/\1/p' | sort -u || true)"
    else
      ports_list="$(grep -E '^[[:space:]]*-[[:space:]]*"[0-9]+:[0-9]+' docker-compose.yml || true)"
    fi
    status[dcompose_ports]="$ports_list"
  else
    status[docker_compose_cli_missing]="true"
  fi
else
  status[dcompose_note]="docker-compose.yml not found"
fi

# ---------- 3. Check expected ports locally ----------
log "Checking local listeners for API_PORT=${API_PORT}..."
listening="false"
if exists ss; then
  if ss -ltn 2>/dev/null | grep -q ":${API_PORT}[[:space:]]"; then
    listening="true"
  fi
elif exists lsof; then
  if lsof -iTCP -sTCP:LISTEN -P -n 2>/dev/null | grep -q ":${API_PORT}[[:space:]]"; then
    listening="true"
  fi
elif exists netstat; then
  if netstat -ltn 2>/dev/null | grep -q ":${API_PORT}[[:space:]]"; then
    listening="true"
  fi
fi
status[api_port_listening]="$listening"

# ---------- 4. Models / env hints search ----------
log "Scanning for MODEL= or PHI3 references..."
models_found="$(grep -R --line-number --exclude-dir=.git -E 'MODEL=|PHI3|phi-3|QDRANT_URL|OPENAI_API_KEY' . 2>/dev/null | head -n 50 || true)"
status[models_found_count]=$(echo "$models_found" | wc -l)
status[models_found_sample]="$(echo "$models_found" | head -n 20 | tr '\n' ' ; ')"

# ---------- 5. Secrets / env check ----------
log "Checking required environment variables / secrets..."
declare -A env_ok
check_var() {
  local name="$1"
  local val="${!name:-}"
  if [[ -n "$val" ]]; then
    env_ok[$name]="present"
  else
    env_ok[$name]="missing"
  fi
}
check_var TELEGRAM_BOT_TOKEN
check_var TELEGRAM_CHAT_ID
check_var TELEGRAM_ALLOWLIST
check_var GITHUB_TOKEN
check_var OPENAI_API_KEY
check_var GROQ_API_KEY
check_var ANTHROPIC_API_KEY
check_var DB_URL
check_var REDIS_URL
check_var NEO4J_URI
check_var NEO4J_AUTH

# copy into status
for k in "${!env_ok[@]}"; do
  status["env_$k"]="${env_ok[$k]}"
done

# ---------- 6. Optional: attempt Telegram sendMessage (dry) ----------
telegram_ok="skipped"
if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
  # do a light test: getMe
  resp="$(curl -s -m 10 "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" || true)"
  if echo "$resp" | grep -q '"ok":true'; then
    telegram_ok="ok"
  else
    telegram_ok="error"
    status[telegram_getme_resp]="$resp"
  fi
else
  status[telegram_test_note]="missing token/chat_id - skipping test"
fi
status[telegram_test]="$telegram_ok"

# ---------- 7. Generate JSON report ----------
jq_available=false
if exists jq; then jq_available=true; fi

# produce JSON in a simple portable way
cat > "$REPORT_OUT" <<EOF
{
  "repo": "$REPO",
  "scan_time": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "docker_compose": {
    "present": ${status[has_docker_compose]:-false},
    "services": "$(echo "${status[dcompose_services]:-}" | tr '\n' ',' )",
    "ports": "$(echo "${status[dcompose_ports]:-}" | tr '\n' ',' )"
  },
  "api_port": {
    "port": $API_PORT,
    "listening": "${status[api_port_listening]}"
  },
  "models_found_count": ${status[models_found_count]:-0},
  "models_sample": "${status[models_found_sample]:-}",
  "telegram_test": "${status[telegram_test]:-}",
  "env": {
    "TELEGRAM_BOT_TOKEN": "${env_ok[TELEGRAM_BOT_TOKEN]:-missing}",
    "TELEGRAM_CHAT_ID": "${env_ok[TELEGRAM_CHAT_ID]:-missing}",
    "TELEGRAM_ALLOWLIST": "${env_ok[TELEGRAM_ALLOWLIST]:-missing}",
    "GITHUB_TOKEN": "${env_ok[GITHUB_TOKEN]:-missing}",
    "OPENAI_API_KEY": "${env_ok[OPENAI_API_KEY]:-missing}",
    "GROQ_API_KEY": "${env_ok[GROQ_API_KEY]:-missing}",
    "ANTHROPIC_API_KEY": "${env_ok[ANTHROPIC_API_KEY]:-missing}",
    "DB_URL": "${env_ok[DB_URL]:-missing}",
    "REDIS_URL": "${env_ok[REDIS_URL]:-missing}",
    "NEO4J_URI": "${env_ok[NEO4J_URI]:-missing}",
    "NEO4J_AUTH": "${env_ok[NEO4J_AUTH]:-missing}"
  }
}
EOF

log "JSON report written to: $REPORT_OUT"

# ---------- 8. Optionally send summary to Telegram if configured ----------
if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
  summary="✅ Preflight Check - $REPO

📦 Services: ${status[dcompose_services]:-n/a}
🔌 Ports: ${status[dcompose_ports]:-n/a}
🚀 API Port: ${API_PORT} (listening: ${status[api_port_listening]})
🤖 Telegram: ${status[telegram_test]}

🔑 Env Status:
TELEGRAM_BOT_TOKEN: ${env_ok[TELEGRAM_BOT_TOKEN]:-missing}
TELEGRAM_CHAT_ID: ${env_ok[TELEGRAM_CHAT_ID]:-missing}
OPENAI_API_KEY: ${env_ok[OPENAI_API_KEY]:-missing}

📊 Report: $REPORT_OUT
⏰ $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
  
  # URL encode for Telegram (bash-only, no external deps)
  encoded_text="${summary// /%20}"
  encoded_text="${encoded_text//$'\n'/%0A}"
  
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${encoded_text}" \
    -d "parse_mode=HTML" >/dev/null 2>&1 || true
  log "Telegram summary attempted (may be blocked if TELEGRAM_ALLOWLIST restricts)."
fi

log "Preflight finished. Report: $REPORT_OUT"
echo
log "شوف التقرير: $REPORT_OUT"

# ---------- 9. Display summary ----------
echo
echo "=========================================="
echo "📊 Preflight Check Summary"
echo "=========================================="
echo "Repository: $REPO"
echo "Time: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
echo "Docker Compose: ${status[has_docker_compose]}"
echo "Services: ${status[dcompose_services]:-none}"
echo "API Port: $API_PORT (listening: ${status[api_port_listening]})"
echo "Telegram Test: ${status[telegram_test]}"
echo
echo "Environment Variables Status:"
echo "  ✅ = present | ❌ = missing"
for k in TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID GITHUB_TOKEN OPENAI_API_KEY GROQ_API_KEY ANTHROPIC_API_KEY DB_URL REDIS_URL NEO4J_URI NEO4J_AUTH; do
  status_icon="❌"
  [[ "${env_ok[$k]:-missing}" == "present" ]] && status_icon="✅"
  printf "  %s %-23s: %s\n" "$status_icon" "$k" "${env_ok[$k]:-missing}"
done
echo "=========================================="
echo
if [[ "$jq_available" == "true" ]]; then
  log "Full report (formatted):"
  jq . "$REPORT_OUT"
else
  log "Install 'jq' for formatted JSON output"
  cat "$REPORT_OUT"
fi

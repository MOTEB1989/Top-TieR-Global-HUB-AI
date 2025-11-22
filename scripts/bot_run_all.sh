#!/usr/bin/env bash
set -euo pipefail

# ==========================================================
#  Bot Runner – Full Auto Orchestrator
#  - Validates environment and compose
#  - Ensures .env
#  - Starts RAG stack (Docker if available)
#  - Health checks + auto-fix
#  - Writes JSON report: scripts/stack_report.json
# ==========================================================

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE=""
REPORT_PATH="${REPO_ROOT}/scripts/stack_report.json"
SERVICES=("qdrant" "rag_engine" "phi3" "gateway" "web_ui")
HEALTH_URLS=(
  "http://localhost:6333/readyz"   # qdrant
  "http://localhost:8081/health"   # rag_engine
  "http://localhost:8082/health"   # phi3
  "http://localhost:3000/health"   # gateway
  "http://localhost:8501"          # web_ui (root)
)
MAX_RETRIES=2
AUTO_FIX=1
SLEEP_AFTER_UP=5

info()    { echo -e "\033[1;36m$*\033[0m"; }
warn()    { echo -e "\033[1;33m$*\033[0m"; }
error()   { echo -e "\033[1;31m$*\033[0m"; }
success() { echo -e "\033[1;32m$*\033[0m"; }

ACTION="up"
for arg in "$@"; do
  case "$arg" in
    --no-auto-fix) AUTO_FIX=0 ;;
    up|down|status) ACTION="$arg" ;;
    *) warn "Unknown argument: $arg" ;;
  esac
done

DOCKER_OK=0
COMPOSE_CMD="docker compose"
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  DOCKER_OK=1
fi

if [ -f "${REPO_ROOT}/docker-compose.rag.yml" ]; then
  COMPOSE_FILE="${REPO_ROOT}/docker-compose.rag.yml"
elif [ -f "${REPO_ROOT}/docker-compose.yml" ]; then
  COMPOSE_FILE="${REPO_ROOT}/docker-compose.yml"
fi

ensure_env() {
  if [[ ! -f "${REPO_ROOT}/.env" ]]; then
    warn "⚠️ .env not found — generating a default one."
    cat <<EOF > "${REPO_ROOT}/.env"
LLM_PROVIDER=phi_local
PHI3_URL=http://phi3:8082
RAG_ENGINE_URL=http://rag_engine:8081
OPENAI_API_KEY=
GROQ_API_KEY=
ANTHROPIC_API_KEY=
NEO4J_URI=
QDRANT_URL=http://qdrant:6333
EOF
    success "✅ .env created."
  else
    success "✅ .env exists."
  fi
}

validate_compose() {
  if (( DOCKER_OK == 1 )) && [[ -n "$COMPOSE_FILE" ]]; then
    info "🔍 Validating compose file: $(basename "$COMPOSE_FILE")"
    if ! $COMPOSE_CMD -f "$COMPOSE_FILE" config >/dev/null; then
      error "❌ docker compose config failed."
      exit 1
    fi
    success "✅ docker-compose file is valid."
  else
    warn "ℹ️ Docker or compose file not available, will fallback if possible."
  fi
}

detect_ip() {
  local ip=""
  if command -v ipconfig >/dev/null 2>&1; then
    ip=$(ipconfig getifaddr en0 2>/dev/null || true)
    [[ -z "$ip" ]] && ip=$(ipconfig getifaddr en1 2>/dev/null || true)
  fi
  if [[ -z "$ip" ]] && command -v hostname >/dev/null 2>&1; then
    ip=$(hostname -I 2>/dev/null | awk '{print $1}')
  fi
  echo "$ip"
}
LOCAL_IP="$(detect_ip)"

codespaces_url() {
  local port="$1"
  if [[ -n "${CODESPACE_NAME:-}" ]]; then
    echo "https://${CODESPACE_NAME}-${port}.app.github.dev"
  fi
}

http_check() {
  local url="$1"
  local code
  code="$(curl -fsS -o /dev/null -w "%{http_code}" --max-time 4 "$url" || true)"
  if [[ "$code" =~ ^2[0-9][0-9]$ || "$code" =~ ^3[0-9][0-9]$ ]]; then
    echo "healthy|$code"
  elif [[ -z "$code" ]]; then
    echo "unhealthy|000"
  else
    echo "unhealthy|$code"
  fi
}

stack_up_docker() {
  info "🚀 Starting stack via Docker..."
  $COMPOSE_CMD -f "$COMPOSE_FILE" up --build -d "${SERVICES[@]}"
  info "⏳ Waiting ${SLEEP_AFTER_UP}s for services to initialize..."
  sleep "$SLEEP_AFTER_UP"
}

stack_down_docker() {
  info "🛑 Stopping stack via Docker..."
  $COMPOSE_CMD -f "$COMPOSE_FILE" down
}

stack_status_docker() {
  $COMPOSE_CMD -f "$COMPOSE_FILE" ps
}

fallback_no_docker() {
  warn "⚠️ Docker not available and no fallback runner implemented."
}

health_and_fix() {
  local -a STATUSES=()
  local -a CODES=()
  local unhealthy_any=0

  info "🩺 Running health checks..."
  local i
  for i in "${!SERVICES[@]}"; do
    local name="${SERVICES[$i]}"
    local url="${HEALTH_URLS[$i]}"
    local res code
    res="$(http_check "$url")"
    code="${res#*|}"
    res="${res%%|*}"
    STATUSES[$i]="$res"
    CODES[$i]="$code"
    if [[ "$res" != "healthy" ]]; then
      unhealthy_any=1
      warn "🔴 $name health failed (${code}) at ${url}"
    else
      success "🟢 $name healthy (${code})"
    fi
  done

  if (( unhealthy_any == 1 && AUTO_FIX == 1 && DOCKER_OK == 1 && ${#COMPOSE_FILE} > 0 )); then
    info "🛠️ Auto-fix enabled. Attempting repairs..."
    local attempt
    for attempt in $(seq 1 "$MAX_RETRIES"); do
      local repaired=0
      local i
      for i in "${!SERVICES[@]}"; do
        if [[ "${STATUSES[$i]}" == "healthy" ]]; then
          continue
        fi
        local svc="${SERVICES[$i]}"
        info "🔄 Attempt #${attempt}: repairing service '$svc'..."
        $COMPOSE_CMD -f "$COMPOSE_FILE" stop "$svc" || true
        $COMPOSE_CMD -f "$COMPOSE_FILE" rm -f "$svc" || true
        $COMPOSE_CMD -f "$COMPOSE_FILE" up --build -d "$svc" || true
        repaired=1
      done
      if (( repaired == 1 )); then
        info "⏳ Waiting ${SLEEP_AFTER_UP}s before re-check..."
        sleep "$SLEEP_AFTER_UP"
        unhealthy_any=0
        for i in "${!SERVICES[@]}"; do
          local name="${SERVICES[$i]}"
          local url="${HEALTH_URLS[$i]}"
          local res code
          res="$(http_check "$url")"
          code="${res#*|}"
          res="${res%%|*}"
          STATUSES[$i]="$res"
          CODES[$i]="$code"
          if [[ "$res" != "healthy" ]]; then
            unhealthy_any=1
            warn "🔴 $name still failing (${code})"
          else
            success "🟢 $name recovered (${code})"
          fi
        done
      fi
      if (( unhealthy_any == 0 )); then
        break
      fi
    done
  fi

  info "📝 Writing JSON report: ${REPORT_PATH}"
  mkdir -p "$(dirname "$REPORT_PATH")"
  {
    echo "{"
    echo "  \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"," 
    echo "  \"auto_fix\": ${AUTO_FIX},"
    echo "  \"environment\": {"
    echo "    \"docker_available\": ${DOCKER_OK},"
    echo "    \"codespaces\": \"${CODESPACE_NAME:-}\"," 
    echo "    \"local_ip\": \"${LOCAL_IP:-}\""
    echo "  },"
    echo "  \"services\": ["
    local first=1
    local i
    for i in "${!SERVICES[@]}"; do
      [[ $first -eq 0 ]] && echo "    ,"
      first=0
      printf '    {"name":"%s","url":"%s","status":"%s","http_code":"%s"}' \
        "${SERVICES[$i]}" "${HEALTH_URLS[$i]}" "${STATUSES[$i]}" "${CODES[$i]}"
    done
    echo ""
    echo "  ]"
    echo "}"
  } > "$REPORT_PATH"

  echo ""
  echo "========================================="
  if (( unhealthy_any == 0 )); then
    success "🎉 All services healthy"
  else
    warn "⚠️ Some services are unhealthy. See report: ${REPORT_PATH}"
  fi
  echo "========================================="
}

print_urls() {
  echo ""
  echo "========================================="
  success "ACCESS POINTS"
  echo "========================================="
  local ip_url=""
  if [[ -n "${LOCAL_IP:-}" ]]; then
    ip_url="http://${LOCAL_IP}"
  fi

  local streamlit_cs="$(codespaces_url 8501)"
  local gateway_cs="$(codespaces_url 3000)"
  local rag_cs="$(codespaces_url 8081)"
  local phi_cs="$(codespaces_url 8082)"
  local qdrant_cs="$(codespaces_url 6333)"

  echo "📌 Streamlit Chat UI:"
  echo "   - Localhost:   http://localhost:8501"
  [[ -n "$ip_url" ]] && echo "   - iPhone/LAN:  ${ip_url}:8501"
  [[ -n "$streamlit_cs" ]] && echo "   - Codespaces:  ${streamlit_cs}"

  echo ""
  echo "📌 Gateway:"
  echo "   - Localhost:   http://localhost:3000"
  [[ -n "$ip_url" ]] && echo "   - iPhone/LAN:  ${ip_url}:3000"
  [[ -n "$gateway_cs" ]] && echo "   - Codespaces:  ${gateway_cs}"

  echo ""
  echo "📌 RAG Engine:    http://localhost:8081"
  [[ -n "$ip_url" ]] && echo "   - iPhone/LAN:  ${ip_url}:8081"
  [[ -n "$rag_cs" ]] && echo "   - Codespaces:  ${rag_cs}"

  echo ""
  echo "📌 Phi-3 Runner:  http://localhost:8082"
  [[ -n "$ip_url" ]] && echo "   - iPhone/LAN:  ${ip_url}:8082"
  [[ -n "$phi_cs" ]] && echo "   - Codespaces:  ${phi_cs}"

  echo ""
  echo "📌 Qdrant UI:     http://localhost:6333"
  [[ -n "$ip_url" ]] && echo "   - iPhone/LAN:  ${ip_url}:6333"
  [[ -n "$qdrant_cs" ]] && echo "   - Codespaces:  ${qdrant_cs}"

  echo ""
  success "🟢 Ready"
  echo "========================================="
}

info "📍 Repository root: $REPO_ROOT"

ensure_env
validate_compose

case "$ACTION" in
  up)
    if (( DOCKER_OK == 1 )) && [[ -n "$COMPOSE_FILE" ]]; then
      stack_up_docker
    else
      fallback_no_docker
    fi
    health_and_fix
    print_urls
    ;;
  down)
    if (( DOCKER_OK == 1 )) && [[ -n "$COMPOSE_FILE" ]]; then
      stack_down_docker
      success "✅ Stack stopped."
    else
      warn "ℹ️ No Docker stack to stop."
    fi
    ;;
  status)
    if (( DOCKER_OK == 1 )) && [[ -n "$COMPOSE_FILE" ]]; then
      stack_status_docker
    else
      warn "ℹ️ No Docker status available."
    fi
    ;;
  *)
    error "Unknown action: $ACTION"
    exit 1
    ;;
esac

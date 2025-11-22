#!/usr/bin/env bash
set -euo pipefail

# =========[ Top-Tier Global HUB AI – Full Runner v2 ]============
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${REPO_ROOT}/docker-compose.rag.yml"
HEALTH_SCRIPT="${REPO_ROOT}/scripts/system_health_check.py"
SERVICES=(qdrant rag_engine phi3 gateway web_ui)

info()    { echo -e "\033[1;36m$*\033[0m"; }
warn()    { echo -e "\033[1;33m$*\033[0m"; }
error()   { echo -e "\033[1;31m$*\033[0m"; }
success() { echo -e "\033[1;32m$*\033[0m"; }

die() { error "$*"; exit 1; }

ACTION="up"
AUTO_FIX=0
for arg in "$@"; do
  case "$arg" in
    up) ACTION="up" ;;
    --auto-fix) AUTO_FIX=1 ;;
    *) warn "Unknown argument: $arg" ;;
  esac
done

info "📍 Repository root: $REPO_ROOT"

# 1) Docker presence
if ! command -v docker >/dev/null 2>&1; then
  die "❌ Docker غير مثبت في هذا الجهاز. الرجاء تثبيت Docker ثم إعادة المحاولة."
fi
success "✅ Docker detected."

# 2) Compose file
info "🔍 Checking docker-compose.rag.yml..."
[ -f "$COMPOSE_FILE" ] || die "❌ الملف غير موجود: $COMPOSE_FILE"
docker compose -f "$COMPOSE_FILE" config >/dev/null || die "❌ يوجد خطأ في بناء ملف الـ compose. الرجاء التصحيح."
success "✅ docker-compose.rag.yml is valid."

# 3) .env
if [[ ! -f "${REPO_ROOT}/.env" ]]; then
  warn "⚠️ لم يتم العثور على .env — سيتم توليد ملف تلقائي."
  cat <<'ENVEOF' > "${REPO_ROOT}/.env"
LLM_PROVIDER=phi_local
PHI3_URL=http://phi3:8082
RAG_ENGINE_URL=http://rag_engine:8081
OPENAI_API_KEY=
GROQ_API_KEY=
ANTHROPIC_API_KEY=
NEO4J_URI=
QDRANT_URL=http://qdrant:6333
ENVEOF
  success "✅ تم توليد ملف .env."
else
  success "✅ ملف .env موجود."
fi

# 4) Local IP
detect_ip() {
  local ip=""
  if command -v ipconfig >/dev/null 2>&1; then
    ip=$(ipconfig getifaddr en0 2>/dev/null || true)
  fi
  if [[ -z "$ip" ]] && command -v hostname >/dev/null 2>&1; then
    ip=$(hostname -I 2>/dev/null | awk '{print $1}')
  fi
  echo "$ip"
}
LOCAL_IP=$(detect_ip)
info "🌐 Local IP for iPhone: ${LOCAL_IP:-unknown}"

if [[ "$ACTION" == "up" ]]; then
  info "🚀 Starting the full RAG stack..."
  docker compose -f "$COMPOSE_FILE" up --build -d "${SERVICES[@]}"
  info "⏳ Waiting 5 seconds for services to initialize..."
  sleep 5

  HC_FAILED=()
  if [[ -f "$HEALTH_SCRIPT" ]]; then
    info "🩺 Running health check..."
    HC_LOG=$(python3 "$HEALTH_SCRIPT" 2>&1 || true)
    echo "$HC_LOG"
    while IFS= read -r line; do
      [[ "$line" =~ "❌" ]] || continue
      for srv in "${SERVICES[@]}"; do
        name="${srv//_/ }"
        [[ "$line" =~ $name ]] && HC_FAILED+=("$srv")
      done
    done <<< "$HC_LOG"

    if (( ${#HC_FAILED[@]} > 0 )) && (( AUTO_FIX == 1 )); then
      warn "⚠️ Attempting auto-fix for: ${HC_FAILED[*]}"
      for broken in "${HC_FAILED[@]}"; do
        info "🔄 Restarting $broken service..."
        docker compose -f "$COMPOSE_FILE" stop "$broken" || true
        docker compose -f "$COMPOSE_FILE" rm -f "$broken" || true
        docker compose -f "$COMPOSE_FILE" up --build -d "$broken"
      done
      info "🩺 Re-checking health after auto-fix..."
      sleep 3
      python3 "$HEALTH_SCRIPT" || true
    elif (( ${#HC_FAILED[@]} > 0 )); then
      warn "⚠️ Some services unhealthy: ${HC_FAILED[*]}. Rerun with --auto-fix to attempt repair."
    else
      success "🟢 All services healthy."
    fi
  else
    warn "⚠️ لم يتم العثور على: $HEALTH_SCRIPT"
  fi

  echo ""
  echo "========================================="
  success "🎉 STACK IS RUNNING – ACCESS POINTS:"
  echo "========================================="
  echo "📌 Streamlit Chat UI:"
  echo "   http://localhost:8501"
  [[ -n "${LOCAL_IP:-}" ]] && echo "   📱 iPhone: http://${LOCAL_IP}:8501"
  echo ""
  echo "📌 Gateway:         http://localhost:3000"
  echo "📌 RAG Engine:      http://localhost:8081"
  echo "📌 Local Phi-3:     http://localhost:8082"
  echo "📌 Qdrant UI:       http://localhost:6333"
  echo ""
  echo "========================================="
  success "🟢 تم تشغيل النظام بالكامل بنجاح"
  echo "========================================="
else
  error "Unknown action: $ACTION"
fi

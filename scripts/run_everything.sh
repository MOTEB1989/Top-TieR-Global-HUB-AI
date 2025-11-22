#!/usr/bin/env bash
set -euo pipefail

##############################################
# Top-Tier Global HUB AI – Unified Runner
# (RAG + Phi3 + Gateway + Web UI + Health)
# Supports selective service start (up/restart <services...>)
##############################################

# ========== Config ==========
REPO_ROOT="$(cd "".$0})/.." && pwd)"
COMPOSE_FILE="${REPO_ROOT}/docker-compose.rag.yml"
HEALTH_SCRIPT="${REPO_ROOT}/scripts/system_health_check.py"
ENV_FILE="${REPO_ROOT}/.env"

# Colors
C_RESET=$'\033[0m'
C_RED=$'\033[31m'
C_GREEN=$'\033[32m'
C_YELLOW=$'\033[33m'
C_BLUE=$'\033[34m'
C_CYAN=$'\033[36m'
C_PURPLE=$'\033[35m'

log()   { printf "%s\n" "$*"; }
info()  { log "${C_BLUE}ℹ${C_RESET} $*"; }
ok()    { log "${C_GREEN}✅${C_RESET} $*"; }
warn()  { log "${C_YELLOW}⚠️${C_RESET} $*"; }
err()   { log "${C_RED}❌ $*${C_RESET}"; }

cleanup() { err "حدث فشل غير متوقع أثناء التنفيذ."; }
trap cleanup ERR

usage() {
  cat <<EOF
Usage: $0 [command] [options] [services]

Commands:
  up [svc..]        تشغيل الستاك (كامل أو خدمات محددة)
  down              إيقاف وحذف الحاويات (مع الاحتفاظ بالبيانات)
  restart [svc..]   إعادة تشغيل كل الخدمات أو خدمات محددة
  ps                عرض حالة الحاويات
  logs [svc]        عرض السجلات (جميعها أو خدمة محددة)
  health            تشغيل فحص الصحة فقط
  services          عرض قائمة الخدمات في ملف الـ compose

Options:
  --no-build        تشغيل بدون إعادة بناء الصور
  --pull            سحب آخر نسخة من الصور قبل التشغيل
  --auto-fix        محاولة تصحيح الحالات الفاشلة بعد التشغيل
  -h|--help         إظهار هذه المساعدة

أمثلة:
  $0 up                      تشغيل جميع الخدمات
  $0 up gateway web_ui       تشغيل gateway و web_ui فقط
  $0 restart rag_engine      إعادة تشغيل خدمة rag_engine فقط
  $0 logs gateway            عرض سجلات gateway
  $0 up --no-build --auto-fix
EOF
}

COMMAND="up"
NO_BUILD=0
DO_PULL=0
AUTO_FIX=0
declare -a ARGS=()

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    up|down|restart|ps|logs|health|services) COMMAND="$1"; shift ;; 
    --no-build) NO_BUILD=1; shift ;;
    --pull) DO_PULL=1; shift ;;
    --auto-fix) AUTO_FIX=1; shift ;;
    -h|--help) usage; exit 0 ;;  
    *) ARGS+=("$1"); shift ;;
  esac
done

info "📍 Repository root: $REPO_ROOT"

# Docker check
if ! command -v docker >/dev/null 2>&1; then
  err "Docker غير مثبت. رجاءً ثبّت Docker ثم أعد المحاولة."; exit 1; fi
ok "Docker detected."

if ! docker compose version >/dev/null 2>&1; then
  warn "أمر docker compose غير متوفر أو قد تحتاج لتحديث Docker."; fi

# Compose file validation
if [[ ! -f "$COMPOSE_FILE" ]]; then err "الملف غير موجود: $COMPOSE_FILE"; exit 1; fi
if ! docker compose -f "$COMPOSE_FILE" config >/dev/null; then err "خطأ في بناء ملف الـ compose."; exit 1; fi
ok "docker-compose.rag.yml is valid."

# Load services dynamically
SERVICES=()
while IFS= read -r svc; do [[ -n "$svc" ]] && SERVICES+=("$svc"); done < <(docker compose -f "$COMPOSE_FILE" config --services 2>/dev/null || true)

# Build a lookup associative array for validation
declare -A SERVICE_MAP=()
for s in "${SERVICES[@]}"; do SERVICE_MAP["$s"]=1; done

# .env handling
if [[ ! -f "$ENV_FILE" ]]; then
  warn ".env غير موجود — سيتم توليده."
  cat <<EOF > "$ENV_FILE"
LLM_PROVIDER=phi_local
PHI3_URL=http://phi3:8082
RAG_ENGINE_URL=http://rag_engine:8081
OPENAI_API_KEY=
GROQ_API_KEY=
ANTHROPIC_API_KEY=
NEO4J_URI=
QDRANT_URL=http://qdrant:6333
EOF
  ok "تم إنشاء .env."
else
  ok ".env موجود."
fi

EMPTY_KEYS=()
for k in OPENAI_API_KEY GROQ_API_KEY ANTHROPIC_API_KEY; do
  if ! grep -q "^${k}=" "$ENV_FILE"; then EMPTY_KEYS+=("$k (مفقود)");
  elif grep -q "^${k}=$" "$ENV_FILE"; then EMPTY_KEYS+=("$k (فارغ)" ); fi; done
[[ ${#EMPTY_KEYS[@]} -gt 0 ]] && warn "مفاتيح API التالية فارغة/ناقصة: ${EMPTY_KEYS[*]}"

# Local IP detection
detect_ip() {
  local ip=""; if command -v ipconfig >/dev/null 2>&1; then ip=$(ipconfig getifaddr en0 2>/dev/null || true); fi
  if [[ -z "$ip" ]] && command -v hostname >/dev/null 2>&1; then ip=$(hostname -I 2>/dev/null | awk '{print $1}'); fi
  echo "$ip"; }
LOCAL_IP=$(detect_ip)
info "🌐 Local IP (iPhone): ${LOCAL_IP:-unknown}"

# Port check (optional if lsof exists)
check_port() {
  local port="$1"; if command -v lsof >/dev/null 2>&1; then
    if lsof -iTCP -sTCP:LISTEN -n 2>/dev/null | grep -q ":$port "; then warn "المنفذ $port مستخدم حالياً."; fi
  else warn "lsof غير متوفر — تخطي فحص المنفذ $port."; fi }
for p in 8501 3000 8081 8082 6333; do check_port "$p"; done

# Determine target services (selective run/restart)
TARGET_SERVICES=("${SERVICES[@]}")
if [[ ("$COMMAND" == "up" || "$COMMAND" == "restart") && ${#ARGS[@]} -gt 0 ]]; then
  TARGET_SERVICES=()
  for a in "${ARGS[@]}"; do
    if [[ -n "${SERVICE_MAP[$a]:-}" ]]; then TARGET_SERVICES+=("$a"); else warn "تجاهل خدمة غير معروفة: $a"; fi
  done
  if [[ ${#TARGET_SERVICES[@]} -eq 0 ]]; then
    warn "لم يتم تمرير خدمات صحيحة — سيتم تشغيل جميع الخدمات."; TARGET_SERVICES=("${SERVICES[@]}"); fi
fi

list_services_pretty() { for s in "${TARGET_SERVICES[@]}"; do printf " - %s\n" "$s"; done; }

compose_up() {
  local build_flag="--build"; [[ $NO_BUILD -eq 1 ]] && build_flag="";
  [[ $DO_PULL -eq 1 ]] && info "🔄 Pulling latest images..." && docker compose -f "$COMPOSE_FILE" pull
  info "🚀 Starting services:"; list_services_pretty
  docker compose -f "$COMPOSE_FILE" up $build_flag -d "${TARGET_SERVICES[@]}"
  ok "Services started."; }

compose_down() { info "🛑 Stopping stack..."; docker compose -f "$COMPOSE_FILE" down; ok "Stack down."; }
compose_restart() { info "🔁 Restarting services:"; list_services_pretty; docker compose -f "$COMPOSE_FILE" restart "${TARGET_SERVICES[@]}"; ok "Restart done."; }
compose_ps() { docker compose -f "$COMPOSE_FILE" ps; }
compose_logs() { if [[ ${#ARGS[@]} -gt 0 ]]; then docker compose -f "$COMPOSE_FILE" logs -f "${ARGS[0]}"; else docker compose -f "$COMPOSE_FILE" logs -f --tail=100; fi }
show_services() { printf "الخدمات المتاحة:\n"; for s in "${SERVICES[@]}"; do echo " - $s"; done }

run_health() {
  if [[ -f "$HEALTH_SCRIPT" ]]; then
    if ! command -v python3 >/dev/null 2>&1; then warn "python3 غير متوفر — تخطي فحص الصحة."; return 0; fi
    info "🩺 Running health check..."; python3 "$HEALTH_SCRIPT" || warn "Health check returned non-zero."
  else warn "لم يتم العثور على سكربت الصحة: $HEALTH_SCRIPT"; fi }

auto_fix() {
  info "🛠 Auto-fix routine..."; local failed=()
  while IFS= read -r line; do [[ -n "$line" ]] && failed+=("$line"); done < <(docker compose -f "$COMPOSE_FILE" ps --status=stopped --services 2>/dev/null || true)
  while IFS= read -r line; do [[ -n "$line" ]] && failed+=("$line"); done < <(docker ps --format '{{.Names}} {{.Status}}' | awk '/(unhealthy)/{print $1}' || true)
  if [[ ${#failed[@]} -eq 0 ]]; then ok "لا توجد خدمات تحتاج إصلاح."; return; fi
  warn "محاولة إعادة تشغيل: ${failed[*]}"; docker compose -f "$COMPOSE_FILE" restart "${failed[@]}" || true }

case "$COMMAND" in
  up) compose_up; sleep 5; run_health; [[ $AUTO_FIX -eq 1 ]] && auto_fix ;;
  down) compose_down ;;
  restart) compose_restart; run_health ;;
  ps) compose_ps; exit 0 ;;
  logs) compose_logs; exit 0 ;;
  health) run_health; exit 0 ;;
  services) show_services; exit 0 ;;
  *) err "أمر غير معروف: $COMMAND"; usage; exit 1 ;;
esac

# Access points
echo ""; echo "========================================="; echo "🎉 STACK IS RUNNING – ACCESS POINTS"; echo "========================================="
has_service() { local n="$1"; for s in "${TARGET_SERVICES[@]}"; do [[ "$s" == "$n" ]] && return 0; done; return 1; }
if has_service web_ui || has_service streamlit; then
  echo "📌 Streamlit Chat UI:"; echo "   http://localhost:8501"; [[ -n "$LOCAL_IP" ]] && echo "   📱 iPhone: http://${LOCAL_IP}:8501"; echo ""; fi
has_service gateway && echo "📌 Gateway:        http://localhost:3000"
has_service rag_engine && echo "📌 RAG Engine:     http://localhost:8081"
has_service phi3 && echo "📌 Phi-3 Runner:   http://localhost:8082"
has_service qdrant && echo "📌 Qdrant UI:      http://localhost:6333"
[[ -n "
${CODESPACE_NAME:-}" ]] && echo "\n📌 Codespaces: استخدم منافذ الفوروارد في واجهة Codespaces."
echo "========================================="; echo "🟢 النظام يعمل بنجاح"; echo "========================================="

exit 0

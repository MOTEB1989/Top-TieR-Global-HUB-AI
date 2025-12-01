#!/usr/bin/env bash
set -euo pipefail

# =========[ Top-Tier Global HUB AI – Codespaces Runner (No Docker) ]============
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${REPO_ROOT}/logs"
mkdir -p "$LOG_DIR"

info()    { echo -e "\033[1;36m$*\033[0m"; }
warn()    { echo -e "\033[1;33m$*\033[0m"; }
error()   { echo -e "\033[1;31m$*\033[0m"; }
success() { echo -e "\033[1;32m$*\033[0m"; }

die() { error "$*"; exit 1; }

# 1) تحقّق من وجود Python
if ! command -v python3 >/dev/null 2>&1; then
  die "Python3 غير متوفر في هذه البيئة."
fi
success "✅ Python3 detected."

cd "$REPO_ROOT" || die "Cannot cd to repo root"

# 2) تثبيت المتطلبات (محلياً في Codespaces)
info "📦 Installing Python dependencies (this may take a bit)..."
python3 -m pip install --user --upgrade pip >/dev/null 2>&1 || true
python3 -m pip install --user -r requirements.txt >/dev/null 2>&1 || true
python3 -m pip install --user fastapi uvicorn[standard] streamlit qdrant-client requests >/dev/null 2>&1 || true
success "✅ Dependencies installed (best-effort)."

# 3) ضبط مسارات Python (للاستخدام مع --user)
export PATH="$HOME/.local/bin:$PATH"

# 4) دالة لتشغيل خدمة في الخلفية مع لوج
run_service() {
  local name="$1"
  shift
  local log_file="${LOG_DIR}/${name}.log"
  info "🚀 Starting service: $name"
  nohup "$@" >"$log_file" 2>&1 &
  local pid=$!
  success "✅ $name started with PID $pid (logs: $log_file)"
}

# 5) تشغيل الخدمات (بدون Docker)
info "🏗 Starting services WITHOUT Docker (Codespaces mode)..."

# RAG Engine (FastAPI) على 8081
run_service "rag_engine" python3 -m uvicorn services.rag_engine.app:app --host 0.0.0.0 --port 8081

# Phi-3 Local Stub على 8082
run_service "phi3" python3 -m uvicorn services.phi3.app:app --host 0.0.0.0 --port 8082

# Gateway على 3000
run_service "gateway" python3 -m uvicorn services.gateway.app:app --host 0.0.0.0 --port 3000

# Web UI (Streamlit) على 8501
run_service "web_ui" streamlit run services/web_ui/app.py --server.address=0.0.0.0 --server.port=8501

# 6) محاولة تحديد رابط Codespaces
CSP_NAME="${CODESPACE_NAME:-}"
CSP_DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-githubpreview.dev}"

echo ""
echo "========================================="
success "🎉 STACK IS RUNNING IN CODESPACES (NO DOCKER)"
echo "========================================="

if [[ -n "$CSP_NAME" ]]; then
  echo "📌 Streamlit Chat UI:"
  echo "   https://${CSP_NAME}-8501.${CSP_DOMAIN}"
  echo ""
  echo "📌 Gateway:"
  echo "   https://${CSP_NAME}-3000.${CSP_DOMAIN}"
  echo ""
  echo "📌 RAG Engine:"
  echo "   https://${CSP_NAME}-8081.${CSP_DOMAIN}"
  echo ""
  echo "📌 Phi-3 Stub:"
  echo "   https://${CSP_NAME}-8082.${CSP_DOMAIN}"
else
  echo "📌 Streamlit Chat UI on port 8501 (check Ports tab in Codespaces)."
fi

echo ""
echo "Logs directory: $LOG_DIR"
echo "Use: tail -f logs/<service>.log لمتابعة أي خدمة."
echo "========================================="
success "🟢 النظام يعمل الآن داخل Codespaces بدون Docker"
echo "========================================="

End of file.

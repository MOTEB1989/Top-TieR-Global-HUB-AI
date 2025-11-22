#!/bin/bash
set -euo pipefail

echo "🤖 تشغيل كامل الستاك (Docker + واجهة المحادثة)..."

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

COMPOSE_FILE="${REPO_ROOT}/docker-compose.yml"

# 1) التحقق من Docker
if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Docker غير مثبت في هذا الـ Codespace / الجهاز."
  echo "شغّل نسخة بدون Docker (مثلاً run_everything.sh أو تشغيل Streamlit مباشرة)."
  exit 1
fi

# 2) التحقق من ملف compose
if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "❌ لم يتم العثور على docker-compose.yml في: $COMPOSE_FILE"
  exit 1
fi

echo "🔍 التحقق من ملف docker-compose.yml..."
docker compose -f "$COMPOSE_FILE" config >/dev/null
echo "✅ ملف docker-compose.yml صالح."

# 3) تشغيل الخدمات
echo "🚀 تشغيل الخدمات عبر Docker Compose..."
docker compose -f "$COMPOSE_FILE" up -d

echo "⏳ الانتظار 8 ثوانٍ حتى تجهز الخدمات..."
sleep 8

# 4) تشغيل Streamlit Chat UI
echo "🚀 تشغيل واجهة المحادثة (Streamlit)..."
# إيقاف أي تشغيل سابق لعدم تضارب البورت
if pgrep -f "streamlit run src/web/app.py" >/dev/null 2>&1; then
  pkill -f "streamlit run src/web/app.py" || true
fi

streamlit run src/web/app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 &
STREAMLIT_PID=$!

sleep 3

# 5) طباعة الروابط
LOCAL_IP=""
if command -v ipconfig >/dev/null 2>&1; then
  LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || true)
elif command -v hostname >/dev/null 2>&1; then
  LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
fi

echo ""
echo "========================================="
echo "🎉 الستاك يعمل الآن"
echo "========================================="
echo "📌 Gateway (من داخل الـ Codespace):"
echo "   http://localhost:3000"
echo ""
echo "📌 واجهة المحادثة (من داخل الـ Codespace):"
echo "   http://localhost:8501"
if [[ -n "${CODESPACE_NAME:-}" ]]; then
  echo ""
  echo "🌐 رابط Codespaces (للمتصفح من الآيفون):"
  echo "   https://${CODESPACE_NAME}-8501.app.github.dev"
fi
if [[ -n "$LOCAL_IP" ]]; then
  echo ""
  echo "📱 من شبكة محلية (لو كنت على لابتوب):"
  echo "   http://${LOCAL_IP}:8501"
fi
echo "========================================="
echo "🔁 لإيقاف Streamlit يدويًا:"
echo "   kill ${STREAMLIT_PID}"
echo "========================================="

wait "${STREAMLIT_PID}"

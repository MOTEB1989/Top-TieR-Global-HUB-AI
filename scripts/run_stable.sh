#!/bin/bash
# Stable Stack Runner (SearXNG + Qdrant + Phi-3 + Streamlit)

set -e

echo "🚀 تشغيل الستاك المستقر..."

# 1. Docker Compose
docker compose up -d --build

# 2. انتظار الخدمات (30 ثانية للتهيئة الأولى)
sleep 30

# 3. قتل أي تشغيل سابق لستريمليت
if pgrep -f "streamlit" >/dev/null; then
    echo "⚠️  إيقاف نسخة سابقة من Streamlit..."
    pkill -f "streamlit"
    sleep 2
fi

# 4. تشغيل Streamlit في الخلفية
echo "🎨 تشغيل Streamlit..."
nohup streamlit run src/web/app.py \
    --server.address 0.0.0.0 \
    --server.port 8501 \
    > /tmp/streamlit.log 2>&1 &

sleep 3

# 5. التحقق من التشغيل
if pgrep -f "streamlit" >/dev/null; then
    echo "✅ Streamlit يعمل بنجاح على المنفذ 8501"
else
    echo "❌ فشل تشغيل Streamlit — تحقق من /tmp/streamlit.log"
fi

# 6. طباعة روابط الوصول
echo ""
echo "📱 افتح على الآيفون:"
echo "   http://$(hostname -I | awk '{print $1}'):8501"

echo ""
echo "💻 للدخول من داخل Codespaces:"
echo "   افتح نافذة Ports → أضف المنفذ 8501 → Open in Browser"


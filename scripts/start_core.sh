#!/bin/bash
# تشغيل سريع لخدمة Core

echo "🚀 بناء وتشغيل خدمة Core..."

# بناء الخدمة
docker compose up -d --build core

echo "⏳ انتظار 10 ثواني..."
sleep 10

# فحص الحالة
echo "📊 فحص حالة الخدمة..."
docker compose ps core

echo ""
echo "🌐 روابط الوصول:"
echo "   → http://localhost:8000"
echo "   → http://localhost:8000/health"
echo ""
echo "🔍 اختبار الخدمة:"
curl -s http://localhost:8000/health | jq . || echo "⚠️ الخدمة ليست جاهزة بعد"

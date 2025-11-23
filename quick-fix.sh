#!/bin/bash
# Quick Deploy Test Script
# سكربت اختبار النشر السريع

set -e

echo "🔧 إصلاح بنية المشروع..."

# إنشاء src إذا لم يكن موجوداً
mkdir -p src/providers

# نقل الملفات إذا كانت في الجذر
[ -f index.ts ] && mv index.ts src/ 2>/dev/null || true
[ -f ai.ts ] && mv ai.ts src/providers/ 2>/dev/null || true  
[ -f openai.ts ] && mv openai.ts src/providers/ 2>/dev/null || true

echo "✅ البنية جاهزة"
echo ""
echo "📦 اختبار البناء المحلي..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ البناء المحلي نجح!"
    echo ""
    echo "🐳 الآن يمكنك:"
    echo "   1. بناء Docker: docker build -t lexcode-api ."
    echo "   2. أو النشر: railway up / render deploy"
else
    echo "❌ البناء المحلي فشل"
    exit 1
fi

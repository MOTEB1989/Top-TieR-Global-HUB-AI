#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

#############################################################################
# force_fix_railway.sh - Force fix Railway deployment issues
#
# Purpose:
#   Apply critical fixes for Railway deployment configuration
#
# Usage:
#   ./scripts/force_fix_railway.sh
#############################################################################

echo "=========================================="
echo "🔧 دفع الإصلاحات الصحيحة لـ Railway"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

# التأكد من أن الملفات صحيحة
echo "✅ التحقق من tsconfig.json..."
grep -q '"src/\*\*/\*"' tsconfig.json && echo "  ✅ include صحيح" || echo "  ❌ include خاطئ"
grep -q '"rootDir": "src"' tsconfig.json && echo "  ✅ rootDir موجود" || echo "  ❌ rootDir مفقود"

echo ""
echo "✅ التحقق من Dockerfile..."
grep -q 'COPY src/ ./src/' Dockerfile && echo "  ✅ COPY src/ صحيح" || echo "  ❌ COPY خاطئ"
grep -q 'COPY tsconfig.json' Dockerfile && echo "  ✅ COPY tsconfig صحيح" || echo "  ❌ COPY tsconfig مفقود"

echo ""
echo "📦 إضافة وحفظ التغييرات..."
git add tsconfig.json Dockerfile
git commit -m "fix(railway): CRITICAL - update tsconfig and Dockerfile for TS18003

Changes:
- tsconfig.json: include from 'src' to 'src/**/*'
- tsconfig.json: add rootDir: 'src'
- Dockerfile: explicit COPY src/ ./src/
- Dockerfile: explicit COPY tsconfig.json

This MUST fix Railway TS18003 error" || echo "لا توجد تغييرات جديدة"

echo ""
echo "🚀 دفع إلى GitHub..."
git push origin main

echo ""
echo "✅ تم! راقب Railway الآن"

#!/bin/bash
# Cleanup duplicate files
# تنظيف الملفات المكررة

set -e

echo "🧹 تنظيف الملفات المكررة..."

# حذف الملفات القديمة من src/
rm -f src/ai.ts src/openai.ts 2>/dev/null || true

echo "✅ تم التنظيف"
echo ""
echo "📁 البنية الحالية:"
echo "src/"
echo "├── index.ts"
echo "└── providers/"
echo "    ├── ai.ts"
echo "    └── openai.ts"
echo ""

ls -R src/

#!/bin/bash
# حذف الملفات المكررة في src/
echo "🧹 حذف الملفات المكررة..."

cd /workspaces/Top-TieR-Global-HUB-AI

# حذف الملفات القديمة
if [ -f "src/ai.ts" ]; then
    rm -f src/ai.ts
    echo "✅ حذف src/ai.ts"
fi

if [ -f "src/openai.ts" ]; then
    rm -f src/openai.ts
    echo "✅ حذف src/openai.ts"
fi

echo ""
echo "📁 البنية النهائية:"
echo "src/"
echo "├── index.ts"
echo "└── providers/"
echo "    ├── ai.ts"
echo "    └── openai.ts"
echo ""

# عرض البنية الفعلية
find src -type f -name "*.ts" | sort

echo ""
echo "✅ تم التنظيف بنجاح!"

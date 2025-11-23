#!/usr/bin/env bash
set -e

echo "=========================================="
echo "🐳 اختبار بناء Docker"
echo "=========================================="
echo ""

# 1. التحقق من وجود الملفات المطلوبة
echo "1️⃣ التحقق من الملفات..."
echo ""

required_files=(
    "package.json"
    "tsconfig.json"
    "Dockerfile"
    "src/index.ts"
    "src/providers/ai.ts"
    "src/providers/openai.ts"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (مفقود)"
        exit 1
    fi
done

echo ""
echo "2️⃣ عرض محتويات src/..."
echo ""
find src -type f -name "*.ts" | sort

echo ""
echo "3️⃣ اختبار بناء TypeScript محلياً..."
echo ""
npm run build

if [[ -d "dist" ]] && [[ -f "dist/index.js" ]]; then
    echo "  ✅ dist/index.js موجود"
    echo ""
    echo "  📁 محتويات dist/:"
    ls -la dist/
else
    echo "  ❌ فشل إنتاج dist/"
    exit 1
fi

echo ""
echo "4️⃣ اختبار بناء Docker..."
echo ""
docker build -t lexcode-api-test:latest . 2>&1 | tail -30

if [[ $? -eq 0 ]]; then
    echo ""
    echo "=========================================="
    echo "✅ البناء نجح بالكامل!"
    echo "=========================================="
    echo ""
    echo "📊 معلومات الصورة:"
    docker images lexcode-api-test:latest
    echo ""
    echo "🚀 لتشغيل الحاوية:"
    echo "   docker run -p 3000:3000 --env-file .env lexcode-api-test:latest"
else
    echo ""
    echo "=========================================="
    echo "❌ فشل بناء Docker"
    echo "=========================================="
    exit 1
fi

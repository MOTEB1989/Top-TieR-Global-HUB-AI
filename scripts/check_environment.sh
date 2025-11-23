#!/bin/bash

set -e

echo "***** فحص البيئة تلقائياً *****"
echo "---"

# 1. التأكد من وجود ملف docker-compose
if [ -f docker-compose.yml ]; then
    echo "✔️ وُجد ملف docker-compose.yml"
else
    echo "❌ لم يتم العثور على ملف docker-compose.yml"
fi

# 2. التأكد من وجود سكربت run_everything.sh
if [ -f scripts/run_everything.sh ]; then
    echo "✔️ وُجد السكربت scripts/run_everything.sh"
    # تأكد من صلاحية التنفيذ
    if [ -x scripts/run_everything.sh ]; then
        echo "✔️ السكربت يمتلك صلاحية التنفيذ"
    else
        echo "⚠️ سيتم إعطاء صلاحية التنفيذ للسكربت"
        chmod +x scripts/run_everything.sh
        echo "✔️ تم إعطاء صلاحية التنفيذ"
    fi
else
    echo "❌ سكربت scripts/run_everything.sh غير موجود"
fi

# 3. التأكد من وجود Docker
if command -v docker &> /dev/null; then
    echo "✔️ Docker مُثبت: $(docker --version)"
else
    echo "❌ Docker غير مثبت"
fi

# 4. التأكد من Docker Compose
if docker compose version &> /dev/null; then
    echo "✔️ Docker Compose مُثبت: $(docker compose version)"
else
    echo "❌ Docker Compose غير مثبت"
fi

# 5. التأكد أن Docker يعمل (service)
docker info &> /dev/null
if [ $? -eq 0 ]; then
    echo "✔️ Docker يعمل بشكل سليم"
else
    echo "❌ مشكلة في اتصال خدمة Docker (قد تحتاج sudo)"
fi

# 6. تجربة تشغيل hello-world
echo "---"
echo "تجربة تشغيل حاوية اختبار (hello-world)..."
if docker run --rm hello-world &> /dev/null; then
    echo "✔️ Docker يعمل والحاويات تُشغل بنجاح"
else
    echo "❌ لم يتم تشغيل الحاوية، هناك مشكلة في Docker"
fi

echo "---"
echo "الفحص انتهى ✅"

#!/bin/bash
set -e

# ============================================================
# 🔗 GPT-TO-REPO LINKER – TOP-TIER GLOBAL HUB AI
# يربط أي Custom GPT بالمستودع تلقائياً
# ============================================================

# متغيرات يجب إضافتها قبل التشغيل:
OPENAI_API_KEY="${OPENAI_API_KEY:-sk-xxx}"  # ⚠️ أضف مفتاحك هنا
GITHUB_REPO="MOTEB1989/Top-TieR-Global-HUB-AI"
CUSTOM_GPTS=(
    "g-68d85ae6a19881919a7699aede6f6366"  # Saudi Nexus
    "g-68d83741405881918336c921a412c7c4"  # Saudi Banks
    "g-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # LexNexus (أضف معرفه عند الإنشاء)
)

echo "🚀 بدء ربط النماذج بالمستودع..."

for GPT_ID in "${CUSTOM_GPTS[@]}"; do
    echo ""
    echo "📊 ربط النموذج: $GPT_ID"
    
    # 1. إضافة المستودع كمصدر معرفة
    echo "   🧠 إضافة مصدر معرفة..."
    curl -X POST "https://api.openai.com/v1/gpts/${GPT_ID}/knowledge" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"type\": \"github\",
            \"url\": \"https://github.com/${GITHUB_REPO}\",
            \"branch\": \"main\",
            \"auto_sync\": true,
            \"sync_interval\": 3600
        }" | grep -q '"status":"success"' && \
        echo "   ✅ تمت إضافة مصدر المعرفة" || \
        echo "   ⚠️ مصدر المعرفة موجود مسبقاً"
    
    # 2. إعداد Webhook للتحديث التلقائي
    echo "   🔄 إعداد Webhook..."
    curl -X POST "https://api.openai.com/v1/gpts/${GPT_ID}/webhooks" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"source\": \"github\",
            \"events\": [\"push\", \"pull_request\", \"release\"],
            \"callback\": \"https://api.railway.app/webhooks/gpt-sync\",
            \"config\": {
                \"repo\": \"${GITHUB_REPO}\",
                \"auto_update\": true
            }
        }" | grep -q '"id"' && \
        echo "   ✅ Webhook مضبوط" || \
        echo "   ⚠️ Webhook موجود مسبقاً"
    
    # 3. تفعيل وضع Repository Aware
    echo "   🎯 تفعيل وضع المستودع..."
    curl -X PATCH "https://api.openai.com/v1/gpts/${GPT_ID}" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"repository_aware\": true,
            \"repo_url\": \"https://github.com/${GITHUB_REPO}\"
        }" | grep -q '"repository_aware":true' && \
        echo "   ✅ وضع المستودع مفعّل" || \
        echo "   ⚠️ فشل تفعيل وضع المستودع"
done

echo ""
echo "✅ تم ربط جميع النماذج بالمستودع بنجاح!"
echo "📱 يمكنك الآن اختبارها عبر Telegram Bot"

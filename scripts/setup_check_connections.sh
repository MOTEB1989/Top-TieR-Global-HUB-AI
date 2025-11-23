#!/usr/bin/env bash
# Quick setup and test script for check_connections.sh

set -euo pipefail

echo "🚀 إعداد سريع لسكربت check_connections.sh"
echo "============================================="
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if script exists
if [[ ! -f "scripts/check_connections.sh" ]]; then
    echo -e "${RED}❌ ملف scripts/check_connections.sh غير موجود${NC}"
    exit 1
fi

# Make executable
chmod +x scripts/check_connections.sh
echo -e "${GREEN}✅ تم جعل السكربت قابلاً للتنفيذ${NC}"

# Check .env file
if [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}⚠️  ملف .env غير موجود، سيتم نسخه من .env.example${NC}"
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        echo -e "${GREEN}✅ تم نسخ .env.example إلى .env${NC}"
        echo -e "${YELLOW}📝 يُرجى تحرير .env وإضافة المفاتيح الحقيقية${NC}"
    else
        echo -e "${RED}❌ ملف .env.example غير موجود أيضاً${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ ملف .env موجود${NC}"
fi

# Create reports directory
mkdir -p reports
echo -e "${GREEN}✅ تم إنشاء مجلد reports${NC}"

echo
echo "============================================="
echo "🧪 تشغيل سكربت الفحص..."
echo "============================================="
echo

# Run the script
export API_PORT=3000
./scripts/check_connections.sh

echo
echo "============================================="
echo "📊 التقرير متاح في: reports/check_connections.json"
echo "============================================="
echo

# Display report if jq is available
if command -v jq >/dev/null 2>&1; then
    echo "عرض التقرير:"
    jq . reports/check_connections.json
else
    echo -e "${YELLOW}⚠️  jq غير مثبت، عرض التقرير الخام:${NC}"
    cat reports/check_connections.json
fi

echo
echo "============================================="
echo "✅ الإعداد والفحص مكتمل"
echo "============================================="
echo
echo "الخطوات التالية:"
echo "1. حرّر ملف .env وأضف المفاتيح الحقيقية"
echo "2. شغّل: source .env"
echo "3. شغّل: ./scripts/check_connections.sh"
echo "4. راجع التقرير في: reports/check_connections.json"
echo
echo "لإضافة أسرار إلى GitHub:"
echo "  gh secret set TELEGRAM_BOT_TOKEN --body \"your_token\""
echo "  gh secret set TELEGRAM_CHAT_ID --body \"your_chat_id\""
echo "  gh secret set OPENAI_API_KEY --body \"your_api_key\""
echo

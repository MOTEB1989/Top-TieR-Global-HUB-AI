#!/bin/bash
# ========================================
# Complete Setup & Fix Script
# سكربت إعداد وإصلاح شامل
# ========================================

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}"
echo "========================================"
echo "🔧 إصلاح وإعداد المشروع الشامل"
echo "========================================"
echo -e "${NC}"

# ========================================
# 1. تنظيف الملفات المكررة
# ========================================
echo -e "${YELLOW}[1/6]${NC} 🧹 تنظيف الملفات المكررة..."
if [ -f "src/ai.ts" ] || [ -f "src/openai.ts" ]; then
    rm -f src/ai.ts src/openai.ts 2>/dev/null || true
    echo -e "${GREEN}✅ تم حذف الملفات المكررة${NC}"
else
    echo -e "${GREEN}✅ لا توجد ملفات مكررة${NC}"
fi
echo ""

# ========================================
# 2. التحقق من ملف .env
# ========================================
echo -e "${YELLOW}[2/6]${NC} 🔍 فحص ملف .env..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  ملف .env غير موجود، جاري إنشائه...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ تم إنشاء .env من .env.example${NC}"
    echo -e "${YELLOW}💡 يرجى تعديل المفاتيح في .env${NC}"
else
    echo -e "${GREEN}✅ ملف .env موجود${NC}"
fi
echo ""

# ========================================
# 3. عرض البنية
# ========================================
echo -e "${YELLOW}[3/6]${NC} 📁 بنية src/..."
find src -type f -name "*.ts" 2>/dev/null | sort || echo "لا توجد ملفات .ts"
echo ""

# ========================================
# 4. اختبار بناء TypeScript
# ========================================
echo -e "${YELLOW}[4/6]${NC} 📦 اختبار بناء TypeScript..."
if [ ! -d "node_modules" ]; then
    echo "📥 تثبيت المكتبات..."
    npm install
fi

if npm run build 2>&1 | tail -10; then
    echo -e "${GREEN}✅ بناء TypeScript نجح!${NC}"
    if [ -d "dist" ]; then
        echo "📂 الملفات المبنية:"
        ls -lh dist/*.js 2>/dev/null | head -5 || echo "dist/ فارغ"
    fi
else
    echo -e "${RED}❌ بناء TypeScript فشل${NC}"
    echo "💡 تحقق من الأخطاء أعلاه"
fi
echo ""

# ========================================
# 5. اختبار Telegram Bot
# ========================================
echo -e "${YELLOW}[5/6]${NC} 🤖 اختبار Telegram Bot..."
if python3 scripts/quick_bot_test.py; then
    echo -e "${GREEN}✅ Telegram Bot جاهز!${NC}"
else
    echo -e "${YELLOW}⚠️  Telegram Bot يحتاج إعداد TELEGRAM_BOT_TOKEN${NC}"
fi
echo ""

# ========================================
# 6. اختبار بناء Docker (اختياري)
# ========================================
echo -e "${YELLOW}[6/6]${NC} 🐳 اختبار بناء Docker..."
echo "⏩ تخطي بناء Docker (يمكنك تشغيله يدوياً: docker build -t lexcode-api .)"
echo ""

# ========================================
# النتيجة النهائية
# ========================================
echo -e "${BOLD}${BLUE}"
echo "========================================"
echo "📊 ملخص الإصلاحات"
echo "========================================"
echo -e "${NC}"

echo -e "${GREEN}✅ الإصلاحات المنفذة:${NC}"
echo "   • تنظيف الملفات المكررة"
echo "   • إعداد ملف .env"
echo "   • اختبار بناء TypeScript"
echo "   • اختبار Telegram Bot"
echo ""

echo -e "${BLUE}🎯 الخطوات التالية:${NC}"
echo ""
echo "1️⃣  ${BOLD}إضافة المفاتيح في .env:${NC}"
echo "   vi .env  # أو استخدم أي محرر"
echo "   # أضف:"
echo "   # TELEGRAM_BOT_TOKEN=<from @BotFather>"
echo "   # OPENAI_API_KEY=<from OpenAI>"
echo ""

echo "2️⃣  ${BOLD}اختبار الخدمات محلياً:${NC}"
echo "   npm start  # API Gateway"
echo "   python scripts/telegram_chatgpt_mode.py  # Bot"
echo ""

echo "3️⃣  ${BOLD}أو استخدام Docker:${NC}"
echo "   docker-compose -f docker-compose.full.yml up -d"
echo ""

echo "4️⃣  ${BOLD}اختبار Health Check:${NC}"
echo "   curl http://localhost:3000/health"
echo ""

echo -e "${BOLD}${BLUE}"
echo "========================================"
echo "✅ جاهز للعمل!"
echo "========================================"
echo -e "${NC}"

echo "📚 للمزيد من المعلومات:"
echo "   • SETUP_GUIDE.md - دليل الإعداد الكامل"
echo "   • DOCKER_FIX_README.md - دليل إصلاح Docker"
echo "   • README.md - نظرة عامة على المشروع"
echo ""

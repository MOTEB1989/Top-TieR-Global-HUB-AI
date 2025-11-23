#!/usr/bin/env bash
# Validation script to check all check_connections files

set -euo pipefail

echo "🔍 التحقق من ملفات check_connections..."
echo "=================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0
warnings=0

# Check if files exist
echo -e "\n1️⃣ فحص وجود الملفات:"
files=(
    "scripts/check_connections.sh"
    "scripts/setup_check_connections.sh"
    "scripts/create_pr_for_check_connections.sh"
    "scripts/GIT_READY_COMMANDS.sh"
    "docs/CHECK_CONNECTIONS_GUIDE.md"
    "docs/QUICK_START_COMMANDS.md"
    "CHECK_CONNECTIONS_README.md"
    "CHECK_CONNECTIONS_QUICKREF.md"
    "IMPLEMENTATION_SUMMARY.md"
    ".env.example"
)

for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "  ${GREEN}✅${NC} $file"
    else
        echo -e "  ${RED}❌${NC} $file (مفقود)"
        ((errors++))
    fi
done

# Check if scripts are executable
echo -e "\n2️⃣ فحص صلاحيات التنفيذ:"
scripts=(
    "scripts/check_connections.sh"
    "scripts/setup_check_connections.sh"
    "scripts/create_pr_for_check_connections.sh"
    "scripts/GIT_READY_COMMANDS.sh"
)

for script in "${scripts[@]}"; do
    if [[ -f "$script" ]]; then
        if [[ -x "$script" ]]; then
            echo -e "  ${GREEN}✅${NC} $script (قابل للتنفيذ)"
        else
            echo -e "  ${YELLOW}⚠️${NC}  $script (غير قابل للتنفيذ)"
            chmod +x "$script" 2>/dev/null && echo "     → تم إصلاحه" || ((warnings++))
        fi
    fi
done

# Check for bash syntax errors
echo -e "\n3️⃣ فحص أخطاء Syntax في السكربتات:"
for script in "${scripts[@]}"; do
    if [[ -f "$script" ]]; then
        if bash -n "$script" 2>/dev/null; then
            echo -e "  ${GREEN}✅${NC} $script (لا أخطاء syntax)"
        else
            echo -e "  ${RED}❌${NC} $script (يوجد أخطاء syntax)"
            ((errors++))
        fi
    fi
done

# Check if required tools are available
echo -e "\n4️⃣ فحص الأدوات المطلوبة:"
tools=("curl" "grep" "sed" "awk")
optional_tools=("docker" "jq" "gh")

for tool in "${tools[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} $tool"
    else
        echo -e "  ${RED}❌${NC} $tool (مفقود - مطلوب)"
        ((errors++))
    fi
done

echo -e "\n5️⃣ فحص الأدوات الاختيارية:"
for tool in "${optional_tools[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} $tool"
    else
        echo -e "  ${YELLOW}⚠️${NC}  $tool (مفقود - اختياري)"
        ((warnings++))
    fi
done

# Check .env.example has all required variables
echo -e "\n6️⃣ فحص المتغيرات في .env.example:"
required_vars=(
    "TELEGRAM_BOT_TOKEN"
    "TELEGRAM_CHAT_ID"
    "OPENAI_API_KEY"
    "GROQ_API_KEY"
    "ANTHROPIC_API_KEY"
    "DB_URL"
    "REDIS_URL"
    "NEO4J_URI"
    "NEO4J_AUTH"
    "API_PORT"
)

if [[ -f ".env.example" ]]; then
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env.example || grep -q "^# ${var}=" .env.example; then
            echo -e "  ${GREEN}✅${NC} $var"
        else
            echo -e "  ${YELLOW}⚠️${NC}  $var (غير موجود في .env.example)"
            ((warnings++))
        fi
    done
fi

# Test dry run (without secrets)
echo -e "\n7️⃣ اختبار تشغيل جاف (بدون أسرار):"
if [[ -f "scripts/check_connections.sh" ]]; then
    if API_PORT=3000 bash scripts/check_connections.sh >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} السكربت يعمل بدون أخطاء"
        if [[ -f "reports/check_connections.json" ]]; then
            echo -e "  ${GREEN}✅${NC} تم توليد التقرير"
            # Validate JSON
            if python3 -m json.tool reports/check_connections.json >/dev/null 2>&1; then
                echo -e "  ${GREEN}✅${NC} التقرير JSON صالح"
            else
                echo -e "  ${RED}❌${NC} التقرير JSON غير صالح"
                ((errors++))
            fi
        else
            echo -e "  ${YELLOW}⚠️${NC}  لم يتم توليد التقرير"
            ((warnings++))
        fi
    else
        echo -e "  ${RED}❌${NC} السكربت فشل في التشغيل"
        ((errors++))
    fi
fi

# Summary
echo -e "\n=================================================="
echo "📊 ملخص التحقق:"
echo "=================================================="
if [[ $errors -eq 0 ]]; then
    echo -e "${GREEN}✅ لا توجد أخطاء${NC}"
else
    echo -e "${RED}❌ عدد الأخطاء: $errors${NC}"
fi

if [[ $warnings -eq 0 ]]; then
    echo -e "${GREEN}✅ لا توجد تحذيرات${NC}"
else
    echo -e "${YELLOW}⚠️  عدد التحذيرات: $warnings${NC}"
fi
echo "=================================================="

if [[ $errors -eq 0 ]]; then
    echo -e "${GREEN}🎉 جميع الفحوصات نجحت!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  يوجد أخطاء تحتاج إصلاح${NC}"
    exit 1
fi

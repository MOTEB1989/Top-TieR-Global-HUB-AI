#!/usr/bin/env bash
set -e

echo "=========================================="
echo "🔧 إصلاح ودفع تغييرات Railway TS18003"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$(dirname "$0")/.."

echo -e "${BLUE}1️⃣ التحقق من حالة Git...${NC}"
git status --short

echo ""
echo -e "${BLUE}2️⃣ إضافة جميع التغييرات...${NC}"
git add -A

echo ""
echo -e "${BLUE}3️⃣ إنشاء commit...${NC}"
git commit -m "fix(railway): resolve TS18003 error - add rootDir and fix Dockerfile

- Add rootDir: 'src' to tsconfig.json to specify source directory
- Update include from 'src' to 'src/**/*' for proper file matching
- Add exclude array for node_modules and dist
- Fix Dockerfile COPY command to explicitly copy src/ directory
- Add tsconfig.json copy to ensure it's available in Docker build
- Add verification step with 'ls -la dist/' to confirm build output

This resolves the Railway build error:
error TS18003: No inputs were found in config file '/app/tsconfig.json'

Fixes: Railway deployment TS18003
Related: TypeScript compilation, Docker build optimization"

echo ""
echo -e "${BLUE}4️⃣ دفع التغييرات إلى GitHub...${NC}"
echo -e "${YELLOW}⚠️  استخدام --force-with-lease لتجاوز conflicts${NC}"
echo ""

if git push --force-with-lease origin main; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✅ تم الدفع بنجاح!${NC}"
    echo "=========================================="
    echo ""
    echo -e "${GREEN}🚀 Railway سيبدأ البناء تلقائياً الآن${NC}"
    echo ""
    echo "📊 راقب السجلات على:"
    echo "   https://railway.app/project/your-project"
    echo ""
    echo "✅ توقع رؤية:"
    echo "   - ✅ npm run build"
    echo "   - ✅ TypeScript compilation completed"
    echo "   - ✅ Created dist/index.js"
    echo ""
else
    echo ""
    echo "=========================================="
    echo -e "${RED}❌ فشل الدفع${NC}"
    echo "=========================================="
    echo ""
    echo -e "${YELLOW}جرب يدوياً:${NC}"
    echo "  git pull --rebase origin main"
    echo "  git push origin main"
    echo ""
    exit 1
fi

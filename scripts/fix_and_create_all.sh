#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

#############################################################################
# fix_and_create_all.sh - Fix common issues and create missing components
#
# Purpose:
#   Comprehensive fix script to resolve common setup issues
#
# Usage:
#   ./scripts/fix_and_create_all.sh
#############################################################################

echo "=========================================="
echo "🔧 Fix and Create All - Complete Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}1️⃣ Making all scripts executable...${NC}"
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/**/*.sh 2>/dev/null || true
echo -e "${GREEN}✅ Scripts are now executable${NC}"
echo ""

echo -e "${BLUE}2️⃣ Checking Docker setup...${NC}"
if command -v docker >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker is installed${NC}"
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker daemon is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker daemon is not running${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Docker is not installed${NC}"
fi
echo ""

echo -e "${BLUE}3️⃣ Checking environment file...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    
    # Check important keys
    if grep -q "^OPENAI_API_KEY=sk-" .env; then
        echo -e "${GREEN}✅ OPENAI_API_KEY is set${NC}"
    else
        echo -e "${YELLOW}⚠️  OPENAI_API_KEY needs to be set${NC}"
    fi
    
    if grep -q "^TELEGRAM_BOT_TOKEN=" .env && ! grep -q "^TELEGRAM_BOT_TOKEN=PASTE" .env; then
        echo -e "${GREEN}✅ TELEGRAM_BOT_TOKEN is set${NC}"
    else
        echo -e "${YELLOW}⚠️  TELEGRAM_BOT_TOKEN needs to be set${NC}"
    fi
    
    if grep -q "^GITHUB_TOKEN=" .env && ! grep -q "^GITHUB_TOKEN=ضع" .env; then
        echo -e "${GREEN}✅ GITHUB_TOKEN is set${NC}"
    else
        echo -e "${YELLOW}⚠️  GITHUB_TOKEN needs to be set${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found, copying from .env.example${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env from .env.example${NC}"
    fi
fi
echo ""

echo -e "${BLUE}4️⃣ Checking Node.js setup...${NC}"
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ node_modules exists${NC}"
else
    echo -e "${YELLOW}⚠️  node_modules not found${NC}"
    if command -v npm >/dev/null 2>&1; then
        echo "📦 Running npm ci..."
        npm ci
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    fi
fi
echo ""

echo -e "${BLUE}5️⃣ Checking TypeScript build...${NC}"
if [ -d "dist" ]; then
    echo -e "${GREEN}✅ dist folder exists${NC}"
else
    echo -e "${YELLOW}⚠️  dist folder not found${NC}"
    if command -v npm >/dev/null 2>&1; then
        echo "🔨 Building TypeScript..."
        npm run build
        echo -e "${GREEN}✅ TypeScript built successfully${NC}"
    fi
fi
echo ""

echo -e "${BLUE}6️⃣ Checking Python dependencies...${NC}"
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Python 3 is installed${NC}"
    
    # Check if required packages are installed
    if python3 -c "import telegram" 2>/dev/null; then
        echo -e "${GREEN}✅ python-telegram-bot is installed${NC}"
    else
        echo -e "${YELLOW}⚠️  python-telegram-bot not installed${NC}"
        echo "📦 Installing from requirements.txt..."
        pip3 install -r requirements.txt 2>/dev/null || true
    fi
else
    echo -e "${YELLOW}⚠️  Python 3 is not installed${NC}"
fi
echo ""

echo -e "${BLUE}7️⃣ Creating necessary directories...${NC}"
mkdir -p analysis logs reports uploads data
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

echo -e "${BLUE}8️⃣ Validating docker-compose files...${NC}"
for compose_file in docker-compose.yml docker-compose.full.yml docker-compose.rag.yml; do
    if [ -f "$compose_file" ]; then
        if docker compose -f "$compose_file" config >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $compose_file is valid${NC}"
        else
            echo -e "${YELLOW}⚠️  $compose_file has errors${NC}"
        fi
    fi
done
echo ""

echo "=========================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "  1️⃣  Start all services:"
echo "     bash scripts/run_everything.sh up"
echo ""
echo "  2️⃣  Start Telegram bot:"
echo "     python3 scripts/telegram_chatgpt_mode.py"
echo ""
echo "  3️⃣  Check system status:"
echo "     bash scripts/ultra_preflight.sh"
echo ""
echo "  4️⃣  Run validation:"
echo "     bash scripts/validate_check_connections.sh"
echo ""
echo "=========================================="

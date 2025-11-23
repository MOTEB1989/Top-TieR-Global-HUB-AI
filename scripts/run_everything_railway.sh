#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

#############################################################################
# run_everything_railway.sh - Railway deployment startup script
#
# Purpose:
#   Start all services and run validation checks for Railway environment
#
# Usage:
#   ./scripts/run_everything_railway.sh
#############################################################################

echo "======================================="
echo "   🚀 Top-TieR Global HUB AI (Railway)"
echo "======================================="

# تحميل متغيرات البيئة
if [ -f ".env" ]; then
    echo "🔧 Loading environment variables..."
    export $(grep -v '^#' .env | xargs)
fi

echo ""
echo "---------------------------------------"
echo "1) Running environment checks..."
echo "---------------------------------------"
bash scripts/validate_check_connections.sh || {
    echo "❌ Environment validation FAILED"
    exit 1
}

echo ""
echo "---------------------------------------"
echo "2) Starting Core..."
echo "---------------------------------------"
if [ -f "start_core.sh" ]; then
    bash start_core.sh
fi

echo ""
echo "---------------------------------------"
echo "3) Starting Smart Agent (FOREGROUND)..."
echo "---------------------------------------"
python3 scripts/smart_agent_validator.py

echo ""
echo "======================================="
echo "✅ Railway deployment completed"
echo "======================================="

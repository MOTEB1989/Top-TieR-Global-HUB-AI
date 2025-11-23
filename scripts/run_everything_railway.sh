#!/usr/bin/env bash
set -e

echo "======================================="
echo "   🚀 Top-TieR Global HUB AI (Railway)"
echo "======================================="

# ================= Config ==================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env"
HEALTH_SCRIPT="${REPO_ROOT}/scripts/system_health_check.py"
VALIDATE_SCRIPT="${REPO_ROOT}/scripts/validate_check_connections.sh"
AGENT_SCRIPT="${REPO_ROOT}/scripts/smart_agent_validator.py"

echo "📁 SCRIPT_DIR = $SCRIPT_DIR"
echo "📁 REPO_ROOT  = $REPO_ROOT"
echo ""

# ================= Safety Checks ==================
echo "🔍 Checking python3..."
command -v python3 >/dev/null || { echo "❌ python3 غير موجود"; exit 1; }

# ================= Secure ENV Loading ==================
if [ -f "$ENV_FILE" ]; then
    echo "🔧 Loading environment variables securely..."
    set -o allexport
    source "$ENV_FILE"
    set +o allexport
else
    echo "❌ No .env file detected at: $ENV_FILE"
    exit 1
fi

echo ""
echo "---------------------------------------"
echo "1) Running environment checks..."
echo "---------------------------------------"

if [ -f "$VALIDATE_SCRIPT" ]; then
    bash "$VALIDATE_SCRIPT" || {
        echo "❌ Environment validation FAILED"
        exit 1
    }
else
    echo "⚠️ No validate_check_connections.sh found"
fi

echo ""
echo "---------------------------------------"
echo "2) Running system health check..."
echo "---------------------------------------"

if [ -f "$HEALTH_SCRIPT" ]; then
    python3 "$HEALTH_SCRIPT" || echo "⚠️ System health warnings"
else
    echo "⚠️ No system_health_check.py found"
fi

echo ""
echo "---------------------------------------"
echo "3) Starting Smart Agent..."
echo "---------------------------------------"

# DRY RUN MODE
if [ "${DRY_RUN:-0}" = "1" ]; then
    echo "🚫 DRY_RUN=1 → Skipping agent execution."
    echo "✨ Service is alive for Railway."
    sleep infinity
fi

# REAL MODE
if [ -f "$AGENT_SCRIPT" ]; then
    echo "🤖 Launching Smart Agent in FOREGROUND..."
    exec python3 "$AGENT_SCRIPT"
else
    echo "❌ smart_agent_validator.py not found — cannot continue."
    exit 1
fi

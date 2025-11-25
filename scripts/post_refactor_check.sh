#!/bin/bash
# post_refactor_check.sh
# Post-refactoring validation checks for the repository
# Verifies environment configuration and optional settings

set -e

echo "=============================================="
echo "🔍 Post-Refactor Check"
echo "=============================================="

# Check for required environment variables
MISSING_VARS=()

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    MISSING_VARS+=("TELEGRAM_BOT_TOKEN")
fi

if [ -z "$OPENAI_API_KEY" ]; then
    MISSING_VARS+=("OPENAI_API_KEY")
fi

if [ -z "$GITHUB_REPO" ]; then
    MISSING_VARS+=("GITHUB_REPO")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please set these variables before proceeding."
    exit 1
fi

echo "✅ All required environment variables are set"
echo ""

# Check optional environment variables
echo "📋 Optional Configuration:"
echo "   OPENAI_MODEL: ${OPENAI_MODEL:-gpt-4o-mini (default)}"

if [ -n "$OPENAI_FALLBACK_MODEL" ]; then
    echo "   OPENAI_FALLBACK_MODEL: $OPENAI_FALLBACK_MODEL ✅"
    echo "   💡 Fallback model is configured for resilience"
    echo "      → Will auto-switch if primary model fails"
else
    echo "   OPENAI_FALLBACK_MODEL: Not set (optional)"
    echo "   💡 Consider setting a fallback model for improved resilience"
    echo "      → Set OPENAI_FALLBACK_MODEL=gpt-4o (or another model)"
fi

echo ""
echo "=============================================="
echo "✅ Post-refactor check completed successfully"
echo "=============================================="

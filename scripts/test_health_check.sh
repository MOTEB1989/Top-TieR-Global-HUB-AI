#!/usr/bin/env bash

# ============================================================================
# Simple Health Check Test Script
# ============================================================================
# This script runs a basic health check test to validate the functionality
# It can be used for local development and testing

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================================================"
echo "          Veritas Health Check Test"
echo "============================================================================"
echo ""

# Change to root directory
cd "$ROOT_DIR"

# Test 1: Direct health check (expected to fail without services)
echo -e "${BLUE}Test 1: Health check without services (should fail)${NC}"
if "$SCRIPT_DIR/veritas_health_check.sh"; then
    echo -e "${YELLOW}⚠️  Unexpected: Health check passed without services running${NC}"
else
    echo -e "${GREEN}✅ Expected: Health check failed without services running${NC}"
fi
echo ""

# Test 2: Health check with services
echo -e "${BLUE}Test 2: Health check with services (should pass)${NC}"
if "$SCRIPT_DIR/start_services_for_health_check.sh"; then
    echo -e "${GREEN}✅ Health check passed with services running${NC}"
    TEST_RESULT="PASS"
else
    echo -e "${RED}❌ Health check failed even with services running${NC}"
    TEST_RESULT="FAIL"
fi
echo ""

# Test 3: Verify port configuration
echo -e "${BLUE}Test 3: Verify port configuration${NC}"
echo "Expected ports from veritas_health_check.sh:"
grep -E "localhost:[0-9]+" "$SCRIPT_DIR/veritas_health_check.sh" | head -5

echo ""
echo "Expected ports from docker-compose.yml:"
grep -E '- "[0-9]+:[0-9]+"' docker-compose.yml | head -5

echo ""
echo "Default port in veritas-web app.py:"
grep -E 'MINI_WEB_PORT.*[0-9]+' veritas-web/app.py || echo "Not found"

echo ""
echo "============================================================================"
if [[ "$TEST_RESULT" == "PASS" ]]; then
    echo -e "${GREEN}✅ All health check tests completed successfully${NC}"
    echo -e "${GREEN}   The health check system is working correctly${NC}"
    exit 0
else
    echo -e "${RED}❌ Health check tests failed${NC}"
    echo -e "${RED}   There may be issues with service startup or configuration${NC}"
    exit 1
fi
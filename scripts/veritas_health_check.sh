#!/usr/bin/env bash

echo "== Veritas Stack Health Check =="
date

# Initialize error counter
ERROR_COUNT=0

# Configuration with environment variable support
CORE_API_URL="${CORE_URL:-http://localhost:8000}"
VERITAS_WEB_URL="${VERITAS_WEB_URL:-http://localhost:8080}"

# Add /health if not already present
if [[ ! "$CORE_API_URL" =~ /health$ ]]; then
    CORE_API_URL="${CORE_API_URL}/health"
fi

if [[ ! "$VERITAS_WEB_URL" =~ /health$ ]]; then
    VERITAS_WEB_URL="${VERITAS_WEB_URL}/health"
fi

echo "Configuration:"
echo "  CORE_API_URL: $CORE_API_URL"
echo "  VERITAS_WEB_URL: $VERITAS_WEB_URL"
echo ""

check_service() {
  local name=$1
  local url=$2

  echo "Checking $name at $url ..."
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")

  if [ "$status" -eq 200 ]; then
    echo "✅ $name is healthy ($status)"
    return 0
  else
    echo "❌ $name health check failed (status: $status)"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    return 1
  fi
}

# Core API health check
check_service "CORE_API" "$CORE_API_URL"

# Veritas Mini-Web health check  
check_service "VERITAS_WEB" "$VERITAS_WEB_URL"

echo "== Health check complete =="

if [ $ERROR_COUNT -gt 0 ]; then
  echo "❌ Health check failed with $ERROR_COUNT error(s)"
  exit 1
else
  echo "✅ All services are healthy"
  exit 0
fi
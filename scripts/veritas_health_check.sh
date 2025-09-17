#!/usr/bin/env bash

echo "== Veritas Stack Health Check =="
date

# Initialize error counter
ERROR_COUNT=0

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

# Use environment variables if set, otherwise use defaults
# For backward compatibility, support both old and new variable names

# Core API (main application)
if [ -n "$CORE_URL" ]; then
  CORE_API_URL="$CORE_URL/health"
else
  CORE_API_URL="http://localhost:8000/health"
fi

# OSINT/Veritas Web service
if [ -n "$OSINT_URL" ]; then
  VERITAS_WEB_URL="$OSINT_URL/health"
elif [ -n "$VERITAS_WEB_URL" ]; then
  VERITAS_WEB_URL="$VERITAS_WEB_URL/health"
else
  VERITAS_WEB_URL="http://localhost:8080/health"
fi

# Core API health check
check_service "CORE_API" "$CORE_API_URL"

# Veritas/OSINT service health check  
if [ -n "$OSINT_URL" ]; then
  check_service "OSINT_SERVICE" "$VERITAS_WEB_URL"
else
  check_service "VERITAS_WEB" "$VERITAS_WEB_URL"
fi

echo "== Health check complete =="

if [ $ERROR_COUNT -gt 0 ]; then
  echo "❌ Health check failed with $ERROR_COUNT error(s)"
  exit 1
else
  echo "✅ All services are healthy"
  exit 0
fi
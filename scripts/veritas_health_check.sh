#!/usr/bin/env bash

echo "== Veritas Stack Health Check =="
date

# Initialize error counter
ERROR_COUNT=0

check_service() {
  local name=$1
  local url=$2

  echo "Checking $name at $url ..."
  
  # Check if curl is available
  if ! command -v curl >/dev/null 2>&1; then
    echo "❌ $name health check failed (curl not available)"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    return 1
  fi
  
  # Perform the health check
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")

  if [ "$status" -eq 200 ]; then
    echo "✅ $name is healthy (status: $status)"
    return 0
  elif [ "$status" = "000" ]; then
    echo "❌ $name health check failed (connection failed - service may not be running)"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    return 1
  else
    echo "❌ $name health check failed (status: $status)"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    return 1
  fi
}

# Core API على المنفذ 8000
check_service "CORE_API" "http://localhost:8000/health"

# Veritas Mini-Web على المنفذ 8080
check_service "VERITAS_WEB" "http://localhost:8080/health"

echo "== Health check complete =="

if [ $ERROR_COUNT -gt 0 ]; then
  echo "❌ Health check failed with $ERROR_COUNT error(s)"
  exit 1
else
  echo "✅ All services are healthy"
  exit 0
fi
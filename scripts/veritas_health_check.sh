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

# Core API على المنفذ 8000
check_service "CORE_API" "http://localhost:8000/health"

# Web UI Service على المنفذ 3000
check_service "WEB_UI" "http://localhost:3000/health"

echo "== Health check complete =="

if [ $ERROR_COUNT -gt 0 ]; then
  echo "❌ Health check failed with $ERROR_COUNT error(s)"
  exit 1
else
  echo "✅ All services are healthy"
  exit 0
fi
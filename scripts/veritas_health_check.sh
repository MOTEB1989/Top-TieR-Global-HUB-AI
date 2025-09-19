#!/usr/bin/env bash
set -euo pipefail

ERROR_COUNT=0

check_service() {
  local name=$1
  local url=$2

  echo "Checking $name at $url ..."
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")

  if [ "$status" -eq 200 ]; then
    echo "✅ $name is healthy ($status)"
    return 0
  else
    echo "❌ $name health check failed (status: $status)"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    return 1
  fi
}

# إضافة الخدمات المطلوب فحصها هنا
check_service "API" "http://localhost:8000/health"
check_service "Frontend" "http://localhost:8080/health"

if [ "$ERROR_COUNT" -gt 0 ]; then
  echo "❌ Health check failed for $ERROR_COUNT service(s)."
  exit 1
else
  echo "✅ All services are healthy."
  exit 0
fi

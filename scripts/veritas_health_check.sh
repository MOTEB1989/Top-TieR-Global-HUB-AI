#!/usr/bin/env bash
set -e

# تحميل القيم من .env إذا كان موجود
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

API_PORT=${API_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}

echo "== Veritas Stack Health Check =="
date

check_service() {
  local name=$1
  local url=$2
  echo "Checking $name at $url ..."
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
  if [ "$status" -eq 200 ]; then
    echo "✅ $name is healthy ($status)"
  else
    echo "❌ $name health check failed (status: $status)"
  fi
}

# فحص الـ Backend API
check_service "CORE_API" "http://localhost:${API_PORT}/health"

# فحص الـ Frontend Web
check_service "VERITAS_WEB" "http://localhost:${FRONTEND_PORT}"

echo "== Health check complete =="

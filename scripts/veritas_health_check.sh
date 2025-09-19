#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="health.log"
> "$LOG_FILE"

check_service() {
  local name=$1
  local url=$2

  echo "== Checking $name at $url ==" | tee -a "$LOG_FILE"
  if curl -fsS "$url" > /dev/null; then
    echo "✅ $name is healthy." | tee -a "$LOG_FILE"
    return 0
  else
    echo "❌ $name health check failed." | tee -a "$LOG_FILE"
    return 1
  fi
}

echo "== Veritas Stack Health Check ==" | tee -a "$LOG_FILE"
date | tee -a "$LOG_FILE"

errors=0

# فحص الـ Core API
if ! check_service "CORE_API" "http://localhost:8000/health"; then
  errors=$((errors+1))
fi

# فحص الـ Veritas Web
if ! check_service "VERITAS_WEB" "http://localhost:8080/health"; then
  errors=$((errors+1))
fi

echo "== Health check complete ==" | tee -a "$LOG_FILE"

if [ "$errors" -gt 0 ]; then
  echo "❌ Health check failed with $errors error(s)." | tee -a "$LOG_FILE"
  exit 1
else
  echo "✅ All services healthy." | tee -a "$LOG_FILE"
fi

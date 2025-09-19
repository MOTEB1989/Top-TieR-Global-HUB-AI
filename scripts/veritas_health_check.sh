#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="health.log"

echo "== Veritas Stack Health Check ==" | tee -a "$LOG_FILE"
date | tee -a "$LOG_FILE"

# تعريف الخدمات
SERVICES=(
  "CORE_API:http://localhost:8000/health"
  "VERITAS_WEB:http://localhost:8080/health"
)

errors=0

for service in "${SERVICES[@]}"; do
  name="${service%%:*}"
  url="${service#*:}"

  echo "Checking $name at $url ..." | tee -a "$LOG_FILE"

  status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
  if [[ "$status" == "200" ]]; then
    echo "✅ $name is healthy ($status)" | tee -a "$LOG_FILE"
  else
    echo "❌ $name health check failed (status: $status)" | tee -a "$LOG_FILE"
    ((errors++))
  fi
done

echo "== Health check complete ==" | tee -a "$LOG_FILE"

if [[ $errors -gt 0 ]]; then
  echo "❌ Health check failed with $errors error(s)" | tee -a "$LOG_FILE"
  exit 1
else
  echo "✅ All services are healthy" | tee -a "$LOG_FILE"
fi

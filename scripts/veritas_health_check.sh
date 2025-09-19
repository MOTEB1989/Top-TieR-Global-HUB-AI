#!/usr/bin/env bash
set -o pipefail

LOG_FILE="health.log"
echo "== Veritas Stack Health Check ==" > $LOG_FILE
date >> $LOG_FILE

# دالة لفحص خدمة
check_service() {
  local name=$1
  local url=$2
  echo "Checking $name at $url ..." | tee -a $LOG_FILE
  status=$(curl -s -o /dev/null -w "%{http_code}" $url || echo "000000")
  if [[ "$status" == "200" ]]; then
    echo "✅ $name is healthy (status: $status)" | tee -a $LOG_FILE
    return 0
  else
    echo "❌ $name health check failed (status: $status)" | tee -a $LOG_FILE
    return 1
  fi
}

# المحاولات
errors=0
for attempt in {1..2}; do
  echo -e "\n== Attempt $attempt ==" | tee -a $LOG_FILE
  check_service "CORE_API" "http://localhost:8000/health" || errors=$((errors+1))
  check_service "VERITAS_WEB" "http://localhost:8080/health" || errors=$((errors+1))

  if [[ $errors -eq 0 ]]; then
    echo "✅ All services healthy" | tee -a $LOG_FILE
    exit 0
  fi
  sleep 10
done

echo "❌ Health check failed with $errors error(s)" | tee -a $LOG_FILE
exit 1

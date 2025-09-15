#!/usr/bin/env bash

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

# Core API على المنفذ 8000
check_service "CORE_API" "http://localhost:8000/health"

# Veritas Mini-Web على المنفذ 8080
check_service "VERITAS_WEB" "http://localhost:8080/health"

echo "== Health check complete =="
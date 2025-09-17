#!/usr/bin/env bash

echo "== Veritas Stack Health Check =="
date

# Initialize error counter
ERROR_COUNT=0

# Configuration from environment with defaults
CORE_API_URL="${CORE_URL:-http://localhost:8000}"
VERITAS_WEB_URL="${OSINT_URL:-http://localhost:8088}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-10}"

check_service() {
  local name=$1
  local url=$2

  echo "Checking $name at $url ..."
  
  # First check if service is reachable at all
  if ! curl -s --max-time 5 "$url" > /dev/null 2>&1; then
    echo "❌ $name is not reachable at $url"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    return 1
  fi
  
  # Check health endpoint with detailed status
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$HEALTH_TIMEOUT" "$url" 2>/dev/null || echo "000")

  if [ "$status" -eq 200 ]; then
    echo "✅ $name is healthy (status: $status)"
    
    # Get health details if available
    response=$(curl -s --max-time 5 "$url" 2>/dev/null || echo "{}")
    if echo "$response" | jq . >/dev/null 2>&1; then
      echo "   Health details: $(echo "$response" | jq -c .)"
    fi
    return 0
  else
    echo "❌ $name health check failed (status: $status)"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    return 1
  fi
}

# Wait for service to be ready (with retry)
wait_for_service() {
  local name=$1
  local url=$2
  local max_attempts=30
  local attempt=1
  
  echo "Waiting for $name to be ready..."
  
  while [ $attempt -le $max_attempts ]; do
    if curl -s --max-time 3 "$url" > /dev/null 2>&1; then
      echo "✅ $name is ready after $attempt attempts"
      return 0
    fi
    
    echo "   Attempt $attempt/$max_attempts - $name not ready yet..."
    sleep 2
    attempt=$((attempt + 1))
  done
  
  echo "❌ $name failed to become ready after $max_attempts attempts"
  return 1
}

# Core API على المنفذ 8000
wait_for_service "CORE_API" "$CORE_API_URL/health"
check_service "CORE_API" "$CORE_API_URL/health"

# Veritas Mini-Web على المنفذ 8088 (not 8080)
wait_for_service "VERITAS_WEB" "$VERITAS_WEB_URL/health" 
check_service "VERITAS_WEB" "$VERITAS_WEB_URL/health"

echo "== Health check complete =="

if [ $ERROR_COUNT -gt 0 ]; then
  echo "❌ Health check failed with $ERROR_COUNT error(s)"
  exit 1
else
  echo "✅ All services are healthy"
  exit 0
fi
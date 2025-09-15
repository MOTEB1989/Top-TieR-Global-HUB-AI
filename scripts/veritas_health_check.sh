#!/usr/bin/env bash
set -euo pipefail

# Veritas Health Check Script
echo "== Veritas Health Check =="
# Check CORE service
echo "Checking CORE_URL: $CORE_URL"
curl --silent --fail "$CORE_URL/health" || { echo "CORE health check failed"; exit 1; }

# Check OSINT service
echo "Checking OSINT_URL: $OSINT_URL"
curl --silent --fail "$OSINT_URL/health" || { echo "OSINT health check failed"; exit 1; }

# Check Neo4j HTTP port
echo "Checking NEO4J_HTTP: $NEO4J_HTTP"
curl --silent --fail --user "$NEO4J_USER:$NEO4J_PASS" "$NEO4J_HTTP" || { echo "Neo4j health check failed"; exit 1; }

echo "All services are healthy."
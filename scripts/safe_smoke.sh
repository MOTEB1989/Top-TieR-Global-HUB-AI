#!/usr/bin/env bash
set -euo pipefail

CORE_URL="${CORE_URL:-http://localhost:8080}"
OSINT_URL="${OSINT_URL:-http://localhost:8081}"
NEO4J_HTTP="${NEO4J_HTTP:-http://localhost:7474}"
HDR=(-H "X-Dry-Run: 1" -H "Content-Type: application/json")

echo "== SAFE SMOKE =="
curl -fsS --max-time 5 "$CORE_URL/health" >/dev/null && echo "CORE: OK" || { echo "CORE: FAIL"; exit 1; }
curl -fsS --max-time 6 "${CORE_URL}/query" "${HDR[@]}" -d '{"query":"null@example.com","type":"email","scope":["osint"],"dry_run":true}' >/dev/null && echo "CORE /query: OK"
curl -fsS --max-time 6 "${OSINT_URL}/osint/search?dry_run=true" -H "X-Dry-Run: 1" >/dev/null && echo "OSINT /osint/search: OK"

if [[ -n "${NEO4J_USER:-}" && -n "${NEO4J_PASS:-}" ]]; then
  curl -fsS --max-time 6 -u "${NEO4J_USER}:${NEO4J_PASS}" \
    "${NEO4J_HTTP}/db/neo4j/tx/commit" -H "Content-Type: application/json" \
    -d '{"statements":[{"statement":"RETURN 1"}]}' >/dev/null && echo "NEO4J: OK"
else
  echo "NEO4J: SKIP (no creds provided)"
fi
echo "ALL GREEN (READ-ONLY)"
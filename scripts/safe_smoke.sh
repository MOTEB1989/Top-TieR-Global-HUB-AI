#!/usr/bin/env bash
set -euo pipefail
CORE_URL="${CORE_URL:-http://localhost:8080}"
OSINT_URL="${OSINT_URL:-http://localhost:8081}"
NEO4J_HTTP="${NEO4J_HTTP:-http://localhost:7474}"
HDR=(-H "X-Dry-Run: 1" -H "Content-Type: application/json")
PASS=1
echo "== SAFE SMOKE (read-only) =="
if curl -fsS --max-time 8 "$CORE_URL/health" >/dev/null; then
  echo "CORE: OK"
else
  echo "CORE: FAIL"; PASS=0
fi
if curl -fsS --max-time 10 "${CORE_URL}/query" "${HDR[@]}" \
  -d '{"query":"null@example.com","type":"email","scope":["osint"],"dry_run":true}' >/dev/null; then
  echo "CORE /query: OK"
else
  echo "CORE /query: FAIL"; PASS=0
fi
if curl -fsS --max-time 10 "${OSINT_URL}/osint/search?dry_run=true" -H "X-Dry-Run: 1" >/dev/null; then
  echo "OSINT /osint/search: OK"
else
  echo "OSINT /osint/search: FAIL"; PASS=0
fi
if [[ -n "${NEO4J_USER:-}" && -n "${NEO4J_PASS:-}" ]]; then
  if curl -fsS --max-time 10 -u "${NEO4J_USER}:${NEO4J_PASS}" \
    "${NEO4J_HTTP}/db/neo4j/tx/commit" -H "Content-Type: application/json" \
    -d '{"statements":[{"statement":"RETURN 1"}]}' >/dev/null; then
    echo "NEO4J: OK"
  else
    echo "NEO4J: FAIL"; PASS=0
  fi
else
  echo "NEO4J: SKIP (no creds)"
fi
[[ $PASS -eq 1 ]] && echo "ALL GREEN (READ-ONLY)" || { echo "SOME CHECKS FAILED"; exit 1; }

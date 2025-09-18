#!/usr/bin/env bash
set -euo pipefail

# =====================================================================
# Veritas CI Readonly Bootstrap
# - لا يشغّل أو يوقف شيئًا افتراضيًا.
# - يفحص فقط إن كانت الخدمات متوفرة محليًا ثم ينفّذ فحوص curl خفيفة.
# - STRICT=1 يجعل الفشل يُرجِع non-zero (لتفعيل الإنذار)؛ افتراضيًا STRICT=0.
# - START_CANARY=1 يسمح بتشغيل كاناري مؤقت عبر docker-compose.override.yml
#   (لن يُشغَّل نهائيًا إلا إذا عرّفته صراحةً).
# =====================================================================

STRICT="${STRICT:-0}"
START_CANARY="${START_CANARY:-0}"

CORE_URL="${CORE_URL:-http://localhost:8080}"
OSINT_URL="${OSINT_URL:-http://localhost:8081}"
NEO4J_HTTP="${NEO4J_HTTP:-http://localhost:7474}"

log()  { printf "%s\n" "$*" ; }
ok()   { log "✅ $*"; }
warn() { log "⚠️  $*"; }
err()  { log "❌ $*"; }

# -------- (اختياري) تشغيل كاناري ظل إذا طُلِب ----------
maybe_start_canary() {
  if [[ "$START_CANARY" != "1" ]]; then
    warn "START_CANARY=0 → لن يتم تشغيل أي حاويات (وضع قراءة فقط)."
    return 0
  fi
  if [[ -f docker-compose.yml && -f docker-compose.override.yml ]]; then
    warn "تشغيل كاناري ظل مؤقت (override) ..."
    docker compose -f docker-compose.yml -f docker-compose.override.yml up -d core-gateway-canary osint-canary || {
      err "فشل تشغيل الكاناري."
      return 1
    }
    ok "تشغيل الكاناري تم بنجاح."
  else
    warn "لا يوجد docker-compose.yml أو override؛ تخطّي تشغيل الكاناري."
  fi
}

# -------- فحوص خفيفة (لا كتابة) ----------
probe_core() {
  local rc=0
  if curl -fsS --max-time 5 "${CORE_URL}/health" >/dev/null 2>&1; then
    ok "CORE /health ✓"
  else
    warn "CORE غير متاح على ${CORE_URL}/health"
    rc=1
  fi

  # استعلام مموّه dry-run (لا كتابة)
  curl -fsS --max-time 6 "${CORE_URL}/query" \
    -H "Content-Type: application/json" -H "X-Dry-Run: 1" \
    -d '{"query":"null@example.com","type":"email","scope":["osint"],"dry_run":true}' >/dev/null 2>&1 \
    && ok "CORE /query (dry-run) ✓" \
    || warn "CORE /query لم يستجب (قد يكون طبيعيًا إذا لم تعمل الخدمة)."
  return $rc
}

probe_osint() {
  curl -fsS --max-time 6 "${OSINT_URL}/osint/search?dry_run=true" \
    -H "X-Dry-Run: 1" >/dev/null 2>&1 \
    && ok "OSINT /osint/search (dry-run) ✓" \
    || warn "OSINT غير متاح على ${OSINT_URL} (قد يكون طبيعيًا)."
}

probe_neo4j() {
  if curl -fsS --max-time 5 "${NEO4J_HTTP}" >/dev/null 2>&1; then
    ok "Neo4j UI متاح على ${NEO4J_HTTP}"
  else
    warn "Neo4j UI غير متاح على ${NEO4J_HTTP}"
  fi

  if [[ -n "${NEO4J_USER:-}" && -n "${NEO4J_PASS:-}" ]]; then
    curl -fsS --max-time 6 -u "${NEO4J_USER}:${NEO4J_PASS}" \
      "${NEO4J_HTTP}/db/neo4j/tx/commit" \
      -H "Content-Type: application/json" \
      -d '{"statements":[{"statement":"RETURN 1"}]}' >/dev/null 2>&1 \
      && ok "Neo4j RETURN 1 ✓" \
      || warn "Neo4j auth أو API لم ينجح (تحذير فقط)."
  else
    warn "Neo4j: لا توجد بيانات اعتماد — تخطّي فحص RETURN 1 (اسماء الأسرار فقط مطلوبة مستقبلًا)."
  fi
}

main() {
  local failures=0
  maybe_start_canary || failures=$((failures+1))

  probe_core  || failures=$((failures+1))
  probe_osint || true
  probe_neo4j || true

  if [[ "$failures" -gt 0 ]]; then
    warn "انتهى الفحص مع ${failures} تحذير/فشل."
    if [[ "$STRICT" == "1" ]]; then
      err "STRICT=1 → إرجاع non-zero لتنبيه الـ CI."
      return 1
    fi
  else
    ok "كل الفحوص (القراءة فقط) بدت سليمة."
  fi
}

main

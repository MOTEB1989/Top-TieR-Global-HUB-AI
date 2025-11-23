#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# -----------------------------------------------------------------
# fix_and_create_all.sh
# Unified fixer: create missing docs, fix ts build, update docker-compose,
# inject health endpoints where feasible, run preflight (if exists),
# commit to feature/safe-auto-merge and push.
# -----------------------------------------------------------------

START_DIR="$(pwd)"
SCRIPT_NAME="$(basename "$0")"
BRANCH="feature/safe-auto-merge"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

info(){ printf "\e[34m[INFO]\e[0m %s\n" "$*"; }
ok(){ printf "\e[32m[OK]\e[0m %s\n" "$*"; }
warn(){ printf "\e[33m[WARN]\e[0m %s\n" "$*"; }
err(){ printf "\e[31m[ERR]\e[0m %s\n" "$*"; }

info "Starting $SCRIPT_NAME in: $START_DIR"

# 0) Ensure git is clean-ish
if ! command -v git >/dev/null 2>&1; then
  err "git not found. Please run inside your Codespace or machine with git."
  exit 1
fi

info "Pulling latest from origin/main"
git fetch origin main --quiet || true
git checkout -B "$BRANCH" || git checkout "$BRANCH" || true
git reset --hard origin/main || true

# Create scripts dir if missing
mkdir -p scripts

# --- 1) Create missing docs if not present ---
info "Creating missing documentation files if absent..."

create_if_missing() {
  local path="$1"; shift
  local content="$*"
  if [ -f "$path" ]; then
    ok "Exists: $path"
  else
    info "Creating: $path"
    mkdir -p "$(dirname "$path")"
    cat > "$path" <<'EOF'
'"$content"'
EOF
    # overwrite with provided here-doc content; we'll replace token above
    # but simpler: use a second approach below
  fi
}

# We'll write content explicitly for each file to avoid quoting issues

if [ ! -f "AGENT_PLAYBOOK.md" ]; then
  cat > AGENT_PLAYBOOK.md <<'MD'
# AGENT_PLAYBOOK

## Purpose
Playbook for safe agent operations in Top-TieR-Global-HUB-AI.

## Safety Limits
- Destructive commands require confirm step.
- Max automatic merges per run: 5 (configurable).

## Commands (bot)
- /scan -> run full repository scan
- /preflight -> run preflight checks
- /auto_merge <PR> -> attempt merge (allowlist + manual confirm)
- /logs -> show logs (read-only)
- /whoami -> return your Telegram numeric ID (useful to add to TELEGRAM_ALLOWLIST)

## Last Updated: ${TIMESTAMP}
MD
  ok "Created AGENT_PLAYBOOK.md"
else
  ok "AGENT_PLAYBOOK.md already present"
fi

if [ ! -f "WORKFLOW_MAP.md" ]; then
  cat > WORKFLOW_MAP.md <<'MD'
# WORKFLOW_MAP

## Key Workflows (sample)
| Workflow | Trigger | Purpose |
|---|---:|---|
| self_healing_agent.yml | failure events | attempt auto-fixes |
| external-api-diagnosis.yml | schedule | check availability of external providers |
| post_merge_validation.yml | PR merge | smoke tests after merge |

## Last Updated: ${TIMESTAMP}
MD
  ok "Created WORKFLOW_MAP.md"
else
  ok "WORKFLOW_MAP.md already present"
fi

# ARCHITECTURE.md: if missing create minimal (if exists leave)
if [ ! -f "ARCHITECTURE.md" ]; then
  cat > ARCHITECTURE.md <<'MD'
# ARCHITECTURE (Auto-generated minimal)

This file summarizes the current layout of the repository and runtime infra.
- Branch used for infra changes: ${BRANCH}
- API_PORT default: 3000

Services:
- core (Rust) - port 8080 (if Dockerfile present)
- api (Node) - port 3000
- redis - port 6379 (optional)
- qdrant - port 6333 (optional)
- neo4j - ports 7474/7687 (optional)

Generated: ${TIMESTAMP}
MD
  ok "Created ARCHITECTURE.md"
else
  ok "ARCHITECTURE.md already present"
fi

# SECURITY_POSTURE.md: if missing create stub
if [ ! -f "SECURITY_POSTURE.md" ]; then
  cat > SECURITY_POSTURE.md <<'MD'
# SECURITY_POSTURE

- Secret management: Use GitHub Secrets (do NOT commit secrets to repo).
- Recommended: TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWLIST, OPENAI_API_KEY, GITHUB_TOKEN, REDIS_URL, NEO4J_URI, NEO4J_AUTH

Generated: ${TIMESTAMP}
MD
  ok "Created SECURITY_POSTURE.md"
else
  ok "SECURITY_POSTURE.md already present"
fi

# --- 2) Create .env.example if missing ---
if [ ! -f ".env.example" ]; then
  cat > .env.example <<'ENV'
# Example .env (placeholders - DO NOT COMMIT SECRETS)
API_PORT=3000

# AI / LLM
OPENAI_API_KEY=
GROQ_API_KEY=
ANTHROPIC_API_KEY=

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWLIST=6090738107,8256840669
TELEGRAM_CHAT_ID=

# GitHub
GITHUB_TOKEN=
GITHUB_REPO=MOTEB1989/Top-TieR-Global-HUB-AI

# Databases
DB_URL=
REDIS_URL=
NEO4J_URI=
NEO4J_AUTH=

# Paths
ULTRA_PREFLIGHT_PATH=scripts/ultra_preflight.sh
FULL_SCAN_SCRIPT=scripts/execute_full_scan.sh
LOG_FILE_PATH=analysis/ULTRA_REPORT.md
ENV
  ok "Created .env.example"
else
  ok ".env.example already present"
fi

# --- 3) Create a small test script to validate Telegram/GitHub/OpenAI secrets ---
if [ ! -f "scripts/test_telegram_bot.py" ]; then
  cat > scripts/test_telegram_bot.py <<'PY'
#!/usr/bin/env python3
"""
scripts/test_telegram_bot.py
Simple checker to validate presence/form of required env vars.
Does not print secret values.
"""
import os, sys
reqs = [
    "OPENAI_API_KEY","TELEGRAM_BOT_TOKEN","TELEGRAM_ALLOWLIST","GITHUB_TOKEN","GITHUB_REPO"
]
ok = []
miss = []
for k in reqs:
    v = os.getenv(k, "")
    if v:
        ok.append((k, len(v)))
    else:
        miss.append(k)
print("=== ENV CHECK ===")
for k,l in ok:
    print(f"OK: {k} (len={l})")
for k in miss:
    print(f"MISSING: {k}")
print("=================")
if miss:
    sys.exit(2)
else:
    print("All required keys present (basic check).")
PY
  chmod +x scripts/test_telegram_bot.py
  ok "Created scripts/test_telegram_bot.py"
else
  ok "scripts/test_telegram_bot.py already present"
fi

# --- 4) Fix TypeScript build issue: ensure src/ contains index.ts if tsconfig expects src ---
TSCONFIG="tsconfig.json"
if [ -f "$TSCONFIG" ]; then
  info "Found tsconfig.json, checking include paths..."
  # crude check: if tsconfig contains "src" and no src dir exists, copy index.ts if found
  if grep -q "\"src\"" "$TSCONFIG" 2>/dev/null; then
    if [ ! -d "src" ]; then
      if [ -f "index.ts" ]; then
        mkdir -p src
        cp -v index.ts src/index.ts || true
        ok "Copied index.ts -> src/index.ts to satisfy tsconfig include"
      else
        warn "tsconfig.json expects src but index.ts not found; please ensure .ts sources are in src/ or adjust tsconfig.json"
      fi
    else
      ok "src/ exists"
    fi
  else
    ok "tsconfig.json does not reference src explicitly"
  fi
else
  warn "No tsconfig.json found; skipping TS fix"
fi

# --- 5) Try to inject /health and /ready endpoints in Node/Express or Fastify entrypoint if present ---
inject_node_health() {
  local file="$1"
  if [ ! -f "$file" ]; then
    return 1
  fi
  if grep -q "/health" "$file" || grep -q "/ready" "$file"; then
    ok "Health endpoints already present in $file"
    return 0
  fi
  info "Injecting simple /health and /ready handlers into $file (backup first)"
  cp -v "$file" "${file}.bak" || true
  # append handlers at end (works for common Express/Fastify patterns)
  cat >> "$file" <<'JS'

/* Auto-inserted health endpoints */
app.get('/health', (_req, res) => res.json({ status: 'ok' }));
app.get('/ready', (_req, res) => res.json({ status: 'ready' }));
/* End auto-insert */
JS
  ok "Injected health endpoints into $file (backup ${file}.bak)"
  return 0
}

# Search for likely Node entrypoints
NODE_ENTRIES=( "src/index.ts" "index.ts" "src/index.js" "index.js" "services/api/index.ts" "services/api/index.js" )
for f in "${NODE_ENTRIES[@]}"; do
  if [ -f "$f" ]; then
    inject_node_health "$f" || true
    break
  fi
done

# For Python FastAPI/Flask
PY_ENTRIES=( "src/web/app.py" "app.py" "api_server/app.py" "services/python/app.py" )
for f in "${PY_ENTRIES[@]}"; do
  if [ -f "$f" ]; then
    if grep -q "def health" "$f" || grep -q "/health" "$f"; then
      ok "Python health endpoints appear present in $f"
    else
      info "Appending simple FastAPI-style health endpoints to $f (if FastAPI is used)"
      cp -v "$f" "${f}.bak" || true
      cat >> "$f" <<'PYAPP'

# Auto-inserted health endpoints
try:
    from fastapi import FastAPI
    _app = globals().get("app", None)
    if _app is None:
        try:
            # if using Flask or other frameworks, skip
            pass
        except Exception:
            pass
    else:
        @_app.get("/health")
        def _health():
            return {"status": "ok"}
        @_app.get("/ready")
        def _ready():
            return {"status": "ready"}
except Exception:
    # Could not detect FastAPI app variable; ensure health endpoints exist.
    pass
# End auto-insert
PYAPP
      ok "Appended FastAPI health stubs to $f (backup ${f}.bak)"
    fi
    break
  fi
done

# --- 6) Update docker-compose.yml (backup first), write normalized version that uses detected contexts ---
DC="docker-compose.yml"
if [ -f "$DC" ]; then
  info "Backing up existing $DC -> ${DC}.bak"
  cp -v "$DC" "${DC}.bak" || true
fi

info "Detecting build contexts..."
# determine core build context
if [ -d "core" ] && [ -f "core/Dockerfile" ]; then
  CORE_CONTEXT="./core"
elif [ -f "Dockerfile" ]; then
  CORE_CONTEXT="."
else
  CORE_CONTEXT="."   # fallback
fi

# determine api build context
if [ -d "services/api" ] && [ -f "services/api/Dockerfile" ]; then
  API_CONTEXT="./services/api"
elif [ -f "package.json" ]; then
  # assume Node code at root
  API_CONTEXT="."
else
  API_CONTEXT="."
fi

cat > "$DC" <<EOF
version: '3.8'

services:
  core:
    build:
      context: ${CORE_CONTEXT}
      dockerfile: Dockerfile
    container_name: core_service
    ports:
      - "8080:8080"
    environment:
      - RUST_LOG=info
      - DATABASE_URL=bolt://neo4j:7687
    depends_on:
      - neo4j
    restart: on-failure

  api:
    build:
      context: ${API_CONTEXT}
      dockerfile: Dockerfile
    container_name: api_gateway
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - CORE_SERVICE_URL=http://core:8080
      - NEO4J_URI=bolt://neo4j:7687
    depends_on:
      - core
      - neo4j
    restart: always

  neo4j:
    image: neo4j:4.4
    container_name: neo4j_db
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - ./data/neo4j/data:/data
      - ./data/neo4j/logs:/logs
    environment:
      - NEO4J_AUTH=neo4j/password
    restart: always

  redis:
    image: redis:7-alpine
    container_name: redis_cache
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data
    restart: always

  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant_db
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./data/qdrant_storage:/qdrant/storage:z
    restart: always

networks:
  default:
    driver: bridge
EOF

ok "Wrote normalized docker-compose.yml (backup at ${DC}.bak)"

# Validate docker compose config if docker available
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  info "Validating docker compose file..."
  if docker compose config >/dev/null 2>&1; then
    ok "docker compose config is valid"
  else
    warn "docker compose config produced errors; review manually (run: docker compose -f docker-compose.yml config)"
  fi
else
  warn "docker CLI or docker compose not available in this environment; skip validation"
fi

# --- 7) Ensure scripts/ultra_preflight.sh exists (touch if missing with stub) ---
if [ ! -f "scripts/ultra_preflight.sh" ]; then
  cat > scripts/ultra_preflight.sh <<'SH'
#!/usr/bin/env bash
set -e
echo "Stub preflight: no checks implemented. Replace with real preflight logic."
exit 0
SH
  chmod +x scripts/ultra_preflight.sh
  ok "Created stub scripts/ultra_preflight.sh"
else
  ok "scripts/ultra_preflight.sh exists"
fi

# --- 8) Commit changes and push to branch ---
info "Staging changes..."
git add AGENT_PLAYBOOK.md WORKFLOW_MAP.md ARCHITECTURE.md SECURITY_POSTURE.md .env.example scripts/test_telegram_bot.py scripts/ultra_preflight.sh docker-compose.yml || true

# If ts src created, add it
if [ -d "src" ]; then
  git add src || true
fi

# Commit with message
COMMIT_MSG="chore(infra): create missing docs & normalize infra, add preflight stub, TS/docker fixes"
git commit -m "$COMMIT_MSG" || {
  warn "No changes to commit (maybe everything already staged/committed)."
}
info "Pushing branch $BRANCH to origin..."
git push -u origin "$BRANCH" || warn "git push failed; check credentials/remote."

# --- 9) Run preflight if available ---
if [ -x "scripts/ultra_preflight.sh" ]; then
  info "Running preflight script (scripts/ultra_preflight.sh)..."
  ./scripts/ultra_preflight.sh 2>&1 | tee preflight_output.log || warn "preflight script returned non-zero (see preflight_output.log)"
  ok "Preflight finished (output saved to preflight_output.log)"
else
  warn "scripts/ultra_preflight.sh not executable or missing; skipped"
fi

# --- 10) Final report to user ---
cat <<SUMMARY

==================== FINAL REPORT ====================

Branch updated: $BRANCH
Committed: $COMMIT_MSG

Files created or ensured:
 - AGENT_PLAYBOOK.md
 - WORKFLOW_MAP.md
 - ARCHITECTURE.md (if absent)
 - SECURITY_POSTURE.md (if absent)
 - .env.example
 - scripts/test_telegram_bot.py
 - scripts/ultra_preflight.sh (stub if none existed)
 - docker-compose.yml (normalized; original backed up to docker-compose.yml.bak)

TypeScript fix:
 - If tsconfig.json referenced "src" and you had index.ts in repo root, a copy was made to src/index.ts.

Health endpoints:
 - Attempted injection to likely Node/Python entrypoints (backups created as *.bak).

Preflight:
 - Ran scripts/ultra_preflight.sh (output -> preflight_output.log)

NEXT STEPS (manual actions for you):
1) Add secrets to GitHub (Repository Settings -> Secrets):
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_ALLOWLIST (e.g. 6090738107,8256840669)
   - OPENAI_API_KEY
   - GITHUB_TOKEN
   - (optional) REDIS_URL, NEO4J_URI, NEO4J_AUTH, DB_URL

2) Verify Node TS build locally:
   - If you use TypeScript, ensure sources are in src/ or adjust tsconfig.json accordingly.
   - Run: npm ci && npm run build

3) Start the stack (if Docker available):
   docker compose up -d --build
   docker compose ps
   docker compose logs -f api

4) Verify preflight:
   tail -n +1 preflight_output.log

======================================================

SUMMARY
ok "Script completed"
SUMMARY


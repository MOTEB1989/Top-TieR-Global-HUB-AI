#!/usr/bin/env bash
set -euo pipefail

REPORT="### 🤖 CodeX Auto-Report\n"
REPORT_FILE="codex_auto_report.log"

log_report() {
  local message=${1:-}
  REPORT+="$message\n"
}

log_report "🔧 CodeX Full System & Security Check Started"

# 1. Ensure required tools are available
if command -v apt-get >/dev/null 2>&1; then
  INSTALLER="apt-get"
  if command -v sudo >/dev/null 2>&1; then
    INSTALLER="sudo $INSTALLER"
  fi
  log_report "Installing required tools (jq, netcat-openbsd) if missing..."
  "$INSTALLER" update -y >/dev/null 2>&1 || log_report "⚠️ apt-get update failed"
  "$INSTALLER" install -y jq netcat-openbsd >/dev/null 2>&1 || log_report "⚠️ package installation failed"
else
  log_report "⚠️ apt-get not available; skipping package installation"
fi

# 2. Check if server is running on port 8000
if command -v nc >/dev/null 2>&1; then
  if nc -z localhost 8000 2>/dev/null; then
    log_report "✅ Server is running on port 8000"
  else
    log_report "❌ Server not responding on port 8000"
  fi
else
  log_report "⚠️ netcat (nc) not available to test port 8000"
fi

# 3. List key dependencies if present
if [[ -f requirements.txt ]]; then
  log_report "📦 Python dependencies detected (top 10):"
  mapfile -t py_deps < <(head -n 10 requirements.txt)
  for dep in "${py_deps[@]}"; do
    log_report "  - $dep"
  done
fi

if [[ -f package.json ]]; then
  if command -v jq >/dev/null 2>&1; then
    log_report "📦 NodeJS dependencies detected:"
    while IFS= read -r dep; do
      log_report "  $dep"
    done < <(jq -r '.dependencies // {} | to_entries[] | "- " + .key + "@" + .value' package.json)
  else
    log_report "⚠️ jq not available to list NodeJS dependencies"
  fi
fi

# 4. Check for common secrets in environment
for var in OPENAI_API_KEY DB_URL OPENSEARCH_URL MINIO_ENDPOINT REDIS_URL NEO4J_URI CLICKHOUSE_URL; do
  if [[ -n "${!var:-}" ]]; then
    log_report "🔑 $var is set"
  fi
done

# 5. Check GitHub workflow endpoints for http:// usage
if [[ -d .github/workflows ]]; then
  if command -v rg >/dev/null 2>&1; then
    if rg -n "http://" .github/workflows >/dev/null; then
      log_report "⚠️ Insecure HTTP endpoints found in workflows (use HTTPS)"
    else
      log_report "✅ All workflows endpoints use HTTPS"
    fi
  else
    if grep -R "http://" .github/workflows >/dev/null 2>&1; then
      log_report "⚠️ Insecure HTTP endpoints found in workflows (use HTTPS)"
    else
      log_report "✅ All workflows endpoints use HTTPS"
    fi
  fi
fi

# 6. Optionally comment on PR when running inside GitHub Actions
if [[ -n "${GITHUB_TOKEN:-}" && -f "${GITHUB_EVENT_PATH:-}" ]]; then
  pr_number=$(jq -r '.pull_request.number // empty' "$GITHUB_EVENT_PATH" 2>/dev/null || true)
  if [[ -n "$pr_number" ]]; then
    if command -v jq >/dev/null 2>&1; then
      jq -n --arg body "$REPORT" '{body: $body}' > pr_comment_payload.json
      curl -s -H "Authorization: token $GITHUB_TOKEN" \
        -X POST \
        -d @pr_comment_payload.json \
        "https://api.github.com/repos/$GITHUB_REPOSITORY/issues/$pr_number/comments" >/dev/null 2>&1 || \
        log_report "⚠️ Failed to post report comment to PR #$pr_number"
      rm -f pr_comment_payload.json
    else
      log_report "⚠️ jq required to format PR comment payload"
    fi
  fi
fi

# 7. Write report to file and stdout
printf "%b" "$REPORT" | tee "$REPORT_FILE"


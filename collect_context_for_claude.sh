#!/usr/bin/env bash
set -euo pipefail

# Veritas Nexus — Context Collector for Claude
# يجمع حالة المستودع والبنى، ويولّد ملفات:
#   - CLAUDE_CONTEXT.md  (نص منظم)
#   - CLAUDE_CONTEXT.json (هيكل بيانات)
# متطلبات اختيارية: jq, gh, docker, kubectl, python3, ruff, pytest

MD="CLAUDE_CONTEXT.md"
JSON="CLAUDE_CONTEXT.json"
TMP_JSON="$(mktemp)"
: > "$MD"; echo '{}' > "$JSON"

has(){ command -v "$1" >/dev/null 2>&1; }
add_json(){ # add_json key value_json
  jq -c --arg k "$1" --argjson v "$2" '. + {($k): $v}' "$JSON" > "$TMP_JSON" && mv "$TMP_JSON" "$JSON"
}
add_json_s(){ # add_json_s key "string"
  jq -c --arg k "$1" --arg v "$2" '. + {($k): $v}' "$JSON" > "$TMP_JSON" && mv "$TMP_JSON" "$JSON"
}

echo "# Veritas Nexus – Repository Context" >> "$MD"
DATE_UTC="$(date -u +%FT%TZ)"
echo "- Collected at: \`$DATE_UTC\` (UTC)" >> "$MD"

# --- Git meta ---
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'N/A')"
LAST="$(git log -1 --pretty=format:'%h %s (%cr) <%an>' 2>/dev/null || echo 'N/A')"
CHANGES="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
echo -e "\n## Git\n- Branch: \`$BRANCH\`\n- Last commit: $LAST\n- Local changes: $CHANGES" >> "$MD"
add_json_s "branch" "$BRANCH"; add_json_s "last_commit" "$LAST"; add_json_s "local_changes" "$CHANGES"

# --- Workflows & security config ---
echo -e "\n## Workflows & Governance" >> "$MD"
WF_LIST="$(ls -1 .github/workflows 2>/dev/null || true)"
echo -e "- Workflows:\n\`\`\`\n$WF_LIST\n\`\`\`" >> "$MD"
POST_MERGE=$(ls .github/workflows | grep -E '^post-merge-validation\.ya?ml$' || true)
echo "- Post-merge workflow present: $([ -n "$POST_MERGE" ] && echo yes || echo no)" >> "$MD"
[ -f .github/dependabot.yml ] && echo "- dependabot.yml: present" >> "$MD" || echo "- dependabot.yml: missing" >> "$MD"
[ -f CODEOWNERS ] && echo "- CODEOWNERS: present" >> "$MD" || echo "- CODEOWNERS: missing" >> "$MD"

add_json_s "post_merge_workflow" "$([ -n "$POST_MERGE" ] && echo "present" || echo "missing")"
add_json_s "dependabot" "$([ -f .github/dependabot.yml ] && echo "present" || echo "missing")"
add_json_s "codeowners" "$([ -f CODEOWNERS ] && echo "present" || echo "missing")"

# --- Secrets overview (names only if gh available) ---
echo -e "\n## Secrets (names only)" >> "$MD"
if has gh; then
  SEC=$(gh secret list --visibility=all 2>/dev/null || true)
  echo -e "\n\`\`\`\n$SEC\n\`\`\`" >> "$MD"
  add_json "secrets" "$(jq -nc --arg sec "$SEC" '{raw: $sec}')"
else
  echo "_Install GitHub CLI (gh) to list secret names safely._" >> "$MD"
fi

# --- Docker Compose overview ---
echo -e "\n## Docker Compose" >> "$MD"
if [ -f docker-compose.yml ]; then
  echo "- docker-compose.yml: present" >> "$MD"
  SRV=$(grep -E '^\s{2,}[A-Za-z0-9_.-]+:' -n docker-compose.yml | sed 's/^ *//')
  echo -e "  - Services:\n\`\`\`\n$SRV\n\`\`\`" >> "$MD"
  add_json "compose_services" "$(jq -nc --arg s "$SRV" '{raw: $s}')"
else
  echo "- docker-compose.yml: missing" >> "$MD"
  add_json_s "compose_services" "missing"
fi

# --- K8s manifests (rough scan) ---
echo -e "\n## Kubernetes Manifests" >> "$MD"
K8S_FILES=$(ls -1 *.yaml *.yml 2>/dev/null | grep -E '(deploy|service|neo4j|osint|core)' || true)
if [ -n "$K8S_FILES" ]; then
  echo -e "Found:\n\`\`\`\n$K8S_FILES\n\`\`\`" >> "$MD"
  add_json "k8s_files" "$(jq -nc --arg s "$K8S_FILES" '{raw: $s}')"
else
  echo "No K8s files detected." >> "$MD"
  add_json_s "k8s_files" "none"
fi

# --- APIs (OpenAPI presence) ---
echo -e "\n## APIs (OpenAPI files)" >> "$MD"
OPENAPI=$(ls -1 *openapi*.yaml *openapi*.yml 2>/dev/null || true)
[ -n "$OPENAPI" ] && echo -e "\`\`\`\n$OPENAPI\n\`\`\`" >> "$MD" || echo "No OpenAPI files detected." >> "$MD"
add_json "openapi_files" "$(jq -nc --arg s "$OPENAPI" '{raw: $s}')"

# --- Tests / Lint quick run (optional) ---
echo -e "\n## Local Checks" >> "$MD"
PYTEST_RESULT="skipped"; RUFF_RESULT="skipped"
if has pytest; then
  if pytest -q; then PYTEST_RESULT="passed"; else PYTEST_RESULT="failed"; fi
else PYTEST_RESULT="missing"; fi
if has ruff; then
  if ruff check .; then RUFF_RESULT="passed"; else RUFF_RESULT="failed"; fi
else RUFF_RESULT="missing"; fi
echo "- pytest: $PYTEST_RESULT" >> "$MD"
echo "- ruff:   $RUFF_RESULT" >> "$MD"
add_json_s "pytest" "$PYTEST_RESULT"; add_json_s "ruff" "$RUFF_RESULT"

# --- Health scripts if present ---
echo -e "\n## Health Scripts" >> "$MD"
for s in validate_security_improvements.sh stack_health_check.sh verify_repo_link.sh scripts/veritas_health_check.sh scripts/verify_openai.py; do
  [ -e "$s" ] && echo "- $s: present" >> "$MD" || echo "- $s: missing" >> "$MD"
done

# --- Last workflow runs (if gh) ---
echo -e "\n## Last CI run" >> "$MD"
if has gh; then
  LAST=$(gh run list --limit 1 --json name,status,conclusion,createdAt,updatedAt 2>/dev/null || true)
  echo -e "\`\`\`json\n$LAST\n\`\`\`" >> "$MD"
  add_json "last_run" "${LAST:-null}"
else
  echo "_Install gh to capture last run details._" >> "$MD"
fi

# --- Token/rate-limit hints (names only, no values) ---
echo -e "\n## Rate-limit & Tokens (expected names)" >> "$MD"
cat <<'EON' >> "$MD"
- OPENAI_API_KEY (LLM)
- NEO4J_USER / NEO4J_PASS (DB)
- SLACK_WEBHOOK_URL (notifications)
- PROVIDER_TOKENS for OSINT sources (Twitter/X, Reddit, GitHub…) — **names only**
EON

echo -e "\n---\n_Context ready for Claude. Upload/attach **CLAUDE_CONTEXT.md** (and JSON) إلى المحادثة._" >> "$MD"

echo "✓ Wrote $MD and $JSON"

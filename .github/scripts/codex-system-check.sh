#!/bin/bash
set -euo pipefail

shopt -s nullglob

REPO_NAME="${GITHUB_REPOSITORY:-Unknown repository}"
BRANCH_NAME="${GITHUB_REF:-Unknown branch}"

echo "🔧 CodeX System Check Started"
echo "Repository: ${REPO_NAME}"
echo "Branch: ${BRANCH_NAME}"

REPORT="### 🤖 CodeX Report\n"

if command -v nc >/dev/null 2>&1; then
  if nc -z localhost 8000 >/dev/null 2>&1; then
    REPORT+="✅ Server running on port 8000\n"
  else
    REPORT+="❌ Server not responding on port 8000\n"
  fi
else
  REPORT+="⚠️ netcat (nc) not installed - server status unknown\n"
fi

if [ -f "requirements.txt" ]; then
  REPORT+="📦 Python dependencies:\n"
  while IFS= read -r pkg; do
    [[ -z "$pkg" || "$pkg" == \#* ]] && continue
    REPORT+="- ${pkg}\n"
  done < requirements.txt
fi

if [ -f "pyproject.toml" ]; then
  REPORT+="📦 Python pyproject dependencies:\n"
  mapfile -t pyproject_deps < <(python - <<'PYINNER'
import sys
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    sys.exit(0)
from pathlib import Path
path = Path('pyproject.toml')
try:
    data = tomllib.loads(path.read_text())
except Exception:
    sys.exit(0)
project = data.get('project', {})
for dep in project.get('dependencies', []):
    print(dep)
PYINNER
)
  if (( ${#pyproject_deps[@]} )); then
    for dep in "${pyproject_deps[@]}"; do
      REPORT+="- ${dep}\n"
    done
  fi
fi

if [ -f "package.json" ] && command -v jq >/dev/null 2>&1; then
  REPORT+="📦 NodeJS dependencies:\n"
  while IFS= read -r dep; do
    REPORT+="${dep}\n"
  done < <(jq -r '.dependencies // {} | to_entries[] | "- " + .key + "@" + .value' package.json)
fi

workflow_keys_found=()
for workflow_file in .github/workflows/*.yml .github/workflows/*.yaml; do
  [ -e "$workflow_file" ] || continue
  if grep -q "OPENAI_API_KEY" "$workflow_file"; then
    workflow_keys_found+=("OPENAI_API_KEY")
  fi
  if grep -q "HUGGINGFACE" "$workflow_file"; then
    workflow_keys_found+=("HUGGINGFACE_API_KEY")
  fi
done

if (( ${#workflow_keys_found[@]} )); then
  mapfile -t unique_keys < <(printf '%s\n' "${workflow_keys_found[@]}" | sort -u)
  for key in "${unique_keys[@]}"; do
    REPORT+="🔑 Model connected: ${key} referenced in workflows\n"
  done
else
  REPORT+="ℹ️ No model API keys referenced in workflows\n"
fi

if grep -R -n --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir="venv" --exclude-dir=".venv" --exclude="*.lock" 'http://' . >/dev/null 2>&1; then
  REPORT+="⚠️ Insecure HTTP endpoints detected (use HTTPS)\n"
else
  REPORT+="✅ All endpoints use HTTPS (secure)\n"
fi

echo -e "$REPORT"

if [ -n "${GITHUB_TOKEN-}" ] && [ -f "${GITHUB_EVENT_PATH-}" ] && command -v jq >/dev/null 2>&1; then
  PR_NUMBER=$(jq -r '.pull_request.number // empty' "$GITHUB_EVENT_PATH")
  if [ -n "$PR_NUMBER" ]; then
    echo "Posting report to PR #${PR_NUMBER} ..."
    PAYLOAD=$(jq -n --arg body "$REPORT" '{body: $body}')
    curl -sS -H "Authorization: token ${GITHUB_TOKEN}" \
         -H "Content-Type: application/json" \
         -X POST \
         -d "$PAYLOAD" \
         "https://api.github.com/repos/${REPO_NAME}/issues/${PR_NUMBER}/comments" >/dev/null
  fi
fi

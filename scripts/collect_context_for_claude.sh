#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

OUTPUT_MD="CLAUDE_CONTEXT.md"
OUTPUT_JSON="CLAUDE_CONTEXT.json"

BRANCH="${GITHUB_REF_NAME:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')}"
COMMIT="$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

RECENT_COMMITS="$(git --no-pager log -5 --pretty=format:'%h %s (%an)' 2>/dev/null || true)"
CHANGED_FILES="$(git status --short 2>/dev/null || true)"

cat <<MD > "$OUTPUT_MD"
# Claude Context Snapshot

- Repository: $(basename "$REPO_ROOT")
- Branch: $BRANCH
- Commit: $COMMIT
- Generated: $TIMESTAMP (UTC)

## Recent Commits
MD

if [ -n "$RECENT_COMMITS" ]; then
  while IFS= read -r line; do
    echo "- $line" >> "$OUTPUT_MD"
  done <<< "$RECENT_COMMITS"
else
  echo "- No commit history available." >> "$OUTPUT_MD"
fi

cat <<MD >> "$OUTPUT_MD"

## Changed Files
MD

if [ -n "$CHANGED_FILES" ]; then
  while IFS= read -r line; do
    echo "- $line" >> "$OUTPUT_MD"
  done <<< "$CHANGED_FILES"
else
  echo "- No uncommitted changes detected." >> "$OUTPUT_MD"
fi

python - "$OUTPUT_JSON" <<'PY'
import json
import os
import subprocess
import sys

output_path = sys.argv[1]
repo = os.path.basename(os.getcwd())

branch = os.environ.get("GITHUB_REF_NAME")
if not branch:
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    ).stdout.strip() or "unknown"

commit = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    check=False,
).stdout.strip() or "unknown"

timestamp = subprocess.run(
    ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
    stdout=subprocess.PIPE,
    text=True,
    check=False,
).stdout.strip()

recent_proc = subprocess.run(
    ["git", "--no-pager", "log", "-5", "--pretty=format:%h %s (%an)"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    check=False,
)
recent = [line for line in recent_proc.stdout.splitlines() if line.strip()]

status_proc = subprocess.run(
    ["git", "status", "--short"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    check=False,
)
changed_files = [line for line in status_proc.stdout.splitlines() if line.strip()]

payload = {
    "repository": repo,
    "branch": branch,
    "commit": commit,
    "generated_at": timestamp,
    "recent_commits": recent,
    "changed_files": changed_files,
}

with open(output_path, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, indent=2)
    fh.write("\n")
PY

echo "Context files generated:"
ls -1 "$OUTPUT_MD" "$OUTPUT_JSON"

#!/bin/bash
set -euo pipefail

echo "🔧 CodeX Auto-Merge Script Started"
echo "Branch: main"

# عدد PRs في كل دفعة
BATCH_SIZE=20

# جلب PRs مفتوحة مرتبة حسب الأقل تغييرات (additions+deletions)
prs=$(gh pr list --state open --json number,additions,deletions \
  --jq 'sort_by(.additions + .deletions) | .[].number' | head -n $BATCH_SIZE)

if [ -z "$prs" ]; then
  echo "✅ No open PRs to process."
  exit 0
fi

echo "📌 Found PRs to merge (smallest changes first): $prs"

for pr in $prs; do
  echo "➡️ Trying to merge PR #$pr ..."
  if gh pr merge $pr --merge --auto; then
    echo "✅ Successfully merged PR #$pr"
  else
    echo "❌ Failed to merge PR #$pr"
    gh issue create \
      --title "Merge failed for PR #$pr" \
      --body "CodeX Bot failed to merge PR #$pr into main. Please check CI logs or conflicts."
  fi
done

echo "🎉 Batch merge finished. main is up-to-date!"

#!/bin/bash
set -euo pipefail

echo "🔧 CodeX Auto-Merge Started"
echo "Repository: $GITHUB_REPOSITORY"
echo "Branch: main"

REPORT="### 🤖 CodeX Auto-Merge Report\n"

# عدد PRs في كل دفعة
BATCH_SIZE=20

# جلب PRs مرتبة (الأحدث أولاً)
prs=$(gh pr list --state open --json number,title --jq '.[].number' | head -n $BATCH_SIZE)

if [ -z "$prs" ]; then
  REPORT+="✅ No open PRs found.\n"
else
  for pr in $prs; do
    echo "➡️ Attempting to merge PR #$pr ..."
    if gh pr merge $pr --squash --admin --auto; then
      REPORT+="✅ PR #$pr merged successfully\n"
    else
      REPORT+="❌ PR #$pr failed to merge\n"
      # محاولة إغلاق PR فاشل
      curl -s -X PATCH \
        -H "Authorization: token $GITHUB_TOKEN" \
        -d '{"state":"closed"}' \
        "https://api.github.com/repos/$GITHUB_REPOSITORY/pulls/$pr" \
        > /dev/null || true
      REPORT+="⚠️ PR #$pr was closed due to merge failure\n"
    fi
  done
fi

echo -e "$REPORT"

# كتابة التقرير في تعليق على Issue خاص بالتقارير
ISSUE_TITLE="CodeX Auto-Merge Summary"
EXISTING=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$GITHUB_REPOSITORY/issues?state=open" | jq -r ".[] | select(.title==\"$ISSUE_TITLE\") | .number")

if [ -n "$EXISTING" ]; then
  curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -X POST -d "{\"body\": \"$REPORT\"}" \
    "https://api.github.com/repos/$GITHUB_REPOSITORY/issues/$EXISTING/comments"
else
  curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -X POST -d "{\"title\": \"$ISSUE_TITLE\", \"body\": \"$REPORT\"}" \
    "https://api.github.com/repos/$GITHUB_REPOSITORY/issues"
fi


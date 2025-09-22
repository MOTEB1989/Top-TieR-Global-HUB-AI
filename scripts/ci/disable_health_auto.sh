#!/usr/bin/env bash
set -euo pipefail

# ===== إعدادات سريعة (عدّلها عند الحاجة) =====
REPO="MOTEB1989/Top-TieR-Global-HUB-AI"        # اسم المستودع owner/repo
BASE_BRANCH="main"                              # الفرع الأساسي
NEW_BRANCH="chore/disable-veritas-health-auto"  # الفرع الذي سيحمل التغيير
PR_TITLE="chore(ci): disable & remove Veritas Nexus • Health (Auto)"
PR_BODY=$'This PR disables the noisy **Veritas Nexus • Health (Auto)** workflow, removes its YAML, cancels running jobs, and closes legacy health-failure issues.\n\n- Disable workflow at server-side (state=disabled_manually)\n- Delete *.yml matching patterns\n- Cancel in-flight runs for those workflows\n- Close open issues with label: health-check + automation\n'

# أنماط أسماء ملفات الـ workflow المطلوب حذفها
# عدّل القائمة لو أردت تضمين/استبعاد أسماء أخرى
WORKFLOW_PATTERNS=(
  "veritas*health*auto*.yml"
  "*stack-health-check*.yml"
  "*health-check-openai*.yml"
)

# وسم/ملصقات القضايا القديمة المراد إغلاقها
ISSUE_MATCH_LABELS=("health-check" "automation")

# وضع تجريبي؟ true = جرّب فقط بدون تعديل
DRY_RUN="${DRY_RUN:-false}"

# ===== متطلبات =====
# - لازم تكون gh و git مثبتة
# - لازم يكون عندك صلاحية push و PR
# - لازم متغير GITHUB_TOKEN مضبوط (أو gh مسجّل دخول)

echo "Repository: $REPO"
echo "Base branch: $BASE_BRANCH"
echo "New branch:  $NEW_BRANCH"
echo "Dry-run:      $DRY_RUN"
echo

# جلب URL الـ repo عبر gh
REPO_URL=$(gh repo view "$REPO" --json url -q .url)

# إنشاء مساحة عمل مؤقتة
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT
cd "$TMPDIR"

echo "➡️  Cloning $REPO_URL ..."
git clone --depth=1 --branch "$BASE_BRANCH" "$REPO_URL" repo
cd repo

git config user.name  "codex-bot"
git config user.email "codex@example.local"

# إنشاء فرع
git checkout -b "$NEW_BRANCH"

# البحث عن ملفات الـ workflow المطابقة
echo "🔎 Searching workflow files to remove under .github/workflows/ ..."
FOUND=()
for pat in "${WORKFLOW_PATTERNS[@]}"; do
  while IFS= read -r -d '' f; do
    FOUND+=("$f")
  done < <(find .github/workflows -maxdepth 1 -type f -name "$pat" -print0 2>/dev/null || true)
done

# إزالة التكرارات
IFS=$'\n' FOUND=($(printf "%s\n" "${FOUND[@]}" | sort -u)); unset IFS

if [[ ${#FOUND[@]} -eq 0 ]]; then
  echo "ℹ️  No matching workflow files found."
else
  echo "🗑️  Will remove the following workflow files:"
  printf '  - %s\n' "${FOUND[@]}"
  if [[ "$DRY_RUN" != "true" ]]; then
    git rm -q "${FOUND[@]}"
  fi
fi

# محاولة تعطيل الـ workflows في GitHub (حتى لو الملف سيُحذف)
disable_workflow () {
  local name="$1"
  echo "⛔ Disabling workflow: $name"
  if [[ "$DRY_RUN" != "true" ]]; then
    gh workflow disable "$name" >/dev/null 2>&1 || true
  fi
}

# إلغاء أي تشغيلات حالية مطابقة
cancel_runs_for () {
  local name="$1"
  echo "🛑 Cancelling in-flight runs for: $name"
  if [[ "$DRY_RUN" != "true" ]]; then
    gh run list --workflow "$name" --limit 50 --json databaseId,status \
      -q '.[] | select(.status=="in_progress" or .status=="queued") | .databaseId' |
    xargs -r -n1 gh run cancel || true
  fi
}

# جرّب تعطيل/إلغاء أشهر أسماء محتملة
CANDIDATE_WORKFLOWS=(
  "Veritas Nexus • Health (Auto)"
  "stack-health-check.yml"
  "health-check-openai.yml"
  "veritas-health.yml"
)

for wf in "${CANDIDATE_WORKFLOWS[@]}"; do
  disable_workflow "$wf"
  cancel_runs_for "$wf"
done

# إن وُجدت تغييرات، ادفع فرعًا وافتح PR
if [[ "$DRY_RUN" == "true" ]]; then
  echo "🧪 Dry-run: skipping commit/push/PR."
else
  if ! git diff --cached --quiet; then
    git commit -m "chore(ci): disable & remove noisy health auto workflows"
    git push -u origin "$NEW_BRANCH"
    gh pr create --title "$PR_TITLE" --body "$PR_BODY" --base "$BASE_BRANCH" --head "$NEW_BRANCH" >/dev/null
    echo "✅ Pull Request opened."
  else
    echo "ℹ️  No file changes staged; skipping PR open."
  fi
fi

# إغلاق القضايا القديمة ذات الملصقات المحددة
echo "🧹 Closing legacy health-failure issues with labels: ${ISSUE_MATCH_LABELS[*]}"
LABEL_QUERY=$(printf "%s," "${ISSUE_MATCH_LABELS[@]}"); LABEL_QUERY="${LABEL_QUERY%,}"
if [[ "$DRY_RUN" != "true" ]]; then
  gh issue list --repo "$REPO" --state open --label "$LABEL_QUERY" --limit 200 --json number,title \
    -q '.[] | [.number, .title] | @tsv' |
  while IFS=$'\t' read -r num title; do
    echo "  - Closing #$num  ($title)"
    gh issue comment "$num" --repo "$REPO" \
      --body "Closed as part of disabling noisy health auto workflows. Replaced by the persistent monitor." >/dev/null || true
    gh issue close "$num" --repo "$REPO" >/dev/null || true
  done
fi

echo "🎉 Done."

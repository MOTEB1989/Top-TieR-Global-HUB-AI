#!/bin/bash
# execute_full_scan.sh - سكريبت تنفيذ كامل لفحص هيكل المستودع

set -e

# ==================== إعدادات ====================
GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null)}"
PR_NUMBER="1090"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "❌ GitHub Token غير موجود. استخدم:"
    echo 'export GITHUB_TOKEN="ghp_..."'
    exit 1
fi

# ==================== 1. إغلاق Issues/PRs القديمة ====================
echo "🔒 إغلاق جميع الـ Issues/PRs المفتوحة..."

# Close issues using array iteration to properly handle errors
mapfile -t issue_numbers < <(gh issue list --state open --json number -q '.[].number')
for num in "${issue_numbers[@]}"; do
    gh issue close "$num" --comment "🧹 Closed during full scan execution. Reopen if needed."
done

# Close PRs using array iteration to properly handle errors
mapfile -t pr_numbers < <(gh pr list --state open --json number -q '.[].number')
for num in "${pr_numbers[@]}"; do
    gh pr close "$num" --comment "🧹 Closed during full scan execution. Reopen if needed."
done

# ==================== 2. تحميل Pull Request ====================
echo "🔄 تحميل Pull Request #$PR_NUMBER..."
gh pr checkout "$PR_NUMBER"

# ==================== 3. تشغيل سكريبت الفحص ====================
echo "🔍 تشغيل سكريبت الفحص..."
python scripts/generate_repo_structure.py

# ==================== 4. إرسال النتائج ====================
echo "📤 إرسال نتائج الفحص..."

# Validate that repo_structure.json exists and is not empty
if [[ ! -f "repo_structure.json" ]]; then
    echo "❌ ملف repo_structure.json غير موجود"
    exit 1
fi

if [[ ! -s "repo_structure.json" ]]; then
    echo "❌ ملف repo_structure.json فارغ"
    exit 1
fi

# Validate JSON format
if ! python -m json.tool repo_structure.json > /dev/null 2>&1; then
    echo "❌ ملف repo_structure.json يحتوي على JSON غير صالح"
    exit 1
fi

gh pr comment "$PR_NUMBER" --body "### 📊 نتائج فحص هيكل المستودع
\`\`\`json
$(cat repo_structure.json)
\`\`\`"

echo "✅ التنفيذ اكتمل بنجاح!"

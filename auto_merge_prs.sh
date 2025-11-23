#!/bin/bash
# auto_merge_prs.sh - سكريبت دمج تلقائي مع التحقق وترتيب الطلبات

set -e

# ==================== إعدادات ====================
REPO="MOTEB1989/Top-TieR-Global-HUB-AI"
GITHUB_TOKEN="");GITHUB_TOKEN:-$(gh auth token 2>/dev/null)}"
MAIN_BRANCH="main"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "❌ GitHub Token غير موجود. استخدم:"
    echo 'export GITHUB_TOKEN="ghp_...}'
    exit 1
fi

# ==================== 1. ترتيب الطلبات ====================
echo "🔍 ترتيب الطلبات المفتوحة..."

# جلب الطلبات المفتوحة وترتيبها حسب الأرقام
OPEN_PRS=$(gh pr list --state open --json number,title,headRefName,baseRefName -q '.[] | {number, title, headRefName, baseRefName}' | jq -s 'sort_by(.number)')

# تحقق من وجود طلبات
if [[ -z "$OPEN_PRS" ]]; then
    echo "✅ لا يوجد طلبات مفتوحة."
    exit 0
fi

# ==================== 2. التحقق من كل طلب ====================
echo "🔍 التحقق من كل طلب..."

# تحقق من كل طلب قبل الدمج
jq -c '.[]' <<< "$OPEN_PRS" | while read PR; do
    PR_NUMBER=$(jq -r '.number' <<< "$PR")
    PR_TITLE=$(jq -r '.title' <<< "$PR")
    PR_HEAD_REF=$(jq -r '.headRefName' <<< "$PR")
    PR_BASE_REF=$(jq -r '.baseRefName' <<< "$PR")

    echo "🔍 التحقق من PR #$PR_NUMBER: $PR_TITLE"

    # التحقق من وجود الـ base branch
    if [[ "$PR_BASE_REF" != "$MAIN_BRANCH" ]]; then
        echo "⚠️ PR #$PR_NUMBER: base branch غير $MAIN_BRANCH"
        continue
    fi

    # التحقق من وجود الـ head branch
    if ! gh pr view "$PR_NUMBER" --json headRefName --jq '.headRefName' | grep -q "$PR_HEAD_REF"; then
        echo "⚠️ PR #$PR_NUMBER: head branch غير موجود"
        continue
    fi

    # التحقق من وجود الـ title
    if [[ -z "$PR_TITLE" ]]; then
        echo "⚠️ PR #$PR_NUMBER: عنوان الطلب غير موجود"
        continue
    fi

    echo "✅ PR #$PR_NUMBER: التحقق اكتمل بنجاح"
done

# ==================== 3. الدمج التلقائي ====================
echo "🚀 الدمج التلقائي..."

# دمج الطلبات المفتوحة
jq -c '.[]' <<< "$OPEN_PRS" | while read PR; do
    PR_NUMBER=$(jq -r '.number' <<< "$PR")
    PR_TITLE=$(jq -r '.title' <<< "$PR")

    echo "🚀 الدمج PR #$PR_NUMBER: $PR_TITLE"

    # الدمج
    gh pr merge "$PR_NUMBER" --auto --merge --delete-branch
done

echo "✅ الدمج التلقائي اكتمل بنجاح!"
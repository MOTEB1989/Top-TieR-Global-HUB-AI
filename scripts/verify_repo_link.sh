#!/usr/bin/env bash
set -euo pipefail

echo "🔍 التحقق من ربط المستودع ..."

# تحقق من الرابط البعيد (remote)
REMOTE_URL="$(git config --get remote.origin.url || true)"
if [[ -z "$REMOTE_URL" ]]; then
  echo "❌ لا يوجد remote مرتبط بهذا المستودع."
  exit 1
fi

echo "✅ Remote مرتبط: $REMOTE_URL"

# تحقق أن الرابط يشير إلى المستودع الصحيح
if [[ "$REMOTE_URL" != *"MOTEB1989/Top-TieR-Global-HUB-AI"* ]]; then
  echo "⚠️ تنبيه: الرابط الحالي لا يشير إلى Top-TieR-Global-HUB-AI"
else
  echo "🎯 الرابط صحيح يشير إلى Top-TieR-Global-HUB-AI"
fi

# تحقق من وجود CI Workflow
if [[ -f ".github/workflows/CI.yml" ]]; then
  echo "✅ Workflow CI.yml موجود"
else
  echo "❌ ملف CI.yml غير موجود"
fi

# فحص حالة آخر CI run عبر GitHub badge
check_ci_status() {
  echo "🔄 فحص حالة آخر CI run..."
  
  # محاولة الوصول لـ GitHub badge API
  local badge_url="https://img.shields.io/github/actions/workflow/status/MOTEB1989/Top-TieR-Global-HUB-AI/CI.yml?branch=main"
  local ci_response
  
  # محاولة جلب المحتوى مع timeout قصير
  ci_response=$(curl -s -m 10 --connect-timeout 5 "$badge_url" 2>/dev/null || echo "network_error")
  
  if [[ "$ci_response" == "network_error" ]]; then
    echo "⚠️ تعذر الوصول لحالة CI (تحقق من الاتصال بالإنترنت)"
    return
  fi
  
  # فحص محتوى SVG للحصول على الحالة
  if echo "$ci_response" | grep -q "passing\|success"; then
    echo "✅ حالة آخر CI: نجح"
  elif echo "$ci_response" | grep -q "failing\|failure\|error"; then
    echo "❌ حالة آخر CI: فشل"
  elif echo "$ci_response" | grep -q "pending\|running\|in_progress"; then
    echo "🔄 حالة آخر CI: قيد التشغيل"
  else
    echo "🔄 حالة آخر CI: غير محددة"
  fi
}

check_ci_status

# تحقق من Secrets الأساسية
echo ""
echo "ℹ️ تأكد من إضافة Secrets في GitHub:"
echo "   - OPENAI_API_KEY"
echo "   - (اختياري) DOCKER_USERNAME / DOCKER_PASSWORD"
echo "   - (اختياري) SLACK_WEBHOOK_URL"

echo ""
echo "✨ الفحص انتهى"
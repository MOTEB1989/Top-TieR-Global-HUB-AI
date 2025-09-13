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

# تحقق من Secrets الأساسية
echo "ℹ️ تأكد من إضافة Secrets في GitHub:"
echo "   - OPENAI_API_KEY"
echo "   - (اختياري) DOCKER_USERNAME / DOCKER_PASSWORD"
echo "   - (اختياري) SLACK_WEBHOOK_URL"

echo "✨ الفحص انتهى"
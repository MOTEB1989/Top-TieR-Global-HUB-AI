#!/usr/bin/env bash
set -euo pipefail

# ============ Veritas Platinum Upgrade ============

mkdir -p policies evals datasets scripts .github/workflows .github/ISSUE_TEMPLATE .github/PULL_REQUEST_TEMPLATE logs

# -------- 1) سياسات ودرع السلامة --------
cat > policies/guardrails.yaml <<'YML'
version: 1
disclaimer:
  osint: "تحذير: تحليل OSINT لمعلومات متاحة علنًا؛ ليست بديلاً للتحقق الرسمي."
  medical: "تنبيه طبي: معلومات تعليمية؛ ليست نصيحة طبية أو تشخيصًا."
  realestate: "تنبيه عقاري: معلومات سوقية استرشادية؛ ليست استشارة قانونية/تمويلية."
  legal: "تنبيه قانوني: تحليل عام؛ ليس استشارة قانونية."
pii_redaction:
  patterns:
    - name: saudi_phone
      regex: "(?<!\\d)(?:\\+?966|0)5\\d{8}(?!\\d)"
      replace: "[REDACTED_PHONE]"
    - name: email
      regex: "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
      replace: "[REDACTED_EMAIL]"
output_contract:
  require_citations: true
  require_confidence: true
  require_trace: true
  format:
    order: [summary, evidence, gaps, next_action, disclaimer, trace]
YML

cat > policies/router.json <<'JSON'
{
  "domains": {
    "osint": { "allow_tools": ["hibp","intelx","search"], "hard_disclaimer": true },
    "medical": { "allow_tools":...
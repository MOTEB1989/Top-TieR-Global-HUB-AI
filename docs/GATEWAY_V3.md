# Gateway V3 – AI Review Layer

هذه الطبقة توفّر بوابة موحدة لتحليل الملفات باستخدام نماذج متعددة (OpenAI / Groq / Azure / Local).

## 🎯 الأهداف

- واجهة واحدة لتحليل الملفات متعددة الأنواع.
- دعم مهام مختلفة (مراجعة كود، تحليل قانوني، مصرفي، طبي، تقني، أو مراجعة مستندات عامة).
- إخراج Markdown جاهز للاستخدام في تقارير أو تعليقات Pull Requests.

## 🧱 المكوّنات

- `gateway.py`  
  نقطة الدخول الرئيسية (CLI) التي:
  - تحدد نوع الملف والمهمة.
  - تحمّل الـ prompts من مجلد `ai_prompts/`.
  - تستدعي مزود النموذج المحدد في متغير البيئة `PROVIDER`.
  - تطبع Markdown إلى stdout.

- مجلد `ai_prompts/`  
  يحتوي قوالب جاهزة لكل مهمة:
  - `review_code.txt`
  - `legal_analysis.txt`
  - `medical_info.txt`
  - `tech_trends.txt`
  - `banking_compliance.txt`
  - `document_analysis.txt`

## ⚙️ الإعداد

### متغيرات البيئة

- `PROVIDER` = `openai` أو `groq` أو `azure` أو `local` (الافتراضي: `openai`).
- `OPENAI_API_KEY`, `OPENAI_MODEL` (اختياري، الافتراضي: `gpt-4o-mini`).
- `GROQ_API_KEY`, `GROQ_MODEL` (الافتراضي: `mixtral-8x7b-32768`).
- `AZURE_OPENAI_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`.
- `LOCAL_MODEL_ENDPOINT` لاستدعاء نموذج محلي عبر HTTP.

## 🚀 أمثلة تشغيل

### مراجعة ملف README:

```bash
PROVIDER=openai OPENAI_API_KEY=... python gateway.py --task document --file README.md

مراجعة كود Python تلقائيًا:

PROVIDER=groq GROQ_API_KEY=... python gateway.py --task auto --file services/api_server/main.py

استخدام نموذج محلي عبر HTTP:

export PROVIDER=local
export LOCAL_MODEL_ENDPOINT=http://localhost:11434/v1/lex-gateway
python gateway.py --task auto --file some_file.md

🚨 القيود والمحددات
•يفضل أن تكون الملفات أقل من ~10KB للحصول على أداء واستقرار أفضل.
•يخضع الاستخدام لحدود الطلبات (Rate Limits) الخاصة بكل مزود.
•المخرجات تميل إلى اللغة العربية افتراضيًا في الشرح والتحليل.

🔧 استكشاف الأخطاء

مشكلة: “فشل استدعاء النموذج”

تحقق من:
1.صحة مفاتيح الـ API في .env أو Secrets.
2.اتصال الشبكة من البيئة إلى مزود الخدمة.
3.عدم تجاوز حدود الاستخدام أو الحصة.

مشكلة: “تعذّر تحميل الـprompt”

تأكد من:
•وجود مجلد ai_prompts/ في جذر المستودع بجوار gateway.py.
•وجود الملفات الستة بأسمائها الصحيحة.

🧪 الاختبارات المقترحة
•إضافة ملف tests/test_gateway_v3.py لاختبار:
•التعامل مع ملفات فارغة.
•التعامل مع ملف كبير (يتم قطع النص في الاختبارات).
•التعامل مع امتداد غير مدعوم.
•اكتشاف مهام متعددة (مثلاً: قانوني + مصرفي في نص واحد).

8.Create/overwrite file: .github/workflows/ai-gateway-reviewer.yml

⸻

name: AI Gateway Reviewer

on:
pull_request:
types: [opened, synchronize, reopened]

jobs:
gateway-review:
runs-on: ubuntu-latest
env:
OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
PROVIDER: ${{ secrets.AI_REVIEW_PROVIDER }}
steps:
- name: Checkout
uses: actions/checkout@v4

  - name: Get changed files
    id: changes
    run: |
      git fetch origin ${{ github.base_ref }}
      git diff --name-only origin/${{ github.base_ref }} > changed_files.txt
      cat changed_files.txt

  - name: Validate readable files
    run: |
      while IFS= read -r file; do
        if [ ! -f "$file" ]; then
          echo "⚠️ Cannot read (not a file): $file"
        fi
      done < changed_files.txt

  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: "3.11"

  - name: Install gateway dependencies
    run: |
      python -m pip install --upgrade pip
      pip install requests PyPDF2 python-docx

  - name: Run AI Gateway on changed files
    timeout-minutes: 15
    run: |
      mkdir -p ai_review_output
      if [ ! -s changed_files.txt ]; then
        echo "No changed files detected." > ai_review_output/review.md
      else
        while IFS= read -r file; do
          if [ -f "$file" ]; then
            echo "=== Analyzing: $file ==="
            python gateway.py --task auto --file "$file" >> ai_review_output/review.md 2>&1 || true
            echo -e "\n\n---\n\n" >> ai_review_output/review.md
          fi
        done < changed_files.txt
      fi

  - name: Upload AI Review Artifact
    uses: actions/upload-artifact@v4
    with:
      name: ai-gateway-review
      path: ai_review_output/review.md

9.Create/overwrite file: .github/workflows/auto-health-fix.yml

⸻

name: Auto Health Diagnostics

on:
workflow_dispatch:
schedule:
- cron: “0 3 * * *”  # daily at 03:00 UTC

jobs:
health-check:
runs-on: ubuntu-latest
env:
GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
steps:
- name: Checkout
uses: actions/checkout@v4

  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: "3.11"

  - name: Install dependencies
    run: |
      python -m pip install --upgrade pip
      pip install requests

  - name: Run system diagnostics
    id: diag
    run: |
      mkdir -p health_reports
      python scripts/system_diagnose_and_fix.py | tee health_reports/latest_health_report.md

  - name: Run auto-fix engine (suggestions only)
    run: |
      python scripts/auto_fix_engine.py > health_reports/auto_fix_suggestions.md

  - name: Upload health artifacts
    uses: actions/upload-artifact@v4
    with:
      name: system-health-report
      path: health_reports/

  - name: Telegram notification (optional)
    if: env.TELEGRAM_BOT_TOKEN != '' && env.TELEGRAM_CHAT_ID != ''
    run: |
      python scripts/telegram_notifier.py "✅ System health diagnostics finished for ${{ github.repository }} on ref ${{ github.ref }}."

Notes:
•Ensure all directories exist (scripts/, ai_prompts/, docs/, .github/workflows/).
•Do not remove or modify existing project logic; this patch is additive.
•After applying changes, run a quick syntax check locally:
•python -m py_compile gateway.py
•python -m py_compile scripts/system_diagnose_and_fix.py
•python -m py_compile scripts/auto_fix_engine.py
•python -m py_compile scripts/telegram_notifier.py
•python -m py_compile scripts/collect_ai_bot_feedback.py

Finally, show me the diff summary and any notes if some paths already existed and had to be merged instead of overwritten.

---

بهذا الأمر الواحد:

- تكمّل كل النواقص التي اشتكى منها Codex في تقرير “Run structural validation”.
- تربط بين:
  - Gateway V3
  - سكربتات الصحّة والتشخيص
  - مجلد الـ prompts
  - التنبيهات عبر تيليجرام
  - Workflows CI التي تشغل كل ذلك.

بعدما ينفّذ Codex هذا الأمر ويعطيك ملخص الـ diff، شاركني فقط:

- سطر أو سطرين من ملخص التغييرات  
أو صورة مثل السابقة، وسنعتبر أن “البنية النهائية” أصبحت جاهزة لمراحل Phase 6 (Observability / Multi-Modal).

# تعليمات اختبار PR #264 - نظام تنظيف المستودع التلقائي

## نظرة عامة على التغييرات
تضيف هذه المراجعة (PR #264) نظام تنظيف متطور للمستودع يتضمن:

1. **سكريبت Python محسن** (`scripts/close_github_items.py`) لإغلاق الـ Issues والـ Pull Requests
2. **GitHub Actions Workflow** (`.github/workflows/cleanup.yml`) مع واجهة مستخدم عربية
3. **نظام أمان متقدم** مع خيارات تصفية وحماية

## المتطلبات التقنية

### البيئة المطلوبة:
- Python 3.11 أو أحدث
- مكتبة `requests` (الإصدار 2.32.4 أو أحدث)
- GitHub Token مع صلاحيات:
  - `issues: write`
  - `pull-requests: write`
  - `contents: read`

### إعداد البيئة:
```bash
# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة الافتراضية
# على Windows:
venv\Scripts\activate
# على macOS/Linux:
source venv/bin/activate

# تثبيت المتطلبات
pip install requests

# إعداد GitHub Token
export GITHUB_TOKEN="your_token_here"
```

## اختبار السكريبت محليًا

### 1. اختبار الوضع الآمن (Dry Run) - **مطلوب أولاً**

```bash
# اختبار أساسي للوضع الآمن
python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI --dry-run --yes

# اختبار مع تصفية التواريخ
python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI \
  --dry-run --yes --before 2024-01-01

# اختبار مع استثناء أرقام محددة
python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI \
  --dry-run --yes --exclude 1 2 3

# اختبار مع استثناء التسميات (Labels)
python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI \
  --dry-run --yes --label-exclude priority keep wontfix
```

### 2. اختبار تخطي أنواع العناصر

```bash
# تخطي الـ Issues فقط
python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI \
  --dry-run --yes --skip-issues

# تخطي الـ Pull Requests فقط
python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI \
  --dry-run --yes --skip-prs
```

### 3. اختبار معالجة الأخطاء

```bash
# اختبار مع token غير صحيح
GITHUB_TOKEN="invalid_token" python scripts/close_github_items.py \
  MOTEB1989/Top-TieR-Global-HUB-AI --dry-run --yes

# اختبار مع مستودع غير موجود
python scripts/close_github_items.py nonexistent/repo \
  --dry-run --yes
```

## اختبار GitHub Actions Workflow

### 1. اختبار التشغيل اليدوي (Manual Dispatch)

#### خطوات الاختبار:
1. **انتقل إلى تبويب Actions في GitHub**
   ```
   https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/actions
   ```

2. **اختر "Repository Hygiene - Close Old Issues & PRs"**

3. **اختبر الخيارات العربية:**

   **وضع التشغيل (Execution mode):**
   - اختبر `dry-run = لا يغلق فعلياً` ✅ (آمن)
   - اختبر `execute = إغلاق حقيقي` ⚠️ (خطر - استخدم بحذر)

   **خيارات التخطي:**
   - `تخطي إغلاق الـ Issues` - اختبر تشغيله وإيقافه
   - `تخطي إغلاق الـ Pull Requests` - اختبر تشغيله وإيقافه

   **تصفية التواريخ:**
   - `أغلق العناصر الأقدم من هذا التاريخ فقط (YYYY-MM-DD)`
   - اختبر مع: `2024-01-01`, `2023-12-31`, تاريخ فارغ

   **استثناء الأرقام:**
   - `أرقام Issues/PRs مفصولة بمسافات لاستثنائها`
   - اختبر مع: `1 2 3`, `264`, قيمة فارغة

   **استثناء التسميات:**
   - `استثناء العناصر التي تحتوي على هذه التسميات`
   - اختبر مع: `priority keep wontfix`, `bug feature`, قيمة فارغة

### 2. اختبار التشغيل المجدول (Scheduled Run)

#### محاكاة التشغيل المجدول:
```bash
# لن يتم تشغيل هذا فعليًا لأنه مجدول، لكن يمكن محاكاته
# بتشغيل manual dispatch مع إعدادات مماثلة للـ schedule
```

**الإعدادات المتوقعة للتشغيل المجدول:**
- وضع: `dry-run` (دائماً للأمان)
- `skip_issues`: `false`
- `skip_prs`: `false`
- `label_exclude`: `priority keep wontfix`

## سيناريوهات الاختبار المتقدمة

### 1. اختبار Rate Limiting
```bash
# قم بتشغيل السكريبت عدة مرات متتالية لاختبار معالجة Rate Limit
for i in {1..5}; do
  echo "اختبار رقم $i"
  python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI \
    --dry-run --yes
  sleep 2
done
```

### 2. اختبار نظام إعادة المحاولة (Retry Logic)
```bash
# اختبار مع انقطاع إنترنت مؤقت (محاكاة)
# سيقوم السكريبت بإعادة المحاولة تلقائياً
python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI \
  --dry-run --yes
```

### 3. اختبار التصفية المتقدمة
```bash
# اختبار دمج عدة مرشحات
python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI \
  --dry-run --yes \
  --before 2024-06-01 \
  --exclude 264 265 266 \
  --label-exclude priority bug critical
```

## معايير النجاح

### ✅ السكريبت يعمل بشكل صحيح إذا:
1. **الوضع الآمن (Dry Run):**
   - يعرض قائمة بالعناصر المرشحة للإغلاق
   - لا يغلق أي شيء فعلياً
   - يظهر تقرير نهائي صحيح

2. **معالجة الأخطاء:**
   - يتعامل مع tokens غير صحيحة بشكل لائق
   - يعيد المحاولة عند انقطاع الاتصال
   - يتعامل مع Rate Limits بطريقة صحيحة

3. **نظام التصفية:**
   - يحترم تصفية التواريخ
   - يستثني الأرقام المحددة
   - يتجاهل العناصر ذات التسميات المستثناة

### ✅ GitHub Actions Workflow يعمل بشكل صحيح إذا:
1. **الواجهة العربية:**
   - جميع الأوصاف تظهر بالعربية بشكل صحيح
   - الخيارات تعمل كما هو متوقع
   - القيم الافتراضية صحيحة

2. **نظام الأمان:**
   - التشغيل المجدول يستخدم `dry-run` دائماً
   - التشغيل اليدوي يحترم الخيارات المحددة
   - العناصر ذات التسميات الحساسة محمية

3. **التقارير:**
   - يُظهر الأوامر المنفذة بوضوح
   - يُبين النتائج والملخص
   - يوضح وضع التشغيل (DRY-RUN أم EXECUTION)

## تحذيرات الأمان ⚠️

### 🚨 احذر عند:
1. **استخدام وضع `execute`** - سيغلق العناصر فعلياً!
2. **عدم استخدام `--exclude`** لاستثناء PRs/Issues مهمة
3. **تشغيل الـ workflow على مستودعات production**
4. **عدم مراجعة قائمة العناصر في dry-run أولاً**

### 🛡️ ممارسات آمنة:
1. **ابدأ دائماً بـ `--dry-run`**
2. **راجع القائمة قبل التنفيذ الفعلي**
3. **استخدم `--exclude` للعناصر المهمة**
4. **احتفظ بنسخة احتياطية من البيانات المهمة**

## مؤشرات الأداء

### قياس الأداء:
```bash
# قياس وقت التنفيذ
time python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI \
  --dry-run --yes

# مراقبة استخدام Memory
top -p $(pgrep -f close_github_items.py)
```

### النتائج المتوقعة:
- **الوقت:** أقل من 30 ثانية لمستودع بـ 200+ issue/PR
- **الذاكرة:** أقل من 50MB
- **معدل API calls:** يحترم GitHub rate limits

## استكشاف الأخطاء وإصلاحها

### المشاكل الشائعة:

1. **"A GitHub token is required"**
   ```bash
   # الحل: تأكد من إعداد GITHUB_TOKEN
   echo $GITHUB_TOKEN  # يجب أن يظهر القيمة
   export GITHUB_TOKEN="your_token_here"
   ```

2. **"HTTP 403 Forbidden"**
   ```bash
   # الحل: تحقق من صلاحيات Token
   # يجب أن يتضمن: repo, issues, pull_requests
   ```

3. **"No module named 'requests'"**
   ```bash
   # الحل: تثبيت المتطلبات
   pip install requests
   ```

4. **الواجهة العربية لا تظهر بشكل صحيح**
   - تأكد من إعدادات UTF-8 في المتصفح
   - راجع إعدادات GitHub language settings

## التقرير النهائي

عند اكتمال الاختبار، يجب أن تحصل على:

✅ **تقرير ناجح يحتوي على:**
- عدد العناصر المُغلقة: X
- عدد العناصر المُتخطاة: Y
- وضع التشغيل: DRY-RUN أو EXECUTION
- وقت التنفيذ: Z ثانية
- معدل نجاح API calls: 100%

**مثال على تقرير ناجح:**
```
Summary:
  Closed:  0
  Skipped: 15
  Mode:    DRY-RUN

✅ Repository hygiene cleanup completed
Mode: dry-run
Repository: MOTEB1989/Top-TieR-Global-HUB-AI
⚠️ This was a DRY RUN - no actual changes were made
```

---

**ملاحظة:** هذه التعليمات مصممة لضمان اختبار شامل وآمن لنظام تنظيف المستودع مع دعم كامل للغة العربية في الواجهات والتوثيق.
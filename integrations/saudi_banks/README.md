# Saudi Banks API Integration

تكامل API للبنوك السعودية مع نظام مكافحة غسل الأموال والذكاء الاصطناعي.

## المميزات

- **فحص KYC للعملاء**: التحقق من توثيق مصدر الأموال
- **إدارة قواعد القرار**: إضافة وإدارة قواعد AML/CFT
- **تقييم المعاملات**: تحليل المعاملات وإنشاء التنبيهات
- **تحليل بالذكاء الاصطناعي**: اكتشاف الأنماط الشاذة باستخدام Isolation Forest
- **إدارة التنبيهات**: عرض وتتبع التنبيهات الأمنية

## التشغيل السريع

### 1. تثبيت المتطلبات
```bash
pip install flask scikit-learn numpy pandas
```

### 2. إنشاء قاعدة البيانات
```bash
cd integrations/saudi_banks
sqlite3 saudi_banks.db < saudi_banks_init.sql
```

### 3. تشغيل السيرفر
```bash
python app.py
```

السيرفر سيعمل على: `http://localhost:5005`

## نقاط النهاية (API Endpoints)

### صحة النظام
```http
GET /health
```

### بيانات KYC للعميل
```http
GET /customer/{customer_id}
```

### إضافة قاعدة قرار
```http
POST /decision-rule
Content-Type: application/json

{
  "rule_id": "rule_001",
  "description": "وصف القاعدة",
  "conditions": {"transaction.amount": ">500000"},
  "action": {"type": "report", "urgency": "high"},
  "metadata": {"source": "لائحة مكافحة غسل الأموال"}
}
```

### تقييم معاملة
```http
POST /transaction
Content-Type: application/json

{
  "transaction": {
    "type": "international_transfer",
    "amount": 600000
  },
  "kyc": {
    "source_of_funds": false
  }
}
```

### عرض التنبيهات
```http
GET /alerts
```

### تحليل بالذكاء الاصطناعي
```http
POST /ai/analyze
Content-Type: application/json

{
  "transactions": [
    {"transaction": {"amount": 50000}},
    {"transaction": {"amount": 150000}}
  ]
}
```

### اقتراح قواعد جديدة
```http
GET /ai/suggest-rules
```

## قاعدة البيانات

يتضمن النظام الجداول التالية:
- `circulars`: التعاميم التنظيمية
- `decision_rules`: قواعد اتخاذ القرار
- `alerts_log`: سجل التنبيهات
- `kyc_data`: بيانات KYC للعملاء

## بيانات الاختبار

يتضمن النظام بيانات اختبارية:
- عميل تجريبي: `cust123` (بدون توثيق مصدر أموال)
- قاعدة AML: تحويل دولي > 500,000 ريال بدون KYC
- تعميم من ساما كمثال

## الأمان والامتثال

- النظام متوافق مع لوائح ساما لمكافحة غسل الأموال
- يدعم النصوص العربية كاملاً
- تسجيل شامل للأحداث والمعاملات
- تحليل ذكي للأنماط الشاذة
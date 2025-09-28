# Saudi Banks API (Flask)

## المتطلبات
- Python 3.10+
- SQLite3

## تثبيت الحزم
```bash
pip install -r integrations/saudi_banks/requirements.txt
```

## تهيئة قاعدة البيانات
```bash
sqlite3 saudi_banks.db < saudi_banks_init.sql
```

تحقق من الجداول:
```bash
sqlite3 saudi_banks.db ".tables"
# النتيجة المتوقعة:
# alerts_log  circulars  decision_rules  kyc_data
```

## التشغيل
```bash
python integrations/saudi_banks/app.py
# Listening on 0.0.0.0:5005
```

## اختبارات سريعة
- الصحة:
```bash
curl -s http://localhost:5005/health
```

- جلب KYC:
```bash
curl -s http://localhost:5005/customer/cust123
```

- إضافة قاعدة قرار:
```bash
curl -s -X POST http://localhost:5005/decision-rule \
  -H "Content-Type: application/json" \
  -d '{
    "rule_id":"aml_intl_transfer_500k_no_kyc",
    "description":"تحويل دولي يتجاوز 500,000 ريال دون توثيق مصدر الأموال",
    "conditions":{"transaction.type":"international_transfer","transaction.amount":">500000","kyc.source_of_funds":false},
    "action":{"type":"report","target":"SAFIU","urgency":"immediate"},
    "metadata":{"domain":"AML/CFT"}
  }'
```

- تقييم معاملة:
```bash
curl -s -X POST http://localhost:5005/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "transaction":{"type":"international_transfer","amount":600000},
    "kyc":{"source_of_funds":false}
  }'
```

- مقترحات القواعد من AI:
```bash
curl -s -X POST http://localhost:5005/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"transactions":[{"transaction":{"amount":120000}}]}'
```

```bash
curl -s http://localhost:5005/ai/suggest-rules
```


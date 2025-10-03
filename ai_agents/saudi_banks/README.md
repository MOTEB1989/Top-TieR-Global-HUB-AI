# 🏦 Saudi Banks – نموذج التحليل المالي الذكي 🇸🇦💰

تم تفعيل التكامل مع المستودع الحي، مما يجعل Saudi Banks قادرًا على تحليل الكود المالي، لوائح الالتزام، والاستراتيجيات البنكية المضمنة داخل ملفات المشروع.

## ✅ القدرات المفعّلة:

- 🔍 تحليل مباشر للملفات المالية داخل المستودع (.py, .json)
- 🧾 التحقق من بنود الالتزام المصرفي والمطابقة التنظيمية
- 📡 الاتصال الحي بـ Codex Gateway: [https://api.lexcode.ai/v1/lex/run](https://api.lexcode.ai/v1/lex/run)
- 🔁 تسجيل كل عملية تحليل في سجل استعلامات دائم (Audit Log)

## 🛠️ مثال على التكامل عبر الأداة:

```yaml
tools:
  - name: CodexRepoFeeder
    url: https://api.lexcode.ai/v1/lex/run
    method: POST
    description: |
      تحليل ملفات المستودع المالية والقانونية وربطها بالنموذج عبر Gateway حي.
    schema:
      type: object
      properties:
        task:
          type: string
          enum: [explain, audit, finance-check]
        file_path:
          type: string
```

## 💬 مثال استدعاء مباشر:

```bash
curl -X POST https://api.lexcode.ai/v1/lex/run \
  -H "Content-Type: application/json" \
  -d '{"task": "finance-check", "file_path": "ai_agents/saudi_banks/bank_compliance.py"}'
```

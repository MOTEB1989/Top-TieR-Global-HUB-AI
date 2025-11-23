# Docker Build Fix - November 23, 2025

## المشكلة
كان بناء Docker يفشل مع الخطأ:
```
error TS18003: No inputs were found in config file '/app/tsconfig.json'. 
Specified 'include' paths were '["src"]' and 'exclude' paths were '["/app/dist"]'.
```

## السبب
- ملفات TypeScript كانت في الجذر وليس في مجلد `src/`
- `tsconfig.json` كان يبحث عن `src/` غير الموجود

## الإصلاحات المنفذة

### 1. إعادة تنظيم البنية
```
قبل:
/
├── index.ts
├── ai.ts
├── openai.ts
└── tsconfig.json

بعد:
/
├── src/
│   ├── index.ts
│   └── providers/
│       ├── ai.ts
│       └── openai.ts
└── tsconfig.json
```

### 2. تحسين Dockerfile
- استخدام `npm ci` بدلاً من `npm install`
- نسخ الملفات المطلوبة فقط
- إضافة Health Check
- تحسين الطبقات للاستفادة من Cache

### 3. إضافة endpoint `/health`
أضفنا endpoint بسيط للـ health check:
```typescript
app.get('/health', (_req, res) => {
  res.json({ 
    status: 'ok', 
    service: 'lexcode-api', 
    timestamp: new Date().toISOString() 
  });
});
```

### 4. تحسين .dockerignore
إنشاء ملف `.dockerignore` شامل لتقليل حجم الصورة

## كيفية البناء الآن

```bash
# بناء محلي
npm run build

# بناء Docker
docker build -t lexcode-api .

# بناء مع docker-compose
docker-compose -f docker-compose.full.yml build
```

## النتيجة
✅ البناء يعمل الآن بنجاح
✅ البنية منظمة ومتوافقة مع معايير TypeScript
✅ حجم الصورة أصغر بفضل .dockerignore
✅ Health check جاهز للاستخدام

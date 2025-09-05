# Veritas Console (Bootstrap)

كونسول أوامر موحّد + API خفيف + Docker + Workflows جاهزة.

## تشغيل محلي
```bash
python veritas_console.py analyze --domain osint --target "+9665XXXXXXX" --scope deep --depth advanced

تشغيل كـ API

uvicorn api_server:app --reload

POST /run:

{"command":"analyze","domain":"osint","target":"+9665XXXXXXX","scope":"deep","depth":"advanced","sources":"auto"}

Actions
	•	Run Console: تشغيل أمر ورفع out.json كـ artifact.
	•	Deploy to GHCR: بناء ودفع docker إلى ghcr.io باستخدام GITHUB_TOKEN.
	•	Bootstrap-Veritas: توليد/تحديث ملفات أساسية تلقائيًا.

نصيحة: فعّل Actions permissions = Read & write من Settings → Actions.

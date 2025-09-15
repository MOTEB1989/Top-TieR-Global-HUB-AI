# -*- coding: utf-8 -*-
"""
تحقق سريع من توافر OPENAI_API_KEY واستدعاء API خفيف.
- يطبع 6 أحرف مقنعة من المفتاح للتأكد من تحميله.
- يجرب طلب GET إلى /v1/models (خيار آمن وخفيف).
"""
import os, json, sys, time
import urllib.request

key = os.environ.get("OPENAI_API_KEY", "")
if not key:
    print("❌ OPENAI_API_KEY is not set in env", file=sys.stderr)
    sys.exit(1)

masked = key[:3] + "…" + key[-3:] if len(key) >= 6 else "•••"
print(f"🔐 OPENAI_API_KEY present: {masked}")

# اختبار اتصال خفيف — يمكن تعطيله إن لم ترغب في استهلاك API
req = urllib.request.Request(
    "https://api.openai.com/v1/models",
    headers={"Authorization": f"Bearer {key}"},
    method="GET",
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        status = r.getcode()
        print(f"🌐 OpenAI API reachable (HTTP {status})")
        # لا نطبع القائمة كاملة لتجنب الضوضاء
        sys.exit(0 if status == 200 else 1)
except Exception as e:
    print(f"⚠️  OpenAI API check failed: {e}", file=sys.stderr)
    # لا نفشل الـ job لو أردته اختياريًا: غيّر القيمة لـ 0 لو تحب عدم الإيقاف
    sys.exit(1)

"""
تحقق خفيف من وجود OPENAI_API_KEY وإمكانية الاتصال بنقطة نماذج OpenAI.
- لا يطبع المفتاح (يعرض 3 أحرف من البداية والنهاية فقط).
- يكتفي بطلب GET إلى /v1/models (أخف وأأمن).
"""
import json  # noqa: F401
import os
import sys
import urllib.request

key = os.environ.get("OPENAI_API_KEY", "")
if not key:
    print("❌ OPENAI_API_KEY غير مضبوط في بيئة التشغيل.", file=sys.stderr)
    sys.exit(1)

masked = f"{key[:3]}…{key[-3:]}" if len(key) >= 6 else "•••"
print(f"🔐 المفتاح موجود: {masked}")

req = urllib.request.Request(
    "https://api.openai.com/v1/models",
    headers={"Authorization": f"Bearer {key}"},
    method="GET",
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        code = r.getcode()
        print(f"🌐 OpenAI API reachable (HTTP {code})")
        # نجاح فقط لو الحالة 200
        sys.exit(0 if code == 200 else 1)
except Exception as e:
    print(f"⚠️ فشل فحص OpenAI: {e}", file=sys.stderr)
    sys.exit(1)

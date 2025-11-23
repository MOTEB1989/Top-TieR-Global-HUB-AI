#!/usr/bin/env python3
"""
scripts/test_telegram_bot.py
Simple checker to validate presence/form of required env vars.
Does not print secret values.
"""
import os, sys
reqs = [
    "OPENAI_API_KEY","TELEGRAM_BOT_TOKEN","TELEGRAM_ALLOWLIST","GITHUB_TOKEN","GITHUB_REPO"
]
ok = []
miss = []
for k in reqs:
    v = os.getenv(k, "")
    if v:
        ok.append((k, len(v)))
    else:
        miss.append(k)
print("=== ENV CHECK ===")
for k,l in ok:
    print(f"OK: {k} (len={l})")
for k in miss:
    print(f"MISSING: {k}")
print("=================")
if miss:
    sys.exit(2)
else:
    print("All required keys present (basic check).")

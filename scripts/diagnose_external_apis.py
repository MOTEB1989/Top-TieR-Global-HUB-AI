#!/usr/bin/env python3
"""
diagnose_external_apis.py

تشخيص شامل للاتصال بمصادر API خارجية:
- OpenAI
- WHO (الصحة العالمية)
- World Bank
- Wikidata

طريقة التشغيل:
    export OPENAI_API_KEY=sk-xxxx
    python scripts/diagnose_external_apis.py
"""

import os
import sys
import requests
from typing import Dict, Any

# -------- Helpers --------
def check_openai():
    import openai
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"ok": False, "error": "OPENAI_API_KEY not set"}
    openai.api_key = api_key
    try:
        models = openai.models.list()
        names = [m.id for m in models.data[:5]]
        return {"ok": True, "models": names}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def check_who():
    url = "https://ghoapi.azureedge.net/api/Indicator?$top=3"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return {"ok": True, "sample": [d.get("IndicatorName") for d in data.get("value", [])]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def check_world_bank():
    url = "https://api.worldbank.org/v2/country/SA/indicator/SP.POP.TOTL?format=json&date=2021"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        pop = data[1][0]["value"] if len(data) > 1 else None
        return {"ok": True, "sample": {"Saudi Arabia population 2021": pop}}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def check_wikidata():
    url = "https://www.wikidata.org/wiki/Special:EntityData/Q30.json"  # Q30 = USA
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        usa = data["entities"]["Q30"]["labels"]["en"]["value"]
        return {"ok": True, "sample": {"Q30 label": usa}}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# -------- Main --------
def main():
    checks = {
        "OpenAI": check_openai(),
        "WHO": check_who(),
        "World Bank": check_world_bank(),
        "Wikidata": check_wikidata(),
    }
    print("\n===== External API Connectivity Report =====")
    for name, result in checks.items():
        if result["ok"]:
            print(f"✅ {name} OK → sample: {result.get('sample') or result.get('models')}")
        else:
            print(f"❌ {name} FAILED → {result['error']}")
    print("============================================\n")

if __name__ == "__main__":
    sys.exit(main())

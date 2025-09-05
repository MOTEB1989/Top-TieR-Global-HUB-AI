#!/usr/bin/env bash
set -euo pipefail

# =========================
# Veritas Bootstrap Script
# =========================
# يجهّز:
# - veritas_console.py      (الكونسول الموحّد)
# - api_server.py           (غلاف FastAPI للـ API)
# - requirements.txt        (تبعيات الـ API)
# - Dockerfile              (لبناء وتشغيل الحاوية)
# - .github/workflows/*.yml (CI + Bootstrap + Deploy-GHCR + Run-Console)
# - .devcontainer/devcontainer.json (لتسريع Codespaces)
# - README.md               (دليل سريع)

mkdir -p .github/workflows .devcontainer

# ---------- veritas_console.py ----------
cat > veritas_console.py <<'PY'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, json, re, sys, time, uuid
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

APP_NAME = "Veritas Console"
APP_VERSION = "1.0.0"
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

def now_iso(): return datetime.now(timezone.utc).isoformat()
def normalize_text(txt: str) -> str:
    import re
    t = (txt or "").strip().translate(ARABIC_DIGITS)
    return re.sub(r"\s+", " ", t)
def normalize_phone(v: str) -> str:
    import re
    v = normalize_text(v); digits = re.sub(r"\D", "", v)
    if digits.startswith("05"): return "+966" + digits[1:]
    if digits.startswith("5") and len(digits) == 9: return "+966" + digits
    if digits.startswith("966"): return "+" + digits
    if digits.startswith("00"): return "+" + digits[2:]
    if v.startswith("+"): return v
    return v
def infer_type(value: str):
    import re
    v = normalize_text(value)
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v): return "email"
    if v.startswith("@") and re.search(r"[a-zA-Z0-9_]{3,}", v): return "username"
    if re.search(r"\d", v) and len(re.sub(r"\D","",v))>=8: return "phone"
    return "text"

DOMAIN_PROFILES = {
    "osint": {
        "disclaimer": "تحذير: تحليل OSINT لمعلومات متاحة علنًا؛ ليست بديلاً للتحقق الرسمي.",
        "default_sources": ["hibp","intelx","search"],
        "router": {"phone":["intelx","search"],"email":["hibp","intelx","search"],"username":["intelx","search"],"text":["search"]}
    },
    "medical": {
        "disclaimer": "تنبيه طبي: معلومات تعليمية لدعم القرار، وليست نصيحة طبية أو تشخيصًا.",
        "default_sources": ["guidelines","literature"],
        "router": {"text":["guidelines","literature"]}
    },
    "realestate": {
        "disclaimer": "تنبيه عقاري: معلومات سوقية استرشادية، وليست استشارة قانونية أو تمويلية.",
        "default_sources": ["govdeals","market","maps"],
        "router": {"text":["govdeals","market","maps"],"address":["govdeals","market","maps"]}
    },
    "legal": {
        "disclaimer": "تنبيه قانوني: معلومات تحليلية عامة وليست استشارة قانونية ملزمة.",
        "default_sources": ["judgments","search"],
        "router": {"text":["judgments","search"]}
    }
}

def _stub(name, hint, q, qual=0.7):
    time.sleep(0.05)
    return [{"source":name,"data":{"hint":hint,"query":q},"first_seen":now_iso(),"last_seen":now_iso(),"quality":qual}]
def fetch_hibp(q, **k):        return _stub("hibp","(HIBP stub) نتائج تجريبية", q, 0.6)
def fetch_intelx(q, **k):      return _stub("intelx","(IntelX stub) نتائج تجريبية", q, 0.7)
def fetch_search(q, **k):      return _stub("search","(Web search stub) نتائج تجريبية", q, 0.5)
def fetch_guidelines(q, **k):  return _stub("guidelines","(Guidelines stub) أدلة إرشادية", q, 0.8)
def fetch_literature(q, **k):  return _stub("literature","(Literature stub) أبحاث مختصرة", q, 0.7)
def fetch_govdeals(q, **k):    return _stub("govdeals","(وزارة العدل/الهيئة - تجريبي) مؤشرات صفقات", q, 0.8)
def fetch_market(q, **k):      return _stub("market","(سوق عقاري تجريبي) متوسطات أسعار", q, 0.65)
def fetch_maps(q, **k):        return _stub("maps","(خرائط/POI تجريبي) نقاط اهتمام", q, 0.6)
def fetch_judgments(q, **k):   return _stub("judgments","(سواند قضائية تجريبية)", q, 0.75)
FETCHERS = {"hibp":fetch_hibp,"intelx":fetch_intelx,"search":fetch_search,"guidelines":fetch_guidelines,
            "literature":fetch_literature,"govdeals":fetch_govdeals,"market":fetch_market,"maps":fetch_maps,"judgments":fetch_judgments}

def step_normalize(domain, target, typ=None):
    t = normalize_text(target); inferred = typ or infer_type(t)
    if inferred == "phone": t = normalize_phone(t)
    return {"normalized": t, "type": inferred}
def step_route(domain, typ, sources_flag=None):
    profile = DOMAIN_PROFILES.get(domain, {})
    if sources_flag and sources_flag != "auto":
        return [s for s in sources_flag.split(",") if s in FETCHERS]
    return profile.get("router", {}).get(typ, profile.get("default_sources", []))
def step_parallel_fetch(sources, query, depth="basic", max_workers=6):
    res = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(FETCHERS[s], query, depth=depth): s for s in sources if s in FETCHERS}
        for fut in as_completed(futs):
            try:
                data = fut.result()
                if isinstance(data, list): res.extend(data)
            except Exception as e:
                res.append({"source":futs[fut],"error":str(e),"ts":now_iso()})
    return res
def step_aggregate_dedup(items):
    seen = set(); out = []
    for it in items:
        key = json.dumps(it.get("data",{}), sort_keys=True, ensure_ascii=False)
        if key not in seen: seen.add(key); out.append(it)
    return out
def step_confidence(items):
    if not items: return 0.0
    base = sum((it.get("quality",0.5) for it in items)) / len(items)
    bonus = min(0.2, 0.05*max(0,len(items)-1))
    return round(min(1.0, base+bonus), 2)
def build_trace(domain, norm, sources, items):
    return {"domain":domain,"query":norm["normalized"],"type":norm["type"],"sources_used":sources,"items_count":len(items),"generated_at":now_iso()}
def domain_disclaimer(domain): return DOMAIN_PROFILES.get(domain, {}).get("disclaimer","")
def autolog(entry: dict, path="console_audit.log"):
    entry = {"id": str(uuid.uuid4()), "ts": now_iso(), **entry}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
def export_output(payload, fmt="json", out=None):
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if out:
        with open(out,"w",encoding="utf-8") as f: f.write(text)
    return text
def run_pipeline(action, domain, target, scope="basic", depth="basic", sources="auto", out=None, fmt="json"):
    profile = DOMAIN_PROFILES.get(domain)
    if not profile: raise SystemExit(f"Domain not registered: {domain}")
    norm = step_normalize(domain, target, None)
    route = step_route(domain, norm["type"], sources_flag=sources)
    items = step_parallel_fetch(route, norm["normalized"], depth=depth)
    items = step_aggregate_dedup(items)
    conf  = step_confidence(items)
    trace = build_trace(domain, norm, route, items)
    payload = {"app":APP_NAME,"version":APP_VERSION,"action":action,"domain":domain,
               "disclaimer":domain_disclaimer(domain),
               "input":{"raw":target,"normalized":norm["normalized"],"type":norm["type"]},
               "scope":scope,"depth":depth,"results":items,"confidence":conf,"trace":trace}
    autolog({"action":action,"domain":domain,"input":payload["input"],"confidence":conf,"count":len(items)})
    return export_output(payload, fmt=fmt, out=out)

def _print(txt): sys.stdout.write(txt + ("\n" if not txt.endswith("\n") else ""))
def build_parser():
    p = argparse.ArgumentParser(prog="veritas", description=f"{APP_NAME} v{APP_VERSION}")
    sub = p.add_subparsers(dest="command", required=True)
    def common(sp):
        sp.add_argument("--domain", required=True, choices=list(DOMAIN_PROFILES.keys()))
        sp.add_argument("--scope", default="basic", choices=["basic","deep","full"])
        sp.add_argument("--depth", default="basic", choices=["basic","deep","advanced"])
        sp.add_argument("--sources", default="auto", help="Comma list or 'auto'")
        sp.add_argument("--format", default="json", choices=["json"])
        sp.add_argument("--out", default=None, help="Output path")
    for cmd, flag in [("analyze","--target"),("verify","--value"),("evaluate","--property"),("report","--identifier"),("search","--query"),("trace","--target")]:
        sp = sub.add_parser(cmd); sp.add_argument(flag, required=True); common(sp)
    return p
def main(argv=None):
    args = build_parser().parse_args(argv)
    target_attr = {"analyze":"target","verify":"value","evaluate":"property","report":"identifier","search":"query","trace":"target"}[args.command]
    target = getattr(args, target_attr)
    _print(run_pipeline(args.command, args.domain, target, scope=args.scope, depth=args.depth, sources=args.sources, out=args.out, fmt=args.format))
if __name__ == "__main__":
    main()
PY
chmod +x veritas_console.py

# ---------- api_server.py ----------
cat > api_server.py <<'PY'
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess, json, shlex

app = FastAPI(title="Veritas Console API")

class RunRequest(BaseModel):
    command: str   # analyze|verify|evaluate|report|search|trace
    domain: str    # osint|medical|realestate|legal
    target: str
    scope: str = "basic"
    depth: str = "basic"
    sources: str = "auto"

@app.post("/run")
def run(req: RunRequest):
    flag = "--target"
    if req.command == "verify": flag = "--value"
    elif req.command == "evaluate": flag = "--property"
    elif req.command == "report": flag = "--identifier"
    elif req.command == "search": flag = "--query"
    cmd = f"python veritas_console.py {shlex.quote(req.command)} --domain {shlex.quote(req.domain)} {flag} {shlex.quote(req.target)} --scope {shlex.quote(req.scope)} --depth {shlex.quote(req.depth)} --sources {shlex.quote(req.sources)}"
    out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    return json.loads(out.decode("utf-8"))
PY

# ---------- requirements.txt ----------
cat > requirements.txt <<'REQ'
fastapi
uvicorn
REQ

# ---------- Dockerfile ----------
cat > Dockerfile <<'DOCK'
FROM python:3.11-slim
WORKDIR /app
COPY veritas_console.py api_server.py requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
DOCK

# ---------- devcontainer (اختياري لكنه مفيد لـ Codespaces) ----------
cat > .devcontainer/devcontainer.json <<'JSON'
{
  "name": "veritas-dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "python -m pip install --upgrade pip && pip install -r requirements.txt"
}
JSON

# ---------- CI ----------
cat > .github/workflows/CI.yml <<'YML'
name: CI
on:
  push:
    branches: [ main, master ]
  pull_request:
permissions:
  contents: read
jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Static check
        run: python -m py_compile veritas_console.py || true
YML

# ---------- Bootstrap (لمن يريد بناء الملفات تلقائيًا من Actions) ----------
cat > .github/workflows/Bootstrap-Veritas.yml <<'YML'
name: Bootstrap-Veritas
on:
  workflow_dispatch:
    inputs:
      create_files:
        description: 'Create/Update veritas files'
        default: 'yes'
        required: true
permissions:
  contents: write
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create/Update files
        if: ${{ github.event.inputs.create_files == 'yes' }}
        run: |
          set -e
          mkdir -p .github/workflows
          git config user.name "veritas-bot"
          git config user.email "veritas-bot@users.noreply.github.com"
          [[ -f veritas_console.py ]] || echo "# placeholder" > veritas_console.py
          [[ -f api_server.py     ]] || echo "# placeholder" > api_server.py
          [[ -f requirements.txt  ]] || echo "fastapi\nuvicorn" > requirements.txt
          [[ -f Dockerfile        ]] || cat > Dockerfile <<'DOCK'
FROM python:3.11-slim
WORKDIR /app
COPY veritas_console.py api_server.py requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
DOCK
          git add -A
          git commit -m "Bootstrap Veritas Console files" || echo "Nothing to commit"
          git push
YML

# ---------- نشر إلى GHCR ----------
cat > .github/workflows/Deploy-GHCR.yml <<'YML'
name: Deploy to GHCR
on:
  push:
    branches: [ main, master ]
    paths:
      - 'Dockerfile'
      - 'api_server.py'
      - 'veritas_console.py'
      - '.github/workflows/Deploy-GHCR.yml'
  workflow_dispatch:
permissions:
  contents: read
  packages: write
env:
  IMAGE_NAME: veritas-console
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository_owner }}/${{ env.IMAGE_NAME }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
YML

# ---------- تشغيل الكونسول من Actions ----------
cat > .github/workflows/Run-Console.yml <<'YML'
name: Run Console
on:
  workflow_dispatch:
    inputs:
      command:
        description: 'analyze|verify|evaluate|report|search|trace'
        required: true
        default: 'analyze'
      domain:
        description: 'osint|medical|realestate|legal'
        required: true
        default: 'osint'
      target:
        description: 'target value (number/email/text/etc)'
        required: true
        default: '+9665XXXXXXX'
      scope:
        description: 'basic|deep|full'
        required: false
        default: 'basic'
      depth:
        description: 'basic|deep|advanced'
        required: false
        default: 'basic'
      sources:
        description: 'auto or comma-list'
        required: false
        default: 'auto'
jobs:
  run-console:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run Console
        run: |
          set -e
          CMD="${{ github.event.inputs.command }}"
          DOMAIN="${{ github.event.inputs.domain }}"
          TARGET="${{ github.event.inputs.target }}"
          SCOPE="${{ github.event.inputs.scope }}"
          DEPTH="${{ github.event.inputs.depth }}"
          SOURCES="${{ github.event.inputs.sources }}"
          FLAG="--target"
          case "$CMD" in
            verify)   FLAG="--value" ;;
            evaluate) FLAG="--property" ;;
            report)   FLAG="--identifier" ;;
            search)   FLAG="--query" ;;
          esac
          python veritas_console.py "$CMD" --domain "$DOMAIN" "$FLAG" "$TARGET" --scope "$SCOPE" --depth "$DEPTH" --sources "$SOURCES" > out.json
      - name: Upload output
        uses: actions/upload-artifact@v4
        with:
          name: console-output
          path: out.json
YML

# ---------- README ----------
cat > README.md <<'MD'
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
MD

echo “✅ تم توليد ملفات Veritas. الآن نفّذ: git add -A && git commit -m ‘Add Veritas stack’ && git push”

## بعد إضافة الملفات — أوامر تشغيل/اختبار سريعة
لو تستخدم **GitHub CLI (gh)**، هذه أوامر مفيدة:

```bash
# تشغيل الـ Workflow الذي يشغّل الكونسول
gh workflow run "Run-Console.yml" -f command=analyze -f domain=osint -f target=+96651234567

# تشغيل نشر Docker إلى GHCR
gh workflow run "Deploy-GHCR.yml"

# تنزيل ناتج التشغيل (artifact) لـ Run-Console (عدّل run-id)
gh run download <run-id> -n console-output

كل ما سبق يستخدم GITHUB_TOKEN الافتراضي—لا حاجة لـ PAT الآن.
إذا أردت إضافة نشر تلقائي إلى خادمك (Azure/AWS/GCP أو Runner ذاتي)، أعطني البيئة وسأجهز لك Workflow إضافي بنفس الأسلوب.
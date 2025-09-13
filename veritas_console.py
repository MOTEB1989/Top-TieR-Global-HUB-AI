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
                if isinstance(data, list):
                    res.extend(data)
                else:
                    res.append({"source":futs[fut],"error":"Result is not a list","ts":now_iso()})
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

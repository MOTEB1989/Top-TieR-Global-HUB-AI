#!/bin/bash
# self_heal.sh — Autonomous Repo Intelligence

set -e

echo "🧠 Running Ultra Agent OS..."
python ultra_agent_os.py \
  --mode full-scan \
  --out-json reports/ultra_report.json \
  --out-md   reports/ultra_report.md

echo "📡 Creating self-heal plan..."

python3 << 'EOF'
import json, os

report = json.load(open("reports/ultra_report.json"))
issues = report.get("issues", [])
files = report.get("files", [])

plan = {
    "summary": f"{len(issues)} issues detected",
    "issues": issues,
    "recommended_fixes": [],
}

for issue in issues:
    plan["recommended_fixes"].append({
        "issue": issue.get("message"),
        "file": issue.get("file"),
        "suggested_action": "autofix" if "missing" in issue.get("message", "").lower() else "manual review"
    })

os.makedirs("reports", exist_ok=True)
json.dump(plan, open("reports/self_heal_plan.json","w"), indent=2)

with open("reports/self_heal_plan.md","w") as f:
    f.write("# 🔧 Self-Heal Plan\n\n")
    f.write(f"Detected {len(issues)} issues.\n\n")
    for rec in plan["recommended_fixes"]:
        f.write(f"- **{rec['issue']}** → `{rec['suggested_action']}` ({rec['file']})\n")

print("✅ self_heal_plan.json + self_heal_plan.md generated.")
EOF

echo "🎯 Self-heal plan ready in reports/"

import argparse
import glob
import json
import os
from typing import Dict, List

WARNING_SIGNALS = ["⚠️", "خطر", "مخاطر", "critical", "security", "vulnerability", "ثغرة"]


def expand_inputs(patterns: List[str]) -> List[str]:
    files = []
    for pattern in patterns:
        matches = glob.glob(pattern)
        if not matches and os.path.isfile(pattern):
            matches = [pattern]
        files.extend(matches)
    return sorted(set(files))


def count_warnings_for_content(content: str) -> int:
    lowered = content.lower()
    total = 0
    for signal in WARNING_SIGNALS:
        if signal.isascii():
            total += lowered.count(signal.lower())
        else:
            total += content.count(signal)
    return total


def assess_file(path: str) -> Dict[str, int]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()
    except FileNotFoundError:
        return {"name": os.path.basename(path), "warnings": 0}

    warnings = count_warnings_for_content(content)
    return {"name": os.path.basename(path), "warnings": warnings}


def determine_risk_level(total_warnings: int) -> str:
    if total_warnings == 0:
        return "low"
    if 1 <= total_warnings <= 3:
        return "medium"
    return "high"


def print_human_summary(risk_level: str, total_warnings: int) -> None:
    level_ar = {"low": "منخفض", "medium": "متوسط", "high": "مرتفع"}.get(risk_level, risk_level)
    print(f"مستوى المخاطر التقديري: {level_ar} (عدد التحذيرات: {total_warnings}).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Assess AI review risk based on warning signals in markdown files.")
    parser.add_argument("--inputs", nargs="+", required=True, help="Input markdown files to scan for risk signals.")
    parser.add_argument("--output", default="ai_review_output/risk_summary.json", help="Path to write the risk summary JSON.")
    args = parser.parse_args()

    files = expand_inputs(args.inputs)
    results = [assess_file(path) for path in files]

    total_warnings = sum(item["warnings"] for item in results)
    risk_level = determine_risk_level(total_warnings)

    output = {
        "files": results,
        "total_warnings": total_warnings,
        "risk_level": risk_level,
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as target:
        json.dump(output, target, ensure_ascii=False, indent=2)

    print_human_summary(risk_level, total_warnings)


if __name__ == "__main__":
    main()

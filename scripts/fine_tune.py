from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _validate_line(raw: str, line_no: int) -> Dict[str, str]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Line {line_no}: invalid JSON ({exc})")
    if not isinstance(data, dict):
        raise ValueError(f"Line {line_no}: expected object")
    if "prompt" not in data or "completion" not in data:
        raise ValueError(f"Line {line_no}: missing prompt/completion fields")
    if not isinstance(data["prompt"], str) or not isinstance(data["completion"], str):
        raise ValueError(f"Line {line_no}: prompt and completion must be strings")
    return {"prompt": data["prompt"], "completion": data["completion"]}


def _compute_stats(samples: List[Dict[str, str]]) -> Dict[str, Any]:
    lengths = [len(s["prompt"].split()) + len(s["completion"].split()) for s in samples]
    return {
        "total_samples": len(samples),
        "average_length": sum(lengths) / len(lengths) if lengths else 0,
        "max_length": max(lengths) if lengths else 0,
    }


def validate_file(path: Path) -> Dict[str, Any]:
    samples: List[Dict[str, str]] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        samples.append(_validate_line(line, idx))
    stats = _compute_stats(samples)
    return {"samples": samples, "stats": stats}


def main(argv: list[str] | None = None) -> None:  # pragma: no cover - CLI
    parser = argparse.ArgumentParser(description="Validate fine-tuning JSONL files")
    sub = parser.add_subparsers(dest="command")
    validate_cmd = sub.add_parser("validate")
    validate_cmd.add_argument("path", type=Path)

    args = parser.parse_args(argv)
    if args.command == "validate":
        result = validate_file(args.path)
        print(json.dumps(result["stats"], ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

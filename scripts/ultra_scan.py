import json
import os
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_file(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def hash_file(path: Path):
    try:
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()
    except Exception:
        return None


report = {
    "files": [],
    "structure": {},
    "languages": {"rust": [], "node": [], "python": []},
    "docker": {"compose_files": [], "dockerfiles": []},
    "k8s": [],
    "issues_detected": [],
}

# Walk repository
for root, dirs, files in os.walk(ROOT):
    for file in files:
        full = Path(root) / file
        rel = full.relative_to(ROOT)

        content = read_file(full)
        checksum = hash_file(full)

        entry = {
            "path": str(rel),
            "size": full.stat().st_size,
            "sha256": checksum,
        }

        # Detect languages / frameworks
        if file.endswith(".rs"):
            report["languages"]["rust"].append(str(rel))
        if file.endswith(".ts") or file == "package.json":
            report["languages"]["node"].append(str(rel))
        if file.endswith(".py"):
            report["languages"]["python"].append(str(rel))

        if file == "docker-compose.yml" or "compose" in file:
            report["docker"]["compose_files"].append(str(rel))
        if file.lower().startswith("dockerfile"):
            report["docker"]["dockerfiles"].append(str(rel))

        if file.endswith((".yaml", ".yml")):
            if content and "apiVersion" in content and ("Deployment" in content or "Service" in content):
                report["k8s"].append(str(rel))

        report["files"].append(entry)


def check_expected_dirs():
    expected = {
        "core": ["Cargo.toml", "main.rs"],
        "services/api": ["package.json"],
        "adapters/python/lexhub": ["__init__.py"],
    }
    for d, files in expected.items():
        dir_path = ROOT / d
        if not dir_path.exists():
            report["issues_detected"].append(f"Missing directory: {d}")
            continue
        for f in files:
            if not (dir_path / f).exists():
                report["issues_detected"].append(f"Missing file {d}/{f}")


check_expected_dirs()

# Qdrant detection
found_qdrant = False
for compose_file in report["docker"]["compose_files"]:
    content = read_file(ROOT / compose_file)
    if content and "qdrant" in content.lower():
        found_qdrant = True
        break
if not found_qdrant:
    report["issues_detected"].append("Qdrant not found in docker-compose")

# Redis usage detection
redis_seen = False
for f in report["files"]:
    if f["path"].endswith(".py"):
        c = read_file(ROOT / f["path"])
        if c and "redis" in c.lower():
            redis_seen = True
            break

if redis_seen:
    redis_in_compose = False
    for compose_file in report["docker"]["compose_files"]:
        content = read_file(ROOT / compose_file)
        if content and "redis" in content.lower():
            redis_in_compose = True
            break
    if not redis_in_compose:
        report["issues_detected"].append(
            "Python code uses Redis but docker-compose has no Redis service"
        )

# Produce JSON + Markdown
analysis_dir = ROOT / "analysis"
analysis_dir.mkdir(exist_ok=True)

with open(analysis_dir / "ultra_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=4)

with open(analysis_dir / "ultra_report.md", "w", encoding="utf-8") as f:
    f.write("# Ultra-Scan Report\n\n")
    f.write("## Summary\n\n")
    f.write(f"- Rust files: {len(report['languages']['rust'])}\n")
    f.write(f"- Node files: {len(report['languages']['node'])}\n")
    f.write(f"- Python files: {len(report['languages']['python'])}\n")
    f.write(f"- Docker Compose files: {report['docker']['compose_files']}\n")
    f.write(f"- Dockerfiles: {report['docker']['dockerfiles']}\n")
    f.write(f"- Kubernetes files: {report['k8s']}\n\n")

    f.write("## Issues Detected\n")
    for issue in report["issues_detected"]:
        f.write(f"- ❗ {issue}\n")

print("Ultra-Scan Complete.")
print("Results written to analysis/ultra_report.json and ultra_report.md")

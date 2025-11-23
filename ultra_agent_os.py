#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA Agent OS – Single File Edition
------------------------------------
- يفحص المستودع محلياً
- يبني Chunks + Semantic Graph
- يفحص docker-compose والمجلدات الناقصة
- يشغّل الاختبارات (pytest / npm test / cargo test) إن وُجدت
- يكتب تقارير JSON + Markdown لاستخدامها من قبل أي Agent (CodeX, GPT, Kimi, Grok)

الاستخدام داخل المستودع:
    python ultra_agent_os.py

يمكن استدعاؤه من أي وكيل كخطوة واحدة.
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional


# =========================
# إعدادات عامة قابلة للتعديل
# =========================

# أقصى حجم للملف النصي بالبايت ليتم تحليله
MAX_FILE_SIZE = 512 * 1024  # 512KB

# الامتدادات التي نعتبرها "نصوص كود / إعداد" ذات أولوية
CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".rs", ".go", ".java",
    ".yml", ".yaml", ".json",
    ".toml", ".md", ".sh", ".bash", ".env",
    ".Dockerfile", ".dockerfile",
}

# مسارات تُستثنى من الفحص
EXCLUDE_DIRS = {
    ".git", ".github", ".venv", "venv", "node_modules",
    "__pycache__", "dist", "build", ".idea", ".vscode",
}

OUTPUT_DIR = ".ultra_reports"  # مجلد التقارير الناتجة


# =========================
# أدوات مساعدة عامة
# =========================

def log(msg: str) -> None:
    print(msg)
    sys.stdout.flush()


def run_cmd(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 600) -> Tuple[int, str, str]:
    """تشغيل أمر في subprocess مع إرجاع (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"Command timeout after {timeout}s: {' '.join(cmd)}"


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def detect_repo_root(start: Optional[Path] = None) -> Path:
    """يكتشف جذر المستودع بالبحث عن .git صعوداً؛ إن لم يجد يرجع current dir."""
    if start is None:
        start = Path.cwd()
    cur = start.resolve()
    for parent in [cur] + list(cur.parents):
        if (parent / ".git").exists():
            return parent
    return cur


# =========================
# مسح الملفات وبناء الـ Chunks
# =========================

def is_text_file(path: Path) -> bool:
    """تخمين بسيط: نحاول قراءة جزء من الملف؛ إذا فشل => نعتبره غير نصي."""
    try:
        with path.open("rb") as f:
            chunk = f.read(4096)
        chunk.decode("utf-8")
        return True
    except Exception:
        return False


def list_repo_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # استثناء مجلدات
        rel_parts = Path(dirpath).relative_to(root).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue

        for name in filenames:
            full = Path(dirpath) / name
            # استثناء ملفات كبيرة جداً
            try:
                size = full.stat().st_size
            except OSError:
                continue
            if size > MAX_FILE_SIZE:
                continue
            files.append(full)
    return files


def classify_file(path: Path, repo_root: Path) -> Dict[str, Any]:
    rel = path.relative_to(repo_root).as_posix()
    ext = path.suffix
    kind = "other"
    if ext in {".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go"}:
        kind = "code"
    elif ext in {".yml", ".yaml", ".toml", ".json"}:
        kind = "config"
    elif ext in {".md"}:
        kind = "doc"
    elif "dockerfile" in path.name.lower():
        kind = "docker"
    elif path.name.startswith(".env"):
        kind = "env"
    return {
        "path": rel,
        "ext": ext,
        "kind": kind,
    }


def chunk_file(path: Path, repo_root: Path, max_chars: int = 4000) -> List[Dict[str, Any]]:
    """تفكيك ملف إلى chunks صغيرة؛ لكل chunk meta تساعد الـ LLM."""
    rel = path.relative_to(repo_root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []
    if not text.strip():
        return []

    chunks: List[Dict[str, Any]] = []
    buffer: List[str] = []
    cur_len = 0
    start_line = 1
    line_no = 0
    for line in text.splitlines(keepends=True):
        line_no += 1
        if cur_len + len(line) > max_chars and buffer:
            chunk_text = "".join(buffer)
            chunks.append({
                "file": rel,
                "start_line": start_line,
                "end_line": line_no - 1,
                "chars": len(chunk_text),
                "sha1": sha1(rel + f":{start_line}-{line_no-1}:" + chunk_text),
                "preview": chunk_text[:200],
            })
            buffer = [line]
            cur_len = len(line)
            start_line = line_no
        else:
            buffer.append(line)
            cur_len += len(line)

    if buffer:
        chunk_text = "".join(buffer)
        chunks.append({
            "file": rel,
            "start_line": start_line,
            "end_line": line_no,
            "chars": len(chunk_text),
            "sha1": sha1(rel + f":{start_line}-{line_no}:" + chunk_text),
            "preview": chunk_text[:200],
        })

    return chunks


def build_semantic_graph(files_meta: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    بناء رسم بياني بسيط (غير قائم على AST) يربط الملفات حسب اسم الخدمة/اللغة ونوعها.
    هذا ليس تحليل لغوي عميق لكنه مفيد كطبقة metadata لأي Agent.
    """
    nodes = []
    edges = []

    for f in files_meta:
        node_id = f["path"]
        label = f["path"]
        group = f["kind"]
        nodes.append({
            "id": node_id,
            "label": label,
            "group": group,
        })

    by_ext: Dict[str, List[str]] = {}
    for f in files_meta:
        by_ext.setdefault(f["ext"], []).append(f["path"])

    for ext, paths in by_ext.items():
        if len(paths) > 1:
            for i in range(len(paths) - 1):
                edges.append({
                    "source": paths[i],
                    "target": paths[i + 1],
                    "type": "same_ext",
                    "ext": ext,
                })

    by_dir: Dict[str, List[Dict[str, Any]]] = {}
    for f in files_meta:
        directory = str(Path(f["path"]).parent)
        by_dir.setdefault(directory, []).append(f)

    for directory, group_files in by_dir.items():
        configs = [f for f in group_files if f["kind"] in {"config", "docker", "env"}]
        codes = [f for f in group_files if f["kind"] == "code"]
        for c in configs:
            for code in codes:
                edges.append({
                    "source": c["path"],
                    "target": code["path"],
                    "type": "config_to_code",
                    "dir": directory,
                })

    return {
        "nodes": nodes,
        "edges": edges,
    }


# =========================
# فحص docker-compose وتحليل build context
# =========================

def find_compose_files(repo_root: Path) -> List[Path]:
    candidates = [
        repo_root / "docker-compose.yml",
        repo_root / "docker-compose.yaml",
        repo_root / "docker-compose.rag.yml",
    ]
    return [p for p in candidates if p.exists()]


def validate_docker_compose(repo_root: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "compose_files": [],
        "docker_available": False,
        "validation": [],
        "missing_build_contexts": [],
        "errors": [],
    }

    compose_files = find_compose_files(repo_root)
    result["compose_files"] = [str(p.relative_to(repo_root)) for p in compose_files]

    code, out, err = run_cmd(["docker", "--version"])
    if code == 0:
        result["docker_available"] = True
    else:
        result["errors"].append("Docker not available in PATH")
        return result

    for compose in compose_files:
        cfg_res = {"file": str(compose.relative_to(repo_root)), "valid": False, "error": None}
        code, out, err = run_cmd(["docker", "compose", "-f", str(compose), "config"], cwd=repo_root)
        if code == 0:
            cfg_res["valid"] = True
        else:
            cfg_res["valid"] = False
            cfg_res["error"] = err.strip() or out.strip()
            result["errors"].append(f"docker compose config failed for {compose}: {cfg_res['error']}")
        result["validation"].append(cfg_res)

        try:
            text = compose.read_text(encoding="utf-8")
        except Exception:
            continue
        lines = text.splitlines()
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith("context:") or line_stripped.startswith("build:"):
                parts = line_stripped.split(":", 1)
                if len(parts) != 2:
                    continue
                raw_path = parts[1].strip()
                if not raw_path or raw_path in {".", "./"}:
                    continue
                if raw_path.startswith(("'", '"')) and raw_path.endswith(("'", '"')):
                    raw_path = raw_path[1:-1]
                build_path = (compose.parent / raw_path).resolve()
                if not build_path.exists():
                    result["missing_build_contexts"].append({
                        "compose_file": str(compose.relative_to(repo_root)),
                        "declared_path": raw_path,
                        "resolved_path": str(build_path),
                    })

    return result


# =========================
# تشغيل الاختبارات (pytest / npm / cargo)
# =========================

def run_pytest_if_exists(repo_root: Path) -> Dict[str, Any]:
    tests_dir = repo_root / "tests"
    pytest_ini = repo_root / "pytest.ini"
    if not tests_dir.exists() and not pytest_ini.exists():
        return {"enabled": False, "status": "skipped", "detail": "pytest not detected"}
    code, out, err = run_cmd(["pytest", "-q"], cwd=repo_root)
    return {
        "enabled": True,
        "status": "ok" if code == 0 else "failed",
        "returncode": code,
        "stdout": out[-4000:],
        "stderr": err[-4000:],
    }


def run_npm_test_if_exists(repo_root: Path) -> Dict[str, Any]:
    package_json = repo_root / "package.json"
    if not package_json.exists():
        return {"enabled": False, "status": "skipped", "detail": "package.json not found"}

    try:
        package_data = json.loads(package_json.read_text(encoding="utf-8"))
    except Exception:
        return {"enabled": False, "status": "skipped", "detail": "invalid package.json"}

    scripts = package_data.get("scripts") or {}
    if "test" not in scripts:
        return {"enabled": False, "status": "skipped", "detail": "no test script in package.json"}

    code, out, err = run_cmd(["npm", "test"], cwd=repo_root)
    return {
        "enabled": True,
        "status": "ok" if code == 0 else "failed",
        "returncode": code,
        "stdout": out[-4000:],
        "stderr": err[-4000:],
    }


def run_cargo_test_if_exists(repo_root: Path) -> Dict[str, Any]:
    cargo_toml = repo_root / "Cargo.toml"
    if not cargo_toml.exists():
        return {"enabled": False, "status": "skipped", "detail": "Cargo.toml not found"}
    code, out, err = run_cmd(["cargo", "test", "--quiet"], cwd=repo_root)
    return {
        "enabled": True,
        "status": "ok" if code == 0 else "failed",
        "returncode": code,
        "stdout": out[-4000:],
        "stderr": err[-4000:],
    }


def run_all_tests(repo_root: Path) -> Dict[str, Any]:
    log("🧪 Running tests (pytest / npm test / cargo test) if available...")
    return {
        "pytest": run_pytest_if_exists(repo_root),
        "npm_test": run_npm_test_if_exists(repo_root),
        "cargo_test": run_cargo_test_if_exists(repo_root),
    }


# =========================
# توليد التقارير (SUPER / ULTRA)
# =========================

def ensure_output_dir(repo_root: Path) -> Path:
    out = repo_root / OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    return out


def generate_super_knowledge_pack(
    repo_root: Path,
    files_meta: List[Dict[str, Any]],
    chunks: List[Dict[str, Any]],
    graph: Dict[str, Any],
) -> Dict[str, Any]:
    """حزمة واحدة كبيرة يمكن أن يحمّلها أي LLM Agent كـ context."""
    return {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "repo_root": str(repo_root),
        "files_count": len(files_meta),
        "chunks_count": len(chunks),
        "graph_nodes": len(graph.get("nodes", [])),
        "graph_edges": len(graph.get("edges", [])),
        "files": files_meta,
        "graph": graph,
    }


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_ultra_summary_markdown(
    path: Path,
    tests_report: Dict[str, Any],
    docker_report: Dict[str, Any],
    files_meta: List[Dict[str, Any]],
) -> None:
    lines: List[str] = []
    lines.append("# ULTRA Stack Report\n")
    lines.append(f"- Generated at: **{datetime.utcnow().isoformat()}Z**\n")
    lines.append(f"- Total files scanned: **{len(files_meta)}**\n")

    lines.append("## Test Results\n")
    for name, rep in tests_report.items():
        status = rep.get("status")
        enabled = rep.get("enabled", False)
        if not enabled:
            lines.append(f"- **{name}**: _skipped_ ({rep.get('detail')})")
        else:
            lines.append(f"- **{name}**: **{status}** (returncode={rep.get('returncode')})")
    lines.append("")

    lines.append("## Docker Compose\n")
    lines.append(f"- Docker available: **{docker_report.get('docker_available')}**")
    lines.append(f"- Compose files: `{', '.join(docker_report.get('compose_files', [])) or 'none'}`")
    if docker_report.get("missing_build_contexts"):
        lines.append("\n### Missing build contexts\n")
        for m in docker_report["missing_build_contexts"]:
            lines.append(
                f"- `{m['declared_path']}` in `{m['compose_file']}` "
                f"→ resolved path `{m['resolved_path']}` (not found)"
            )
    if docker_report.get("errors"):
        lines.append("\n### Errors\n")
        for e in docker_report["errors"]:
            lines.append(f"- {e}")
    lines.append("")

    lines.append("## Key Files\n")
    important = [f for f in files_meta if f["kind"] in {"code", "config", "docker"}]
    important = sorted(important, key=lambda f: f["path"])[:40]
    for f in important:
        lines.append(f"- `{f['path']}` ({f['kind']})")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_ultra_report(
    repo_root: Path,
    files_meta: List[Dict[str, Any]],
    docker_report: Dict[str, Any],
    tests_report: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "repo_root": str(repo_root),
        "summary": {
            "files_count": len(files_meta),
            "docker_available": docker_report.get("docker_available"),
            "compose_files": docker_report.get("compose_files", []),
        },
        "docker": docker_report,
        "tests": tests_report,
    }


# =========================
# الدالة الرئيسية
# =========================

def main() -> int:
    log("📍 Detecting repository root...")
    repo_root = detect_repo_root()
    log(f"   → repo_root = {repo_root}")

    out_dir = ensure_output_dir(repo_root)
    log(f"📁 Output directory: {out_dir}")

    log("🔎 Scanning files...")
    all_files = list_repo_files(repo_root)
    files_meta: List[Dict[str, Any]] = []
    for path in all_files:
        meta = classify_file(path, repo_root)
        files_meta.append(meta)
    log(f"   → Total files scanned (after filters): {len(files_meta)}")

    log("🧩 Building chunks...")
    chunks: List[Dict[str, Any]] = []
    for path in all_files:
        if not is_text_file(path):
            continue
        file_chunks = chunk_file(path, repo_root)
        if file_chunks:
            chunks.extend(file_chunks)
    log(f"   → Total chunks: {len(chunks)}")

    log("🕸️ Building semantic graph...")
    graph = build_semantic_graph(files_meta)
    log(f"   → Nodes: {len(graph.get('nodes', []))}, Edges: {len(graph.get('edges', []))}")

    log("🐳 Validating docker-compose...")
    docker_report = validate_docker_compose(repo_root)

    tests_report = run_all_tests(repo_root)

    log("📦 Writing SUPER_KNOWLEDGE_PACK & raw graph/chunks...")
    super_pack = generate_super_knowledge_pack(repo_root, files_meta, chunks, graph)
    write_json(out_dir / "SUPER_KNOWLEDGE_PACK.json", super_pack)
    write_json(out_dir / "semantic_chunks.json", chunks)
    write_json(out_dir / "semantic_graph.json", graph)

    log("📝 Writing ULTRA_REPORT.json and ULTRA_SUMMARY.md...")
    ultra_report = build_ultra_report(repo_root, files_meta, docker_report, tests_report)
    write_json(out_dir / "ULTRA_REPORT.json", ultra_report)
    write_ultra_summary_markdown(out_dir / "ULTRA_SUMMARY.md", tests_report, docker_report, files_meta)

    log("")
    log("✅ ULTRA Agent OS finished successfully.")
    log(f"   - SUPER_KNOWLEDGE_PACK.json → {out_dir / 'SUPER_KNOWLEDGE_PACK.json'}")
    log(f"   - ULTRA_REPORT.json         → {out_dir / 'ULTRA_REPORT.json'}")
    log(f"   - ULTRA_SUMMARY.md          → {out_dir / 'ULTRA_SUMMARY.md'}")
    log("")
    log("يمكن لأي Agent (CodeX / GPT / Grok / Kimi) قراءة هذه الملفات واستخدامها لفهم المستودع وتشغيل التحسينات.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

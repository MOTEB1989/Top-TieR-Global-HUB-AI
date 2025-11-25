# Phase 3 — Final Production-Grade Edition

The following directive was provided for Codex to execute Phase 3 (Engineering Stabilization & Unified CI/CD) on the repository `MOTEB1989/Top-TieR-Global-HUB-AI`.

---

```
Codex, open the repository:

MOTEB1989/Top-TieR-Global-HUB-AI

Perform Phase 3: Engineering Stabilization & Unified CI/CD, incorporating all safety, determinism, and production requirements.
Produce a single diff and do not push.
If any step is ambiguous, soft-fail and document manually in the stabilization report instead of modifying code blindly.
```

1) **Docker & Compose Consistency (Strict Mode)**
   - Update paths to the new structured locations:
     - `services/api_server`
     - `services/veritas-web`
     - `services/veritas-mini-web`
   - Before applying any path change, verify that the referenced directory exists.
     - If missing → add item to the “Manual Review” list in the stabilization report.
   - Remove references to missing paths (`./core`, `./services/api`) only if confirmed missing.
   - Enforce pinned images (no `latest`).
   - Add reliable healthchecks per service:
     - If `/health` endpoint exists → use HTTP healthcheck.
     - If not → use TCP check: `"CMD-SHELL", "nc -z localhost ${PORT:-8080}"`
     - Neo4j healthcheck: `"CMD-SHELL", "curl -sf http://localhost:7474 || exit 1"`
   - Set `restart: unless-stopped`.

   **Dockerfiles**
   - Remove anti-pattern `npm install || true`.
   - Convert services to multi-stage builds.
   - Add non-root user hardening (`USER app` / `USER node`).
   - Pin base images to exact versions (no floating tags).
   - Use consistent `ARG PORT` / `ENV PORT`.
   - `COPY` only necessary files after restructure.

2) **Database Stabilization (Neo4j & Scripts)**
   - Fix the typo in `databases/neo4j/init_graph.cql`: `p.address` → `e.address`.
   - Repair `setup_neo4j_security.sh` trailing truncation and ensure executable bit.
   - Validate k8s manifests: secret names, PVC sizes, indentation. Document changes clearly.
   - Ensure `.env.neo4j.example` aligns with runtime variable names without embedding secrets.
   - Add an automated CQL syntax check in CI using transient Neo4j container running the init file.

3) **Runtime Dependencies (Pinned & Synchronized)**
   - Synchronize `pyproject.toml` and `requirements.txt` using pinned versions:
     - `python-dotenv~=1.0`
     - `PyMuPDF~=1.24`
     - `beautifulsoup4~=4.12`
     - `fastapi~=0.115`
     - `groq~=0.9`
     - `openai~=1.57`
   - Node: ensure `package-lock.json` or `pnpm-lock.yaml` is present and valid.
   - General: no unpinned versions and no secrets in code or lockfiles.

4) **Legacy Module Policy (Deterministic Rule)**
   - For `utils/graph_ingestor.py`:
     - If no references found → remove file and record it under Legacy Removal.
     - If references exist but implementation incomplete → replace with a placeholder class + TODO + deterministic safe fallback return.
   - Document decision and justification in the report.

5) **Harden veritas-web / veritas-mini-web**
   - Add environment-driven CORS (`ALLOWED_ORIGINS`, default: localhost only).
   - Replace raw string responses with structured JSON.
   - Add feature flags: `NEO4J_ENABLED` and `ENCRYPTION_ENABLED`.
   - Move shared logic to `services/common/` (verify file existence before refactoring; otherwise mark for manual review).

6) **Deterministic Unit & Integration Tests**
   - Under `tests/` add FastAPI tests for `/health`, `/query`, `/review`, and ingestion.
   - Implement a consistent `MockGateway`:
     - Activate via env: `LLM_GATEWAY=mock`.
     - Provide stable deterministic responses.
     - Ensure coverage of: `veritas-web`, `veritas-mini-web`, `review_engine`.
   - Generate and upload coverage reports in CI.

7) **Unified CI/CD — Production Grade**
   - Create/upgrade `.github/workflows/ci.yml` with jobs for:
     - Python linting (ruff)
     - Type checks (mypy, tsc)
     - Unit tests + coverage
     - Gateway validation (reuse existing workflow)
     - Docker builds for: `api_server`, `veritas-web`, `veritas-mini-web`
     - `docker-compose` boot validation
     - Neo4j CQL syntax validation
     - Security scanning: CodeQL and Trivy
   - Controls:
     - `strategy.fail-fast: true`
     - `timeout-minutes: 10` per step
     - Use `actions/cache` for pip/node/cargo
     - Upload artifacts: logs, coverage, test reports
   - Secrets: use GitHub Secrets only; if a secret is missing → fail with a helpful message; never echo secrets.

8) **Stabilization Report (`docs/REPO_STABILIZATION_REPORT.md`)**
   - Include: summary of fixes, paths updated (before/after), CI test matrix, coverage summary, known issues, Manual Review list for ambiguous steps, TODO roadmap for Phase 4 (RAG Engine, Streamlit/Web UI, Local Phi-3 integration, Gateway orchestration enhancements, JSONL fine-tuning toolkit, PDF ingestion pipeline, Docker-only release process).

9) **Output Requirements**
   - Provide the full diff; do not merge.
   - Show modified files, new/updated tests, CI workflow changes, stabilization report full content.

End of directive.

---

This document captures the exact instructions requested for Phase 3 execution.

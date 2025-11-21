# Repo Restructure Report (Phase 2)

## Summary
- Established standardized top-level folders for services, databases, scripts, tests, documentation, and release assets.
- Consolidated service code under `services/` and database artifacts under `databases/` to clarify deployment boundaries.
- Centralized operational scripts in `scripts/` and test assets in `tests/` for easier maintenance.
- Relocated key project documentation into `docs/` and added a root README that points to the new locations.
- Segregated large archive artifacts into `releases/` and updated ignore rules for future uploads.

## File Moves
| Item | From | To | Notes |
| --- | --- | --- | --- |
| API server package | `api_server/` | `services/api_server/` | Added `services/__init__.py` for package discovery; updated imports and uvicorn target strings accordingly. |
| Veritas web UI | `veritas-web/` | `services/veritas-web/` | Maintains existing Dockerfile and app entrypoints. |
| Veritas mini web | `veritas-mini-web/` | `services/veritas-mini-web/` | Maintains existing Dockerfile and app entrypoints. |
| Workflows addon | `veritas_workflows_addon/` | `services/veritas_workflows_addon/` | Moved intact. |
| Neo4j assets | `db/neo4j/` | `databases/neo4j/` | Demo script reference updated. |
| Utility scripts | Root `*.sh` scripts | `scripts/` | Includes `demo_features.sh`, `do_all_now.sh`, `harden_repo.sh`, `run_codex_full.sh`, `setup_neo4j_security.sh`, `setup_veritas.sh`, `upgrade_veritas.sh`, `validate_security_improvements.sh`, `verify_repo_link.sh`. |
| Tests | `test_gpt_connection.py*` | `tests/` | Updated GPT client tests to import from `services.api_server`. |
| Documentation | Root `README.md`, `SECURITY.md`, `SECURITY_GOVERNANCE.md` | `docs/` | Root README now points to `docs/`. |
| Archives (unreferenced) | Root `*.zip` | `releases/` | See release asset notes below. |

## Release Asset Recommendations
The following archives were not referenced in code or Dockerfiles and have been moved to `releases/` for staging. They appear safe to remove from source control and should be uploaded as GitHub Release assets if needed:
- `releases/LexCode-Hybrid-Starter-AI-Infer.zip`
- `releases/bluetooth-open-diagnostics.zip`
- `releases/bluetooth-open-diagnostics2.zip`
- `releases/top-tier-base-files.zip`
- `releases/topTireAI-quality-pack.zip`
- `releases/veritas-nexus-v2.zip`

## TODO / Manual Follow-ups
- `scripts/setup_veritas.sh` still includes inline Dockerfile snippets and file-generation steps that assume root-level `api_server.py`; refactor to align with `services/api_server/` if the script is used for bootstrapping.
- `docker-compose.yml` references `./services/api`, which does not exist in the new structure; update the compose service definitions to match the relocated services before running Compose.
- Consider relocating any future archive additions directly to GitHub Releases; `.gitignore` now excludes archive extensions to prevent accidental commits.

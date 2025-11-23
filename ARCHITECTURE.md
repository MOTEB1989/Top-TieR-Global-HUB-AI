# ARCHITECTURE (Auto-generated minimal)

This file summarizes the current layout of the repository and runtime infra.
- Branch used for infra changes: ${BRANCH}
- API_PORT default: 3000

Services:
- core (Rust) - port 8080 (if Dockerfile present)
- api (Node) - port 3000
- redis - port 6379 (optional)
- qdrant - port 6333 (optional)
- neo4j - ports 7474/7687 (optional)

Generated: ${TIMESTAMP}

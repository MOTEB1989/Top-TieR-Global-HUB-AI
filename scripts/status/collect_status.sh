#!/usr/bin/env bash
set -euo pipefail

BOLD="$(tput bold || true)"; RESET="$(tput sgr0 || true)"

header() { echo -e "\n${BOLD}== $* ==${RESET}"; }

mask() {
  local s="${1:-}"; [[ -z "$s" ]] && { echo "absent"; return; }
  local len=${#s}
  if (( len <= 4 )); then echo "***"; else echo "${s:0:2}***${s: -2}"; fi
}

summary_sys() {
  header "System"
  echo "Uptime: $(uptime -p || true)"
  echo "Load: $(uptime | sed 's/.*load average: //')"
  echo "Memory: $(free -h | awk '/Mem:/ {print $3 " used / " $2}')"
  echo "Disk: $(df -h / | awk 'NR==2 {print $3 " used / " $2 " (" $5 ")"}')"
}

summary_env() {
  header "Neo4j Env"
  if [[ -n "${NEO4J_AUTH:-}" ]]; then
    echo "NEO4J_AUTH present (masked): $(mask "$NEO4J_AUTH")"
  else
    echo "NEO4J_AUTH: absent"
  fi
}

summary_k8s() {
  header "Kubernetes"
  kubectl version --short || true
  echo
  echo "Contexts: $(kubectl config current-context 2>/dev/null || echo 'n/a')"
  echo
  kubectl get nodes -o wide || true
  echo
  kubectl get ns || true
  echo
  echo "--- Pods (all namespaces) ---"
  kubectl get pods -A -o wide || true
  echo
  echo "--- Neo4j resources (if any) ---"
  kubectl get pods -A | grep -i neo4j || echo "No neo4j pods found"
  kubectl get svc -A | grep -i neo4j || true
  kubectl get statefulset -A | grep -i neo4j || true
  echo
  echo "--- Probes (neo4j pods) ---"
  for ns in $(kubectl get ns -o jsonpath='{.items[*].metadata.name}'); do
    for pod in $(kubectl -n "$ns" get pods -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | grep -i neo4j || true); do
      echo "Pod: $ns/$pod"
      kubectl -n "$ns" get pod "$pod" -o json | jq -r '
        .spec.containers[]? |
        "  container: \(.name)\n  readinessProbe: \(.readinessProbe!=null)\n  livenessProbe: \(.livenessProbe!=null)"' || true
    done
  done
  echo
  echo "--- Recent logs (neo4j, last 100 lines) ---"
  for ns in $(kubectl get ns -o jsonpath='{.items[*].metadata.name}'); do
    for pod in $(kubectl -n "$ns" get pods -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | grep -i neo4j || true); do
      echo "Logs: $ns/$pod"
      kubectl -n "$ns" logs "$pod" --tail=100 || true
    done
  done
}

summary_docker() {
  header "Docker"
  docker version || true
  echo
  docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' || true
  echo
  if command -v docker compose >/dev/null 2>&1 || docker-compose version >/dev/null 2>&1; then
    header "Docker Compose"
    (docker compose ps || docker-compose ps) || true
    echo
    echo "--- Recent logs (neo4j*, last 100 lines) ---"
    for svc in $(docker ps --format '{{.Names}}' | grep -i neo4j || true); do
      echo "Logs: $svc"
      docker logs --tail=100 "$svc" || true
    done
  fi
}

summary_ci() {
  header "CI (optional via gh CLI)"
  if command -v gh >/dev/null 2>&1; then
    REPO="${1:-}"
    if [[ -n "$REPO" ]]; then
      gh run list -R "$REPO" -L 10 || true
    else
      echo "Set REPO (e.g., MOTEB1989/Top-TieR-Global-HUB-AI) to list recent runs."
    fi
  else
    echo "gh CLI not installed. Skip."
  fi
}

summary_neo4j_http() {
  header "Neo4j HTTP probe (optional)"
  local host="${NEO4J_HOST:-localhost}" port="${NEO4J_HTTP_PORT:-7474}"
  if command -v curl >/dev/null 2>&1; then
    echo "Probing http://$host:$port/"
    echo "WARNING: Using HTTP to connect to Neo4j may expose sensitive data. Use HTTPS in production or secure environments." >&2
    curl -fsS "http://$host:$port/" | head -n 5 || echo "Neo4j HTTP endpoint not reachable"
  else
    echo "curl not installed. Skip."
  fi
}

main() {
  summary_sys
  summary_env

  if command -v kubectl >/dev/null 2>&1 && kubectl cluster-info >/dev/null 2>&1; then
    summary_k8s
  elif command -v docker >/dev/null 2>&1; then
    summary_docker
  else
    header "Platform"
    echo "Neither Kubernetes nor Docker detected."
  fi

  summary_neo4j_http
  summary_ci "${REPO:-}"
}

main "$@"

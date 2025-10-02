#!/usr/bin/env bash
set -euo pipefail

missing_items=()

required_items=(
  "api_server"
  "veritas-web"
  "veritas-mini-web"
  "scripts"
)

for item in "${required_items[@]}"; do
  if [[ ! -e "$item" ]]; then
    missing_items+=("$item")
  fi
done

if [[ ${#missing_items[@]} -gt 0 ]]; then
  echo "Stack health check failed. Missing required items: ${missing_items[*]}" >&2
  exit 1
fi

echo "Stack health check passed. All required components are present."

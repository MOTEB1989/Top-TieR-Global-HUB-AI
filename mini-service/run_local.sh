#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
image="mini-safe"

echo "[build] Building $image ..."
docker build -t "$image" .

echo "[run] Starting container on host port 8085 -> container 8080"
docker run --rm -p 8085:8080 -e PORT=8080 "$image"

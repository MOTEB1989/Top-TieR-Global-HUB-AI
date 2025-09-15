#!/usr/bin/env bash
set -euo pipefail

# Wrapper to maintain compatibility with workflows
# Calls the status collection script
"$(dirname "$0")/status/collect_status.sh" "$@"

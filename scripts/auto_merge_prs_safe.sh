#!/bin/bash
# auto_merge_prs_safe.sh - دمج تلقائي آمن ومدروس للطلبات
# الإصدار: 1.1
set -euo pipefail

REPO="${REPO:-MOTEB1989/Top-TieR-Global-HUB-AI}"
MAIN_BRANCHES="${MAIN_BRANCHES:-main}"
DRY_RUN="${DRY_RUN:-true}"              # افتراضياً لا دمج فعلي
MAX_MERGE="${MAX_MERGE:-5}"             # الحد الأقصى في تشغيل واحد
REQUIRE_SUCCESS_CHECKS="${REQUIRE_SUCCESS_CHECKS:-true}"
EXCLUDE_LABELS="${EXCLUDE_LABELS:-wip,WIP,do-not-merge,blocked}"
EXCLUDE_TITLE_PATTERNS="${EXCLUDE_TITLE_PATTERNS:-\\[WIP\\],draft,DRAFT}"
LOG_DIR="logs"
RUN_ID="$(date -u +%Y%m%d_%H%M%S)"
LOG_FILE="${LOG_DIR}/auto_merge_${RUN_ID}.log"

mkdir -p "${LOG_DIR}"

log() { echo -e "$*" | tee -a "${LOG_FILE}"; }
fai...n   if [[ "
# 1090
# 1066

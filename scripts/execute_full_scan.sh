#!/bin/bash
# execute_full_scan.sh - تنفيذ آمن لفحص هيكل المستودع مع إغلاق مضبوط (اختياري)
# الإصدار: 1.0 (نسخة محسّنة)
# المتطلبات: gh CLI, jq, python, وجود السكربت: scripts/generate_repo_structure.py

set -euo pipefail

REPO="${REPO:-MOTEB1989/Top-TieR-Global-HUB-AI}"
TARGET_PR="${TARGET_PR:-1090}"
DRY_RUN="${DRY_RUN:-true}"
MAX_CLOSE="${MAX_CLOSE:-0}"
FORCE_FULL_CLOSE="${FORCE_FULL_CLOSE:-false}"
EXCLUSIONS_FILE="${EXCLUSIONS_FILE:-exclusions.txt}"
STATE_DIR="state"
LOG_DIR="logs"
STRUCT_SCRIPT="${STRUCT_SCRIPT:-scripts/generate_repo_structure.py}"
OUTPUT_JSON="repo_structure.json"
STATE_FILE="${STATE_DIR}/scan_last_run.json"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
RUN_ID="$(date -u +%Y%m%d_%H%M%S)"
LOG_FILE="${LOG_DIR}/scan_run_${RUN_ID}.log"

mkdir -p "${STATE_DIR}" "${LOG_DIR}"

log() { echo -e "$*" | tee -a "${LOG_FILE}"; }
fai...US}
if [[ -f "${EXCLUSIONS_FILE}" ]]; then
    while IFS= read -r line; do
      [[ -z "$line" || "$line" =~ ^# ]] && continue
      EXCLUDED["$line"]=1
    done < "${EXCLUSIONS_FILE}"
    log "📄 تم تحميل الاستثناءات من ${EXCLUSIONS_FILE}: ${!EXCLUDED[*]:-لا شيء}"
else
    log "ℹ️ لا يوجد ملف استثناءات (${EXCLUSIONS_FILE})."
fi

log "🔍 جمع الـ Issues المفتوحة..."
mapfile -t ISSUE_NUMBERS < <(gh issue list --state open --json number -q '.[].number')
log "🔍 جمع الـ PRs المفتوحة..."
mapfile -t PR_NUMBERS < <(gh pr list --state open --json number -q '.[].number')

log "📊 إحصائية أولية:"
log "   - عدد الـ Issues المفتوحة: ${#ISSUE_NUMBERS[@]}"
log "   - عدد الـ PRs المفتوحة: ${#PR_NUMBERS[@]}"

close_counter=0
closed_items=()

can_close() {
  local id="$1"
  [[ -n "${EXCLUDED[$id]:-}" ]] && { log "⏭️ تجاهل #$id (مستثنى)"; return 1; }
  [[ "$id" == "${TARGET_PR}" ]] && { log "⏭️ تجاهل PR #$id (هو الهدف للفحص)"; return 1; }
  (( close_counter >= MAX_CLOSE )) && { log "⏭️ وصلنا للحد الأقصى MAX_CLOSE=${MAX_CLOSE}"; return 1; }
  return 0
}

close_issue() {
  local id="$1"
  if [[ "${DRY_RUN}" == "true" ]]; then
    log "DRY_RUN: سيُغلق Issue #${id}"
  else
    gh issue close "${id}" --comment "🧹 Closed via structured scan (controlled). Reopen if needed." \
      && { log "✅ Closed Issue #${id}"; closed_items+=("issue:${id}"); ((close_counter++)); } \
      || log "⚠️ فشل إغلاق Issue #${id}"
  fi
}

close_pr() {
  local id="$1"
  if [[ "${DRY_RUN}" == "true" ]]; then
    log "DRY_RUN: سيُغلق PR #${id}"
  else
    gh pr close "${id}" --comment "🧹 Closed via structured scan (controlled). Reopen if needed." \
      && { log "✅ Closed PR #${id}"; closed_items+=("pr:${id}"); ((close_counter++)); } \
      || log "⚠️ فشل إغلاق PR #${id}"
  fi
}

log "🛡️ إعدادات الإغلاق:"
log "   DRY_RUN=${DRY_RUN}"
log "   MAX_CLOSE=${MAX_CLOSE}"
log "   FORCE_FULL_CLOSE=${FORCE_FULL_CLOSE}"

if [[ "${FORCE_FULL_CLOSE}" == "true" && "${DRY_RUN}" == "false" && "${MAX_CLOSE}" -gt 0 ]]; then
  log "🚨 وضع الإغلاق الفعلي مفعّل (دقيق ومحدود)."
else
  log "⚠️ الإغلاق الفعلي غير مفعل (لن يُغلق شيء) حتى إعداد FORCE_FULL_CLOSE=true و DRY_RUN=false و MAX_CLOSE>0."
fi

for iid in "${ISSUE_NUMBERS[@]}"; do
  can_close "$iid" || continue
  if [[ "${FORCE_FULL_CLOSE}" == "true" && "${DRY_RUN}" == "false" ]]; then
    close_issue "$iid"
  else
    log "DRY_RUN: (لن يُغلق فعلياً) Issue #$iid"
  fi
 done

for pid in "${PR_NUMBERS[@]}"; do
  can_close "$pid" || continue
  if [[ "${FORCE_FULL_CLOSE}" == "true" && "${DRY_RUN}" == "false" ]]; then
    close_pr "$pid"
  else
    log "DRY_RUN: (لن يُغلق فعلياً) PR #$pid"
  fi
 done

log "📦 إجمالي العناصر (مغلقة أو افتراضية في DRY_RUN): ${close_counter}"

log "🔄 التحقق من وجود PR الهدف #${TARGET_PR}..."
if ! gh pr view "${TARGET_PR}" --json number >/dev/null 2>&1; then
  fail "PR #${TARGET_PR} غير موجود. عدل TARGET_PR أو تأكد من الرقم."
fi

log "🔄 تنفيذ gh pr checkout ${TARGET_PR}..."
gh pr checkout "${TARGET_PR}"

[[ -f "${STRUCT_SCRIPT}" ]] || fail "ملف السكربت ${STRUCT_SCRIPT} غير موجود."
log "🔍 تشغيل السكربت: python ${STRUCT_SCRIPT}"
python "${STRUCT_SCRIPT}" || fail "فشل تشغيل سكربت الفحص."

if [[ ! -s "${OUTPUT_JSON}" ]]; then
  fail "الملف ${OUTPUT_JSON} غير موجود أو فارغ."
fi

if ! jq . "${OUTPUT_JSON}" >/dev/null 2>&1; then
  fail "الملف ${OUTPUT_JSON} ليس JSON صالح."
fi

TOTAL_FILES=$(jq '.files | length' "${OUTPUT_JSON}" 2>/dev/null || echo 0)
TOTAL_SIZE=$(jq '[.files[].size] | add' "${OUTPUT_JSON}" 2>/dev/null || echo 0)
TOP_EXT=$(jq -r '[.files[].name | capture("(?<ext>\.[^.]+)$")?.ext] | map(select(.!=null)) | group_by(.) | map({ext:.[0], count:length}) | sort_by(-.count) | .[:5]' "${OUTPUT_JSON}" 2>/dev/null || echo '[]')

SUMMARY_JSON=$(jq -n \
  --arg ts "${TIMESTAMP}" \
  --arg repo "${REPO}" \
  --arg target_pr "${TARGET_PR}" \
  --arg dry "${DRY_RUN}" \
  --arg max_close "${MAX_CLOSE}" \
  --arg force "${FORCE_FULL_CLOSE}" \
  --arg total_files "${TOTAL_FILES}" \
  --arg total_size "${TOTAL_SIZE}" \
  --argjson top_ext "${TOP_EXT}" \
  --argjson closed "$(printf '%s\n' "${closed_items[@]}" | jq -R -s 'split("\n")[:-1]')" \
  '{
     timestamp: $ts,
     repository: $repo,
     target_pr: $target_pr,
     dry_run: $dry,
     max_close: ($max_close|tonumber),
     force_full_close: ($force=="true"),
     total_files: ($total_files|tonumber),
     total_size_bytes: ($total_size|tonumber),
     top_extensions: $top_ext,
     closed_items: $closed
   }')

echo "${SUMMARY_JSON}" > "${STATE_FILE}"
log "🗂 حفظ حالة التشغيل في ${STATE_FILE}"

COMMENT_HEADER="### 📊 نتائج فحص هيكل المستودع (نسخة محسّنة)\n"
COMMENT_SUMMARY=$(jq -r '. | {
  timestamp,
  total_files,
  total_size_bytes,
  max_close,
  force_full_close,
  dry_run
} | to_entries | map("* " + .key + ": " + (.value|tostring)) | join("\n")' <<< "${SUMMARY_JSON}")

FILE_SIZE_BYTES=$(wc -c < "${OUTPUT_JSON}")
ATTACH_FULL="true"
MAX_INLINE_BYTES=25000
if (( FILE_SIZE_BYTES > MAX_INLINE_BYTES )); then
  ATTACH_FULL="false"
  log "ℹ️ ملف ${OUTPUT_JSON} حجمه ${FILE_SIZE_BYTES} (> ${MAX_INLINE_BYTES}). سيتم تضمين ملخص فقط."
fi

COMMENT_BODY="${COMMENT_HEADER}${COMMENT_SUMMARY}\n\n"
COMMENT_BODY+="Top extensions (limit 5):\n"
COMMENT_BODY+=$(jq -r '.top_extensions | map("* " + .ext + " → " + (.count|tostring)) | join("\n")' <<< "${SUMMARY_JSON}")
COMMENT_BODY+="\n\n"

if [[ "${ATTACH_FULL}" == "true" ]]; then
  SAFE_JSON=$(jq '.' "${OUTPUT_JSON}")
  COMMENT_BODY+="التقرير الكامل:\n\`
"json\n${SAFE_JSON}\n\`
\n"
else
  COMMENT_BODY+="التقرير الكامل كبير؛ احفظ الملف محلياً أو أرفقه كـ artifact.\n"
fi

COMMENT_BODY+="\nوضع الإغلاق: DRY_RUN=${DRY_RUN} | MAX_CLOSE=${MAX_CLOSE} | FORCE_FULL_CLOSE=${FORCE_FULL_CLOSE}\n"

if [[ "${DRY_RUN}" == "true" ]]; then
  log "DRY_RUN: لن يتم نشر تعليق على PR #${TARGET_PR}"
  log "----- محتوى التعليق (معاينة) -----"
  echo -e "${COMMENT_BODY}" | tee -a "${LOG_FILE}"
else
  log "📤 نشر تعليق على PR #${TARGET_PR}..."
  gh pr comment "${TARGET_PR}" --body "${COMMENT_BODY}"
  log "✅ تم نشر التعليق."
fi

log "✅ التشغيل اكتمل بنجاح!"
exit 0

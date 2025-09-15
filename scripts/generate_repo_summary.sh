#!/usr/bin/env bash
set -euo pipefail
OUT="repo_summary.txt"
echo "Repository summary generated on $(date --iso-8601=seconds)" > "$OUT"
echo "" >> "$OUT"

echo "Top-level entries:" >> "$OUT"
ls -1 | sed -n '1,200p' >> "$OUT"
echo "" >> "$OUT"

echo "Files count by extension:" >> "$OUT"
find . -type f ! -path "./.git/*" -printf "%f\n" | sed -n '1,200000p' \
  | awk -F. 'NF>1{print $NF; next} {print "noext"}' \
  | sort | uniq -c | sort -rn >> "$OUT"
echo "" >> "$OUT"

echo "Top 40 largest files (size bytes):" >> "$OUT"
find . -type f ! -path "./.git/*" -printf "%s %p\n" | sort -nr | head -n 40 >> "$OUT"
echo "" >> "$OUT"

echo "Important files preview (README*, Dockerfile, .github/workflows/*, package.json, pyproject.toml, requirements.txt, scripts/*):" >> "$OUT"
for f in README* Dockerfile package.json package-lock.json pyproject.toml requirements.txt setup.py Pipfile .github/workflows/* scripts/*; do
  if [ -f "$f" ]; then
    echo "=== $f ===" >> "$OUT"
    echo "" >> "$OUT"
    head -n 40 "$f" >> "$OUT"
    echo "" >> "$OUT"
  fi
done
echo "" >> "$OUT"

echo "File list (up to first 2000 files):" >> "$OUT"
find . -type f ! -path "./.git/*" | sed 's|^\./||' | sort | head -n 2000 >> "$OUT"

echo "Done. Output written to $OUT"
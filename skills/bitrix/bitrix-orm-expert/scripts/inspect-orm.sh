#!/usr/bin/env bash
set -euo pipefail

site_root="${1:-$(pwd)}"
orm_dir="${site_root%/}/bitrix/modules/main/lib/orm"

if [[ ! -d "$orm_dir" ]]; then
  echo "ORM directory not found: $orm_dir" >&2
  echo "Usage: $0 <site-root>" >&2
  exit 1
fi

echo "ORM directory: $orm_dir"
echo "Files: $(find "$orm_dir" -type f -name '*.php' | wc -l | tr -d ' ')"
echo "Lines: $(find "$orm_dir" -type f -name '*.php' -print0 | xargs -0 wc -l | tail -1 | awk '{print $1}')"
echo
echo "Subsystems:"
find "$orm_dir" -type f -name '*.php' \
  | sed "s#^$orm_dir/##" \
  | awk -F/ '{print (NF == 1 ? "(root)" : $1)}' \
  | sort | uniq -c | sort -nr
echo
echo "Public API:"
rg -n '^[[:space:]]*(final[[:space:]]+)?public[[:space:]]+(static[[:space:]]+)?function[[:space:]]+' "$orm_dir" || true
echo
echo "Classes, interfaces and traits:"
rg -n '^(abstract[[:space:]]+|final[[:space:]]+)?(class|interface|trait)[[:space:]]+' "$orm_dir" || true

#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=1
if [ "${1:-}" = "--apply" ]; then
  DRY_RUN=0
fi

paths=(
  "${HOME}/printer_data/config.update-backup-"*
  "${HOME}/printer_data/config.backup-"*
  "${HOME}/axiscope.bak"
)

echo "Cleanup candidates:"
for path in "${paths[@]}"; do
  [ -e "${path}" ] || continue
  echo "  ${path}"
done

if [ "${DRY_RUN}" -eq 1 ]; then
  echo
  echo "Dry run only. To remove these candidates:"
  echo "  bash ~/printer_data/config/scripts/cleanup-voron.sh --apply"
  exit 0
fi

echo
echo "Removing cleanup candidates."
for path in "${paths[@]}"; do
  [ -e "${path}" ] || continue
  rm -rf -- "${path}"
done

echo "Cleanup complete."

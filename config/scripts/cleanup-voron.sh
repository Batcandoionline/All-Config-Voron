#!/usr/bin/env bash
set -euo pipefail

APPLY=0
if [[ "${1:-}" == "--apply" ]]; then
  APPLY=1
elif [[ -n "${1:-}" ]]; then
  echo "Usage: $0 [--apply]" >&2
  exit 2
fi

PRINTER_DATA="$(realpath -m "${HOME}/printer_data")"
CONFIG_DIR="${PRINTER_DATA}/config"
BACKUP_ROOT="${PRINTER_DATA}/config_backups"

mapfile -d '' CANDIDATES < <(
  find "${PRINTER_DATA}" -maxdepth 1 -mindepth 1 \
    \( -name 'config.update-backup-*' -o -name 'config.backup-*' \) \
    -print0
)
if [[ -e "${HOME}/axiscope.bak" ]]; then
  CANDIDATES+=("${HOME}/axiscope.bak")
fi

# Also find markdown documentation inside CONFIG_DIR
if [[ -d "${CONFIG_DIR}" ]]; then
  while IFS= read -r -d '' md_file; do
    CANDIDATES+=("${md_file}")
  done < <(find "${CONFIG_DIR}" -maxdepth 1 -type f \( -name "*.md" -o -name "*.markdown" \) -print0)
fi

# Find old config_backups beyond the 5 most recent
if [[ -d "${BACKUP_ROOT}" ]]; then
  while IFS= read -r old_backup; do
    if [[ -n "${old_backup}" ]]; then
      CANDIDATES+=("${old_backup}")
    fi
  done < <(find "${BACKUP_ROOT}" -maxdepth 1 -mindepth 1 -type d -name "config-install-*" | sort -r | tail -n +6)
fi

if [[ ${#CANDIDATES[@]} -eq 0 ]]; then
  echo "No cleanup candidates found. System is already lean."
  exit 0
fi

echo "Cleanup candidates:"
printf '  %s\n' "${CANDIDATES[@]}"
if [[ ${APPLY} -eq 0 ]]; then
  echo "Dry run only. Re-run with --apply to remove listed files."
  exit 0
fi

for candidate in "${CANDIDATES[@]}"; do
  resolved="$(realpath -m "${candidate}")"
  case "${resolved}" in
    "${PRINTER_DATA}"/config.update-backup-*|"${PRINTER_DATA}"/config.backup-*|"${HOME}/axiscope.bak"|"${CONFIG_DIR}"/*.md|"${CONFIG_DIR}"/*.markdown|"${BACKUP_ROOT}"/config-install-*)
      rm -rf -- "${resolved}"
      ;;
    *)
      echo "ERROR: refusing unexpected path: ${resolved}" >&2
      exit 1
      ;;
  esac
done

echo "Cleanup complete. Removed all selected excess and legacy candidates."


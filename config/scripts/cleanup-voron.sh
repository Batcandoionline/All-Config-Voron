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
mapfile -d '' CANDIDATES < <(
  find "${PRINTER_DATA}" -maxdepth 1 -mindepth 1 \
    \( -name 'config.update-backup-*' -o -name 'config.backup-*' \) \
    -print0
)
if [[ -e "${HOME}/axiscope.bak" ]]; then
  CANDIDATES+=("${HOME}/axiscope.bak")
fi

if [[ ${#CANDIDATES[@]} -eq 0 ]]; then
  echo "No legacy cleanup candidates found."
  exit 0
fi

echo "Legacy cleanup candidates:"
printf '  %s\n' "${CANDIDATES[@]}"
if [[ ${APPLY} -eq 0 ]]; then
  echo "Dry run only. Re-run with --apply after reviewing every path."
  exit 0
fi

for candidate in "${CANDIDATES[@]}"; do
  resolved="$(realpath -m "${candidate}")"
  case "${resolved}" in
    "${PRINTER_DATA}"/config.update-backup-*|"${PRINTER_DATA}"/config.backup-*|"${HOME}/axiscope.bak")
      rm -rf -- "${resolved}"
      ;;
    *)
      echo "ERROR: refusing unexpected path: ${resolved}" >&2
      exit 1
      ;;
  esac
done

echo "Cleanup complete. Removed only the listed legacy candidates."

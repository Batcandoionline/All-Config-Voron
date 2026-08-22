#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HOME}/printer_data/config"
BACKUP_ROOT="${HOME}/printer_data/config_backups"
BACKUP_DIR="${BACKUP_ROOT}/config-install-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_CONFIG_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TOOL_CRASH_SOURCE="${HOME}/klipper/klippy/extras/tool_crash.py"
TOOL_CRASH_PATCH="${SCRIPT_DIR}/patches/tool_crash-active-tool-validation.patch"
TOOL_CRASH_PATCH_MARKER="Every tool detection pin is registered with this same callback"
TOOL_CRASH_PATCH_NEEDED=0
KTAMV_CLIENT="${HOME}/klipper/klippy/extras/ktamv.py"
KTAMV_UTILITY="${HOME}/klipper/klippy/extras/ktamv_utl.py"
KTAMV_DETECTOR="${HOME}/kTAMV/server/ktamv_server_dm.py"

if [[ ! -f "${SOURCE_CONFIG_DIR}/printer.cfg" ]]; then
  echo "ERROR: printer.cfg was not found in ${SOURCE_CONFIG_DIR}" >&2
  exit 1
fi

# The temporary kTAMV trial is installed manually instead of using its
# system-wide upstream installer. Refuse to deploy an active include unless the
# reviewed client links and multi-object detector fix are present.
if grep -Fq '[include Printer-Setup/ktamv.cfg]' \
    "${SOURCE_CONFIG_DIR}/printer.cfg"; then
  for required_file in "${KTAMV_CLIENT}" "${KTAMV_UTILITY}" \
      "${KTAMV_DETECTOR}"; do
    if [[ ! -f "${required_file}" ]]; then
      echo "ERROR: active kTAMV trial runtime is missing: ${required_file}" >&2
      exit 1
    fi
  done
  if ! grep -Fq 'def find_closest_keypoint(self, keypoints):' \
      "${KTAMV_DETECTOR}" ||
      ! grep -Fq 'np.around(keypoints[closest_index].pt)' \
      "${KTAMV_DETECTOR}"; then
    echo "ERROR: reviewed kTAMV multi-object selection patch is missing." >&2
    exit 1
  fi
fi

# Preflight the machine-local tool_crash runtime before deploying config. The
# upstream plugin is an independent checkout/copy, so All-Config stores only a
# minimal downstream patch and reapplies it after a future upstream reinstall.
if [[ -f "${TOOL_CRASH_PATCH}" ]]; then
  if [[ ! -f "${TOOL_CRASH_SOURCE}" ]]; then
    echo "WARNING: tool_crash.py is not installed; runtime patch was skipped." >&2
  elif grep -Fq "${TOOL_CRASH_PATCH_MARKER}" "${TOOL_CRASH_SOURCE}"; then
    echo "tool_crash active-tool validation patch is already installed."
  elif patch --dry-run --fuzz=0 --forward --batch \
      -d "$(dirname "${TOOL_CRASH_SOURCE}")" -p1 \
      < "${TOOL_CRASH_PATCH}" >/dev/null; then
    TOOL_CRASH_PATCH_NEEDED=1
  else
    echo "ERROR: installed tool_crash.py does not match the reviewed upstream source." >&2
    echo "Refusing to deploy configuration without a valid crash-detector patch." >&2
    exit 1
  fi
fi

mkdir -p "${CONFIG_DIR}" "${BACKUP_DIR}"
if [[ -d "${CONFIG_DIR}" ]]; then
  rsync -a "${CONFIG_DIR}/" "${BACKUP_DIR}/"
fi

# Preserve installer-owned KTC links when they already exist. A fresh payload
# may copy the bundled baseline so printer.cfg never points at missing files.
READONLY_EXCLUDE=()
if [[ -e "${CONFIG_DIR}/toolchanger/readonly-configs" ]]; then
  READONLY_EXCLUDE=(--exclude "toolchanger/readonly-configs/")
fi

# Deploy only repository-owned configuration. On-printer backups, calibration
# state/results, ShakeTune output, downloaded snapshots, and printer-local
# files remain untouched. External Git runtimes live outside CONFIG_DIR.
rsync -a --delete --itemize-changes \
  --exclude ".codex-backups/" \
  --exclude ".moonraker.conf.bkp" \
  --exclude "Generated-Data/" \
  --exclude "ShakeTune_results/" \
  --exclude "Nhat-ky-chinh-sua/" \
  --exclude "/tool_vision_state.json" \
  --exclude "/tool_vision_results.json" \
  --exclude "config-*.zip" \
  --exclude "moonraker.conf.pre-*" \
  "${READONLY_EXCLUDE[@]}" \
  --exclude "README.md" \
  --exclude "*.md" \
  "${SOURCE_CONFIG_DIR}/" "${CONFIG_DIR}/"

if (( TOOL_CRASH_PATCH_NEEDED )); then
  mkdir -p "${BACKUP_DIR}/runtime"
  cp -a "${TOOL_CRASH_SOURCE}" "${BACKUP_DIR}/runtime/tool_crash.py"
  patch --fuzz=0 --forward --batch \
    -d "$(dirname "${TOOL_CRASH_SOURCE}")" -p1 \
    < "${TOOL_CRASH_PATCH}" >/dev/null
  echo "Installed tool_crash active-tool validation patch."
fi

echo "Installed configuration from ${SOURCE_CONFIG_DIR}"
echo "Backup: ${BACKUP_DIR}"
if [[ ! -L "${CONFIG_DIR}/toolchanger/readonly-configs/toolchanger.cfg" ]]; then
  echo "WARNING: KTC readonly configs are not installer-managed symlinks." >&2
  echo "Repair them with the installed KTC-Easy installer before upgrading KTC." >&2
fi
echo "Review changes, then restart Moonraker and Klipper only while the printer is idle."

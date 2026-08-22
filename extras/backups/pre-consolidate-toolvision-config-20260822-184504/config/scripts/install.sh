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

if [[ ! -f "${SOURCE_CONFIG_DIR}/printer.cfg" ]]; then
  echo "ERROR: printer.cfg was not found in ${SOURCE_CONFIG_DIR}" >&2
  exit 1
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

# Deploy only repository-owned configuration. On-printer backups, Tool Vision
# state/results, ShakeTune output, downloaded snapshots, and printer-local
# files remain untouched.
rsync -a --delete --itemize-changes \
  --exclude ".codex-backups/" \
  --exclude ".moonraker.conf.bkp" \
  --exclude "Generated-Data/" \
  --exclude "ShakeTune_results/" \
  --exclude "Tool-Vision/" \
  --exclude "Nhat-ky-chinh-sua/" \
  --exclude "tool_vision_state.json" \
  --exclude "tool_vision_results.json" \
  --exclude "config-*.zip" \
  --exclude "moonraker.conf.pre-*" \
  "${READONLY_EXCLUDE[@]}" \
  --exclude "README.md" \
  --exclude "*.md" \
  "${SOURCE_CONFIG_DIR}/" "${CONFIG_DIR}/"

# Tool Vision remains an independent runtime, but its one editable machine
# config is managed by All-Config without deleting result/local files beside it.
if [[ -f "${SOURCE_CONFIG_DIR}/Tool-Vision/tool_vision.cfg" ]]; then
  mkdir -p "${CONFIG_DIR}/Tool-Vision"
  rsync -a "${SOURCE_CONFIG_DIR}/Tool-Vision/tool_vision.cfg" \
    "${CONFIG_DIR}/Tool-Vision/tool_vision.cfg"
fi

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

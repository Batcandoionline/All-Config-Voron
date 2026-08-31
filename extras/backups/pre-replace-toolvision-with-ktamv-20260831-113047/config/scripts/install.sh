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
TOOL_VISION_RUNTIME="${HOME}/Tool-Vision"
TOOL_VISION_VENV="${HOME}/tool-vision-env/bin/python"
TOOL_VISION_SERVICE="/etc/systemd/system/tool-vision.service"
TOOL_VISION_MODULES=(
  "tool_vision.py"
  "tool_vision_client.py"
  "tool_vision_state.py"
  "tool_vision_toolchanger.py"
  "tool_vision_z.py"
)
KTC_READONLY_DIR="${CONFIG_DIR}/toolchanger/readonly-configs"
KTC_READONLY_FILES=(
  "calibrate-offsets.cfg"
  "crash-detection.cfg"
  "homing.cfg"
  "toolchanger-include.cfg"
  "toolchanger-macros.cfg"
  "toolchanger.cfg"
)

if [[ ! -f "${SOURCE_CONFIG_DIR}/printer.cfg" ]]; then
  echo "ERROR: printer.cfg was not found in ${SOURCE_CONFIG_DIR}" >&2
  exit 1
fi

# KTC-Easy is the sole owner of readonly-configs. All-Config deploys only the
# user-owned toolchanger-config.cfg and tools/T*.cfg files. Refuse deployment
# when the official installer-managed links are missing or have broken targets.
KTC_INVALID_LINKS=()
for file in "${KTC_READONLY_FILES[@]}"; do
  path="${KTC_READONLY_DIR}/${file}"
  if [[ ! -L "${path}" || ! -e "${path}" ]]; then
    KTC_INVALID_LINKS+=("${path}")
  fi
done
if (( ${#KTC_INVALID_LINKS[@]} )); then
  echo "ERROR: KTC-Easy readonly links are missing, not symlinks, or broken:" >&2
  printf '  - %s\n' "${KTC_INVALID_LINKS[@]}" >&2
  echo "Run bash ~/klipper-toolchanger-easy/install.sh while the printer is idle," >&2
  echo "then retry this deployment. No configuration was changed." >&2
  exit 1
fi

# ToolVision owns the PF2 switch during this canary. Refuse to deploy the
# include unless the reviewed Git runtime, isolated Python and all five Klipper
# extension links already exist on the machine.
if grep -Eq '^[[:space:]]*\[include[[:space:]]+Printer-Setup/tool-vision\.cfg\][[:space:]]*$' \
    "${SOURCE_CONFIG_DIR}/printer.cfg"; then
  if [[ ! -d "${TOOL_VISION_RUNTIME}/.git" || ! -x "${TOOL_VISION_VENV}" || \
        ! -f "${TOOL_VISION_SERVICE}" ]]; then
    echo "ERROR: ToolVision runtime, venv, or systemd unit is missing." >&2
    echo "Expected: ${TOOL_VISION_RUNTIME}, ${TOOL_VISION_VENV}, ${TOOL_VISION_SERVICE}" >&2
    exit 1
  fi
  for module in "${TOOL_VISION_MODULES[@]}"; do
    source_path="${TOOL_VISION_RUNTIME}/klippy/extras/${module}"
    link_path="${HOME}/klipper/klippy/extras/${module}"
    if [[ ! -f "${source_path}" || ! -L "${link_path}" || ! -e "${link_path}" || \
          "$(readlink -f "${link_path}")" != "$(readlink -f "${source_path}")" ]]; then
      echo "ERROR: ToolVision Klipper link is missing or invalid: ${link_path}" >&2
      exit 1
    fi
  done
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

# Deploy only repository-owned configuration. On-printer backups, calibration
# state/results, ShakeTune output, downloaded snapshots, and printer-local
# files remain untouched. KTC-Easy owns readonly-configs and external Git
# runtimes live outside CONFIG_DIR.
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
  --exclude "toolchanger/readonly-configs/" \
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
echo "KTC-Easy readonly symlinks were verified and preserved."
echo "Review changes, then restart Moonraker and Klipper only while the printer is idle."

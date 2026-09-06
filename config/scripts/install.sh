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
KTAMV_RUNTIME="${HOME}/kTAMV"
KTAMV_REVIEWED_COMMIT="72421f2d54da0de8701c4f84449c6e6b7d060301"
KTAMV_VENV="${HOME}/ktamv-env/bin/python"
KTAMV_SERVICE="${HOME}/.config/systemd/user/ktamv-server.service"
KTAMV_CLIENT_SOURCE="${KTAMV_RUNTIME}/extension/ktamv.py"
KTAMV_UTILITY_SOURCE="${KTAMV_RUNTIME}/extension/ktamv_utl.py"
KTAMV_DETECTOR="${KTAMV_RUNTIME}/server/ktamv_server_dm.py"
KTAMV_CLIENT_PATCH_MARKER='minimum_count = max(1, initial_count - 1)'
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

# kTAMV is installed manually instead of using its system-wide upstream
# installer. Refuse to deploy the active include unless the pinned checkout,
# isolated Python, user service, exact Klipper links and reviewed runtime fixes
# exist.
if grep -Eq '^[[:space:]]*\[include[[:space:]]+Printer-Setup/ktamv\.cfg\][[:space:]]*$' \
    "${SOURCE_CONFIG_DIR}/printer.cfg"; then
  if [[ ! -d "${KTAMV_RUNTIME}/.git" || ! -x "${KTAMV_VENV}" || \
        ! -f "${KTAMV_SERVICE}" ]]; then
    echo "ERROR: kTAMV runtime, venv, or user service is missing." >&2
    echo "Expected: ${KTAMV_RUNTIME}, ${KTAMV_VENV}, ${KTAMV_SERVICE}" >&2
    exit 1
  fi
  if [[ "$(git -C "${KTAMV_RUNTIME}" rev-parse HEAD 2>/dev/null || true)" != \
        "${KTAMV_REVIEWED_COMMIT}" ]]; then
    echo "ERROR: kTAMV checkout is not at reviewed commit ${KTAMV_REVIEWED_COMMIT}." >&2
    exit 1
  fi
  for source_path in "${KTAMV_CLIENT_SOURCE}" "${KTAMV_UTILITY_SOURCE}"; do
    link_path="${HOME}/klipper/klippy/extras/$(basename "${source_path}")"
    if [[ ! -f "${source_path}" || ! -L "${link_path}" || ! -e "${link_path}" || \
          "$(readlink -f "${link_path}")" != "$(readlink -f "${source_path}")" ]]; then
      echo "ERROR: kTAMV Klipper link is missing or invalid: ${link_path}" >&2
      exit 1
    fi
  done
  if ! grep -Fq 'def find_closest_keypoint(self, keypoints):' \
      "${KTAMV_DETECTOR}" ||
      ! grep -Fq 'np.around(keypoints[closest_index].pt)' \
      "${KTAMV_DETECTOR}" ||
      ! grep -Fq 'def find_center_highlight_keypoint(self, frame):' \
      "${KTAMV_DETECTOR}" ||
      ! grep -Fq 'self.__algorithm = 6' "${KTAMV_DETECTOR}" ||
      ! grep -Fq 'stdev(mpps) if len(mpps) > 1 else 0.0' \
      "${KTAMV_UTILITY_SOURCE}" ||
      ! grep -Fq 'def cmd_MEASURE_TOOL_XY(self, gcmd):' \
      "${KTAMV_CLIENT_SOURCE}" ||
      ! grep -Fq 'mpps = mpps.copy()' "${KTAMV_UTILITY_SOURCE}" ||
      ! grep -Fq 'camera_coordinates.remove(camera_coordinates[i])' \
      "${KTAMV_UTILITY_SOURCE}" ||
      ! grep -Fq "${KTAMV_CLIENT_PATCH_MARKER}" "${KTAMV_CLIENT_SOURCE}"; then
    echo "ERROR: one or more reviewed kTAMV runtime patches are missing." >&2
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
  --exclude "config-*.zip" \
  --exclude "moonraker.conf.pre-*" \
  --exclude "toolchanger/readonly-configs/" \
  --exclude "README.md" \
  --exclude "*.md" \
  "${SOURCE_CONFIG_DIR}/" "${CONFIG_DIR}/"

# Purge any leftover markdown documentation from config directory to keep printer lean
find "${CONFIG_DIR}" -maxdepth 1 -type f \( -name "*.md" -o -name "*.markdown" \) -delete 2>/dev/null || true

# Prune old config backups on the printer, keeping only the 5 most recent
if [[ -d "${BACKUP_ROOT}" ]]; then
  mapfile -t OLD_BACKUPS < <(
    find "${BACKUP_ROOT}" -maxdepth 1 -mindepth 1 -type d -name "config-install-*" | sort -r | tail -n +6
  )
  for old_backup in "${OLD_BACKUPS[@]:-}"; do
    if [[ -n "${old_backup}" && -d "${old_backup}" ]]; then
      rm -rf -- "${old_backup}"
    fi
  done
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
echo "KTC-Easy readonly symlinks were verified and preserved."
echo "The pinned kTAMV runtime and detector patch were verified."
echo "Review changes, then restart Moonraker and Klipper only while the printer is idle."

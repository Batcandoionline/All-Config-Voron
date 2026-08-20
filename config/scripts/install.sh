#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HOME}/printer_data/config"
BACKUP_ROOT="${HOME}/printer_data/config_backups"
BACKUP_DIR="${BACKUP_ROOT}/config-install-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_CONFIG_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ ! -f "${SOURCE_CONFIG_DIR}/printer.cfg" ]]; then
  echo "ERROR: printer.cfg was not found in ${SOURCE_CONFIG_DIR}" >&2
  exit 1
fi

mkdir -p "${CONFIG_DIR}" "${BACKUP_DIR}"
rsync -a "${CONFIG_DIR}/" "${BACKUP_DIR}/"

# Deploy only repository-owned configuration. Installer-owned KTC links,
# Tool Vision, on-printer backups, and local Markdown remain untouched.
rsync -a --delete --itemize-changes \
  --exclude ".codex-backups/" \
  --exclude ".moonraker.conf.bkp" \
  --exclude "Tool-Vision/" \
  --exclude "Nhat-ky-chinh-sua/" \
  --exclude "toolchanger/readonly-configs/" \
  --exclude "README.md" \
  --exclude "*.md" \
  "${SOURCE_CONFIG_DIR}/" "${CONFIG_DIR}/"

echo "Installed configuration from ${SOURCE_CONFIG_DIR}"
echo "Backup: ${BACKUP_DIR}"
if [[ ! -L "${CONFIG_DIR}/toolchanger/readonly-configs/toolchanger.cfg" ]]; then
  echo "WARNING: KTC readonly configs are not installer-managed symlinks." >&2
  echo "Repair them with the installed KTC-Easy installer before upgrading KTC." >&2
fi
echo "Review changes, then restart Moonraker and Klipper only while the printer is idle."

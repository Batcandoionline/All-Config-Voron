#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HOME}/printer_data/config"
REPO_URL="git@github.com:IDcrazy123/All-Config-Voron.git"
REPO_DIR="${HOME}/All-Config-Voron"
BACKUP_ROOT="${HOME}/printer_data/config_backups"
BACKUP_KEEP="${BACKUP_KEEP:-10}"
BACKUP_DIR="${BACKUP_ROOT}/config-$(date +%Y%m%d-%H%M%S)"

if [ -d "${REPO_DIR}/.git" ]; then
  echo "Updating source repository: ${REPO_DIR}"
  git -C "${REPO_DIR}" pull --ff-only
else
  echo "Cloning source repository to: ${REPO_DIR}"
  git clone "${REPO_URL}" "${REPO_DIR}"
fi

echo "Backing up current config to: ${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"
rsync -a "${CONFIG_DIR}/" "${BACKUP_DIR}/"

echo "Copying latest config files."
rsync -a --delete --delete-excluded --exclude "Nhat-ky-chinh-sua/" "${REPO_DIR}/config/" "${CONFIG_DIR}/"

if [ "${BACKUP_KEEP}" -gt 0 ] 2>/dev/null; then
  echo "Keeping the newest ${BACKUP_KEEP} config backups in: ${BACKUP_ROOT}"
  find "${BACKUP_ROOT}" -maxdepth 1 -mindepth 1 -type d -name 'config-*' \
    | sort -r \
    | tail -n +"$((BACKUP_KEEP + 1))" \
    | xargs -r rm -rf
fi

echo "Update complete."
echo "Backup: ${BACKUP_DIR}"
echo "Restore example:"
echo "  rsync -a --delete '${BACKUP_DIR}/' '${CONFIG_DIR}/'"
echo "Next:"
echo "  sudo systemctl restart moonraker"
echo "  sudo systemctl restart klipper"

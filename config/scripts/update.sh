#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HOME}/printer_data/config"
BACKUP_DIR="${HOME}/printer_data/config.update-backup-$(date +%Y%m%d-%H%M%S)"

if [ ! -d "${CONFIG_DIR}/.git" ]; then
  echo "ERROR: ${CONFIG_DIR} is not a git repository."
  echo "Use scripts/install.sh for the first install."
  exit 1
fi

echo "Backing up current config to: ${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"
rsync -a --exclude ".git" "${CONFIG_DIR}/" "${BACKUP_DIR}/"

echo "Pulling latest config."
git -C "${CONFIG_DIR}" pull --ff-only

echo "Update complete."
echo "Backup: ${BACKUP_DIR}"
echo "Next:"
echo "  sudo systemctl restart moonraker"
echo "  sudo systemctl restart klipper"


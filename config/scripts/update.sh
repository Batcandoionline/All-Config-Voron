#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HOME}/printer_data/config"
REPO_URL="git@github.com:Batcandoionline/All-Config-Voron.git"
REPO_DIR="${HOME}/All-Config-Voron"
BACKUP_DIR="${HOME}/printer_data/config.update-backup-$(date +%Y%m%d-%H%M%S)"

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

echo "Update complete."
echo "Backup: ${BACKUP_DIR}"
echo "Next:"
echo "  sudo systemctl restart moonraker"
echo "  sudo systemctl restart klipper"

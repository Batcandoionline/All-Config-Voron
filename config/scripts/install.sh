#!/usr/bin/env bash
set -euo pipefail

REPO_URL="git@github.com:Batcandoionline/All-Config-Voron.git"
CONFIG_DIR="${HOME}/printer_data/config"
BACKUP_DIR="${HOME}/printer_data/config.backup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_CONFIG_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Installing All-Config-Voron/config"
echo "Target: ${CONFIG_DIR}"

if [ -d "${CONFIG_DIR}" ]; then
  echo "Backing up existing config to: ${BACKUP_DIR}"
  mv "${CONFIG_DIR}" "${BACKUP_DIR}"
fi

echo "Installing config files from: ${SOURCE_CONFIG_DIR}"
mkdir -p "${CONFIG_DIR}"
rsync -a --exclude "Nhat-ky-chinh-sua/" "${SOURCE_CONFIG_DIR}/" "${CONFIG_DIR}/"

echo "Install complete."
echo "Source repository: ${REPO_URL}"
echo "Backup: ${BACKUP_DIR}"
echo "Next:"
echo "  sudo systemctl restart moonraker"
echo "  sudo systemctl restart klipper"

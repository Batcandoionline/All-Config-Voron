#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Batcandoionline/Stealth-changer-config.git"
CONFIG_DIR="${HOME}/printer_data/config"
BACKUP_DIR="${HOME}/printer_data/config.backup-$(date +%Y%m%d-%H%M%S)"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

echo "Installing Stealth-changer-config"
echo "Target: ${CONFIG_DIR}"

if [ -d "${CONFIG_DIR}/.git" ]; then
  echo "Existing git-managed config found. Pulling latest changes."
  git -C "${CONFIG_DIR}" pull --ff-only
  echo "Done."
  exit 0
fi

if [ -d "${CONFIG_DIR}" ]; then
  echo "Backing up existing config to: ${BACKUP_DIR}"
  mv "${CONFIG_DIR}" "${BACKUP_DIR}"
fi

echo "Cloning repository."
git clone "${REPO_URL}" "${CONFIG_DIR}"

echo "Install complete."
echo "Backup: ${BACKUP_DIR}"
echo "Next:"
echo "  sudo systemctl restart moonraker"
echo "  sudo systemctl restart klipper"

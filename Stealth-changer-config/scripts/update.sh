#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HOME}/printer_data/config"
BACKUP_DIR="${HOME}/printer_data/config.update-backup-$(date +%Y%m%d-%H%M%S)"
TMP_DIR="$(mktemp -d)"
MOONRAKER_CONF_BACKUP="${TMP_DIR}/moonraker.conf"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

if [ ! -d "${CONFIG_DIR}/.git" ]; then
  echo "ERROR: ${CONFIG_DIR} is not a git repository."
  echo "Use scripts/install.sh for the first install."
  exit 1
fi

echo "Backing up current config to: ${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"
rsync -a --exclude ".git" "${CONFIG_DIR}/" "${BACKUP_DIR}/"

if [ -f "${CONFIG_DIR}/moonraker.conf" ]; then
  cp "${CONFIG_DIR}/moonraker.conf" "${MOONRAKER_CONF_BACKUP}"
  if git -C "${CONFIG_DIR}" ls-files --error-unmatch moonraker.conf >/dev/null 2>&1; then
    git -C "${CONFIG_DIR}" checkout -- moonraker.conf
  fi
fi

echo "Pulling latest config."
git -C "${CONFIG_DIR}" pull --ff-only

if [ -f "${MOONRAKER_CONF_BACKUP}" ]; then
  echo "Restoring machine-local moonraker.conf."
  cp "${MOONRAKER_CONF_BACKUP}" "${CONFIG_DIR}/moonraker.conf"
fi

echo "Update complete."
echo "Backup: ${BACKUP_DIR}"
echo "Next:"
echo "  sudo systemctl restart moonraker"
echo "  sudo systemctl restart klipper"

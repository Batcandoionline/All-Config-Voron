#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Batcandoionline/Stealth-changer-config.git"
CONFIG_DIR="${HOME}/printer_data/config"
BACKUP_DIR="${HOME}/printer_data/config.backup-$(date +%Y%m%d-%H%M%S)"
TMP_DIR="$(mktemp -d)"
MOONRAKER_CONF_BACKUP="${TMP_DIR}/moonraker.conf"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

echo "Installing Stealth-changer-config"
echo "Target: ${CONFIG_DIR}"

if [ -d "${CONFIG_DIR}/.git" ]; then
  echo "Existing git-managed config found. Pulling latest changes."
  if [ -f "${CONFIG_DIR}/moonraker.conf" ]; then
    cp "${CONFIG_DIR}/moonraker.conf" "${MOONRAKER_CONF_BACKUP}"
    if git -C "${CONFIG_DIR}" ls-files --error-unmatch moonraker.conf >/dev/null 2>&1; then
      git -C "${CONFIG_DIR}" checkout -- moonraker.conf
    fi
  fi
  git -C "${CONFIG_DIR}" pull --ff-only
  if [ -f "${MOONRAKER_CONF_BACKUP}" ]; then
    cp "${MOONRAKER_CONF_BACKUP}" "${CONFIG_DIR}/moonraker.conf"
  fi
  echo "Done."
  exit 0
fi

if [ -d "${CONFIG_DIR}" ]; then
  echo "Backing up existing config to: ${BACKUP_DIR}"
  mv "${CONFIG_DIR}" "${BACKUP_DIR}"
fi

echo "Cloning repository."
git clone "${REPO_URL}" "${CONFIG_DIR}"

if [ -f "${BACKUP_DIR}/moonraker.conf" ]; then
  echo "Restoring machine-local moonraker.conf from backup."
  cp "${BACKUP_DIR}/moonraker.conf" "${CONFIG_DIR}/moonraker.conf"
fi

echo "Install complete."
echo "Backup: ${BACKUP_DIR}"
echo "Next:"
echo "  sudo systemctl restart moonraker"
echo "  sudo systemctl restart klipper"

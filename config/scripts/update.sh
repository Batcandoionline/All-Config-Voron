#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HOME}/printer_data/config"
ARCHIVE_URL="${ARCHIVE_URL:-https://github.com/IDcrazy123/All-Config-Voron/archive/refs/heads/main.tar.gz}"
TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/all-config-voron.XXXXXX")"
ARCHIVE_FILE="${TEMP_ROOT}/source.tar.gz"
SOURCE_ROOT="${TEMP_ROOT}/source"

cleanup() {
  rm -rf -- "${TEMP_ROOT}"
}
trap cleanup EXIT HUP INT TERM

# Download a transient source archive. No persistent repository clone is kept
# on the Pi; install.sh performs the full backup and protected rsync.
mkdir -p "${SOURCE_ROOT}"
if command -v curl >/dev/null 2>&1; then
  curl --fail --location --silent --show-error "${ARCHIVE_URL}" --output "${ARCHIVE_FILE}"
elif command -v wget >/dev/null 2>&1; then
  wget --quiet "${ARCHIVE_URL}" --output-document="${ARCHIVE_FILE}"
else
  echo "ERROR: curl or wget is required." >&2
  exit 1
fi

tar -xzf "${ARCHIVE_FILE}" --strip-components=1 -C "${SOURCE_ROOT}"
if [[ ! -f "${SOURCE_ROOT}/config/printer.cfg" ]]; then
  echo "ERROR: downloaded archive does not contain config/printer.cfg" >&2
  exit 1
fi

bash "${SOURCE_ROOT}/config/scripts/install.sh"
echo "Update source was downloaded to a temporary directory and removed; no repository clone remains on the Pi."

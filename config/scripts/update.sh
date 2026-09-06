#!/usr/bin/env bash
set -euo pipefail

ARCHIVE_URL="${ARCHIVE_URL:-https://github.com/IDcrazy123/All-Config-Voron/archive/refs/heads/main.tar.gz}"
TEMP_PARENT="${TMPDIR:-/tmp}"
TEMP_PARENT="${TEMP_PARENT%/}"
TEMP_ROOT="$(mktemp -d "${TEMP_PARENT}/all-config-voron.XXXXXX")"
ARCHIVE_FILE="${TEMP_ROOT}/source.tar.gz"
SOURCE_ROOT="${TEMP_ROOT}/source"

cleanup() {
  case "${TEMP_ROOT}" in
    "${TEMP_PARENT}"/all-config-voron.*) rm -rf -- "${TEMP_ROOT}" ;;
    *) echo "WARNING: refusing unexpected temporary path: ${TEMP_ROOT}" >&2 ;;
  esac
}
trap cleanup EXIT HUP INT TERM

# Download a transient archive. No persistent Git checkout is created on the
# Pi; install.sh performs the backup-first, protected deployment.
mkdir -p "${SOURCE_ROOT}"
if command -v curl >/dev/null 2>&1; then
  curl --fail --location --silent --show-error \
    "${ARCHIVE_URL}" --output "${ARCHIVE_FILE}"
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
echo "Update complete; the temporary source archive was removed and no repository clone remains on the Pi."

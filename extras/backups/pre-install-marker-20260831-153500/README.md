# Backup before kTAMV install preflight marker update

- Date: 2026-08-31
- Source: `config/scripts/install.sh`
- SHA256 before edit: `9ffd54fb0eb1c9d1375ce1259df9970499974dd859a06e7da4acb66e9007c3cc`
- Reason: preserve the installer before adding a preflight check for the
  duplicate-center calibration threshold marker.
- The live patch/config copy was separately backed up on the printer at
  `/home/voron/printer_data/config_backups/pre-independent-cycles-20260831-153700/`.

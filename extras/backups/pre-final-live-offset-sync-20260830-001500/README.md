# Pre-final live Z-offset sync backup

- Captured: 2026-08-30 before correcting the active printer configuration.
- Source: `voron@192.168.1.43:/home/voron/printer_data/config/printer.cfg`.
- SHA-256 of the captured live file: `B60946F78E8C25A69DEBB45B1D572219B615E99F424DA11E2F9B6104D75D318B`.
- Remote copy: `/home/voron/printer_data/config_backups/tool-vision/pre-final-live-offset-sync-20260830-001500/printer.cfg`.
- The captured file contained T1 `0.228` and T4 `-0.014`; these were corrected to the operator-selected print-tested values T1 `0.2464` and T4 `0.1028`. T2/T3 were already `-0.2688`/`-0.1896`.
- The candidate is derived from the live file and changes only the four generated `gcode_z_offset` values; unrelated live settings are preserved.

# Backup before applying the pre-ToolVision Z-offset set

- Captured: 2026-08-30 before applying the temporary print-test values.
- Source: `voron@192.168.1.43:/home/voron/printer_data/config/printer.cfg`.
- SHA-256 of the captured live file: `A17B7CCC07FB90934FAFA8A44D45B2E749D8F3DDC21C70B5CEF6325441BAC765`.
- Remote copy: `/home/voron/printer_data/config_backups/tool-vision/pre-apply-pre-toolvision-offsets-20260830-003000/printer.cfg`.
- Applied only the generated Z-offset lines, preserving all other live settings:
  - T1 `+0.2464` -> `+0.228`
  - T2 `-0.2688` -> `-0.295`
  - T3 `-0.1896` -> `-0.268`
  - T4 `+0.1028` -> `-0.014`
- The repository production baseline was intentionally not changed; this is a
  temporary live print-test configuration pending print results.
- `FIRMWARE_RESTART` completed successfully. Klipper returned ready, the
  printer remained standby, ToolVision was idle and all heater targets were 0 C.

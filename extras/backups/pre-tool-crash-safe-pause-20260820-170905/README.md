# Pre-change backup: tool_crash safe pause

- Created: 2026-08-20 17:09:05 (Asia/Saigon)
- Purpose: preserve the production tool_crash configuration before replacing
  Klipper shutdown behavior with a no-XYZ-movement pause handler.
- Source files:
  - `config/Printer-Setup/tool_crash_cartographer.cfg`
  - `config/Printer-Setup/crash_detection_override.cfg`
- Restore the files from `Printer-Setup/` to their original paths, then run a
  Klipper `RESTART`, only while the printer is idle.

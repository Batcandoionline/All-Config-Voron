# Backup record

- **Date:** 2026-08-20 21:07:54
- **Task:** Cut over the calibration backend from Axiscope to Tool Vision.
- **PC and live printer files:**
  - `printer.cfg`
  - `Printer-Setup/calibration-probe.cfg`
  - `Tool-Vision/tool_vision.cfg`
  - `toolchanger/toolchanger-config.cfg`
- **System state:**
  - `system/axiscope.service`
  - `system/pre-cutover-state.txt`
- **Tool Vision source before runtime fixes:**
  - `tool-vision-source/server/tool-vision.service.in`
  - `tool-vision-source/klippy/extras/tool_vision.py`
  - `tool-vision-source/tests/test_contracts.py`
  - `tool-vision-source/tests/test_klipper_logic.py`
- **Verified PC/live SHA-256:**
  - `printer.cfg`:
    `BA587918927B06A2F31CE4E4CC8D7B93A21114B20932FF9D6296DE3840BADBD5`
  - `calibration-probe.cfg`:
    `C42EF48A9484110B7116E5684A5D5582C01E568290F529BB420E3CD3BADA10A6`
  - `tool_vision.cfg`:
    `A4B4649A5D25642256F36C90EB4B6002A2FBD6BB91DCA8D41F51E1D4BFF4E0E8`
  - `toolchanger-config.cfg`:
    `CDD9DE4AB0A71CF13A3B09BBF5D8ADF0EECE6DC90955C83ED8261786ACFA58FD`
- **Printer backup:**
  `/home/voron/printer_data/config/.codex-backups/pre-toolvision-cutover-20260820-210754/`
- **Related journal:**
  `extras/Nhat-ky-chinh-sua/2026-08-20-session-updates.md`

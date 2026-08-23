# Backup Record

- **Date:** 2026-08-23 21:15:30
- **Task:** Prepare the Z-offset backend change from Axiscope PF2 to the
  ToolVision `main` canary.
- **Backed-up files:**
  - `config/printer.cfg` — before adding the ToolVision include.
  - `config/moonraker.conf` — before adding the Moonraker update manager.
  - `config/Printer-Setup/calibration-probe.cfg` — before disabling Axiscope
    and updating backend status macros.
  - `config/scripts/install.sh` — before replacing the Axiscope preflight with
    the ToolVision runtime preflight.
- **Planned new file:** `config/tool_vision.cfg`
- **Related log:** `extras/Nhat-ky-chinh-sua/2026-08-23-session-updates.md`

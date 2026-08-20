# Backup record

- **Date:** 2026-08-20 15:41:54
- **Task:** Rebuild Tool Vision as a safe, portable XYZ measurement module.
- **Files backed up:**
  - `tool_vision.cfg` — legacy module configuration
  - `klippy/extras/tool_vision.py` — legacy Klipper extension
  - `server/vision_server.py` — legacy HTTP service
  - `server/vision_dm.py` — legacy detection module
  - `server/vision_io.py` — legacy camera I/O
  - `server/tool_vision.service` — legacy systemd unit
  - `install.sh` — legacy installer
- **Related log:** `extras/Nhat-ky-chinh-sua/2026-08-20-session-updates.md`

The previous user-facing README is intentionally not duplicated: this file is
the required backup manifest. The implementation files above are byte-for-byte
copies from immediately before the rebuild.

# Bản ghi sao lưu

- **Ngày:** 2026-08-22 17:45:12
- **Tác vụ:** Sửa các lỗi logic đã xác nhận trong Printer-Setup và tool crash detector.
- **File đã sao lưu:**
  - `print-macros.cfg` — liên động dryer/print, thứ tự dock và vòng đời bed fan.
  - `fans-leds.cfg` — khôi phục crash detector và cleanup khi cancel.
  - `nozzle-clean.cfg` — xác thực tool thực sự đang gắn.
  - `input-shaper.cfg` — đồng bộ fallback T0.
  - `calibration-probe.cfg` — loại bỏ trạng thái ToolVision hard-code đã cũ.
  - `tool_crash.py` — lọc cạnh sensor qua trạng thái active tool/watchdog.
- **Nhật ký liên quan:** `extras/Nhat-ky-chinh-sua/2026-08-22-session-updates.md`
- **Backup máy thật:** `/home/voron/printer_data/config_backups/pre-fix-printer-setup-logic-20260822-174512/`

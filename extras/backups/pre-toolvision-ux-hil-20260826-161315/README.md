# Bản ghi sao lưu

- **Ngày:** 2026-08-26 16:13:15 +07:00
- **Tác vụ:** Cập nhật ToolVision lên UX hợp nhất XY/Z/XYZ và chạy HIL 5 lượt switch + 5 lượt Cartographer Touch.
- **Máy in:** `192.168.1.43`, trạng thái trước sao lưu `standby`, Klipper `ready`, heater targets bằng 0.
- **ToolVision trước cập nhật:** commit `204ae4cecfec90c58cd4a84b85f4b378c1264062`, runtime `3.4.0-rc2`.
- **File đã sao lưu:**
  - `tool-vision.cfg` — cấu hình và action-prompt production trước khi đồng bộ template mới.
  - `Generated-Data-ToolVision/` — state, latest result, schema backups và history HIL hiện có.
- **Bản sao trên máy in:** `/home/voron/printer_data/config_backups/pre-toolvision-ux-hil-20260826-161315/`.
- **Nhật ký liên quan:** `extras/Nhat-ky-chinh-sua/2026-08-26-session-updates.md`.

Không dùng dữ liệu trong thư mục này làm cấu hình hoạt động. Khi rollback, khôi
phục đúng file cần thiết rồi kiểm tra hash và `FIRMWARE_RESTART` theo runbook.

# Bản ghi sao lưu

- **Ngày:** 2026-08-07 16:11:00
- **Tác vụ:** Đồng bộ Z-offset cho toàn bộ 5 toolhead (T0 đến T4). Đặt Cartographer Touch `z_offset = -0.03` để T0 đạt lớp in hoàn hảo, đồng thời hạ `gcode_z_offset` của T1–T4 thêm -0.02mm để đồng bộ chính xác theo mặt phẳng Z reference mới của T0.
- **File đã sao lưu:**
  - `printer.cfg` — Sao lưu trước khi cập nhật `touch_model z_offset` (-0.03) và `gcode_z_offset` cho T1-T4.
- **Nhật ký liên quan:** `extras/Nhat-ky-chinh-sua/2026-08-07-session-updates.md`

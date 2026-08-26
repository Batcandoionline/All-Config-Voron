# Bản ghi sao lưu

- **Ngày:** 2026-08-26 18:48:26 +07:00
- **Tác vụ:** Lưu bằng chứng và cấu hình live trước khi xem xét tiếp tục HIL Z sau lỗi driver X.
- **File đã sao lưu:**
  - `printer.cfg` — cấu hình live tại thời điểm sự cố.
  - `tool-vision.cfg` — cấu hình ToolVision live tại thời điểm sự cố.
  - `20260826-114524-081-z-switch-01.json` — session INVALID ghi lỗi `stepper_x ShortToSupply_A` trong full `G28`.
- **Phạm vi:** Không có offset nào được đo hoặc apply; chuỗi 10 attempt dừng ngay ở attempt đầu.
- **Nhật ký liên quan:** `extras/Nhat-ky-chinh-sua/2026-08-26-session-updates.md`, mục 10.

Không dùng trực tiếp các file trong thư mục này làm cấu hình
hoạt động. Kiểm tra phần cứng stepper X và power-cycle trước khi
thử lại.

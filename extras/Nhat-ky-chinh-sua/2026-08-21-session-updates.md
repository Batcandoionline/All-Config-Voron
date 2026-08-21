# Nhật ký — 2026-08-21

## 1. Gộp các preset sấy nhựa thành một hộp chọn trên Mainsail

### Mục tiêu

Làm gọn bảng macro trên Mainsail bằng cách thay bảy nút `DRY_PLA`, `DRY_TPU`, `DRY_PETG`, `DRY_ABS`, `DRY_ASA`, `DRY_NYLON`, `DRY_PC` bằng một nút `START_DRYER` có hộp chọn vật liệu, đồng thời vẫn hỗ trợ gọi trực tiếp bằng một lệnh có tham số.

### File đã sửa đổi

- `config/Printer-Setup/print-macros.cfg` — thêm hộp chọn vật liệu, gom bảng preset vào macro nội bộ và xóa bảy macro preset công khai.
- `README.md` — cập nhật cách dùng hệ thống sấy và bảng tham số vật liệu.
- `config/README.md` — cập nhật mô tả `print-macros.cfg` theo giao diện một hộp chọn.

### Sao lưu

- [print-macros.cfg (Backup)](<file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-consolidate-dryer-presets-20260821-215854/print-macros.cfg>)
- [README.md.master (Backup)](<file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-consolidate-dryer-presets-20260821-215854/README.md.master>)
- [config-README.md (Backup)](<file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-consolidate-dryer-presets-20260821-215854/config-README.md>)

### Chi tiết thay đổi

- `START_DRYER` không tham số nay mở Mainsail prompt để chọn `PLA`, `TPU`, `PETG`, `ABS`, `ASA`, `NYLON/PA` hoặc `PC`.
- Hỗ trợ gọi trực tiếp, ví dụ `START_DRYER MATERIAL=PETG`.
- Giữ tương thích với chế độ tùy chỉnh: các tham số `BED`, `CHAMBER`, `TIME`, `TIME_HOURS`, `FAN`, `PARK`, `TARGET_HUMIDITY` vẫn có thể ghi đè preset.
- Chuyển bộ điều khiển chính thành macro ẩn `_START_DRYER`; thêm `_DRYER_SELECT` và `_DRYER_PROMPT_CLOSE` để phục vụ hộp thoại Mainsail.
- Xóa bảy section macro công khai `DRY_*`. Mainsail chỉ còn hiển thị ba điều khiển sấy: `START_DRYER`, `STOP_DRYER`, `DRYER_STATUS`.
- Bổ sung tên vật liệu đang sấy vào `DRYER_STATUS` và thông báo bắt đầu chu trình.
- Giữ nguyên toàn bộ giá trị đã hiệu chỉnh:
  - PLA: Bed 50°C, Chamber 40°C, 240 phút, Fan 40%.
  - TPU: Bed 60°C, Chamber 45°C, 300 phút, Fan 40%.
  - PETG: Bed 70°C, Chamber 55°C, 240 phút, Fan 50%.
  - ABS/ASA: Bed 90°C, Chamber 65°C, 240 phút, Fan 60%.
  - Nylon/PA: Bed 100°C, Chamber 70°C, 360 phút, Fan 70%.
  - PC: Bed 105°C, Chamber 75°C, 360 phút, Fan 70%.

### Lý do

Bảy macro preset riêng làm bảng điều khiển Mainsail dài và khó quan sát. Hộp chọn tập trung giữ đủ chức năng nhưng làm giao diện gọn hơn, đồng thời lệnh `MATERIAL=` giúp sử dụng từ Console hoặc quy trình tự động rõ ràng hơn.

### Kiểm tra

- Đọc toàn bộ 163 file Markdown trong workspace để nắm quy tắc, cấu trúc, lịch sử và quyết định của dự án: đạt.
- Phân tích cấu trúc CFG nghiêm ngặt: đạt, 19 section hợp lệ.
- Phân tích 16 template bằng cú pháp Jinja delimiter của Klipper: đạt.
- Render và đối chiếu 7/7 preset vật liệu: đạt, mọi nhiệt độ/thời gian/quạt khớp giá trị cũ.
- Render hộp chọn và đường chuyển tiếp `START_DRYER MATERIAL=...`: đạt.
- Kiểm tra macro sấy công khai: đạt, chỉ còn `START_DRYER`, `STOP_DRYER`, `DRYER_STATUS`.
- So sánh khối `Multi-Zone Adaptive Regulation` với bản sao lưu: đạt, nội dung không thay đổi.
- `git diff --check`: đạt.
- Khởi động lại Klipper: chưa thực hiện trên máy in thật.
- Chạy thử heater/quạt thực tế: chưa thực hiện; cần xác nhận khi máy in đang rảnh và không có vật cản.

### Kết quả

Cấu hình sấy đã được gom thành một luồng chọn vật liệu duy nhất mà không thay đổi các preset và thuật toán sấy đã hiệu chỉnh.

### Vấn đề còn lại

- Sau khi đồng bộ cấu hình lên máy in, chạy `FIRMWARE_RESTART`, bấm `START_DRYER` để kiểm tra hộp chọn trên Mainsail, sau đó có thể chọn một vật liệu và dùng `STOP_DRYER` ngay để xác nhận luồng điều khiển trước khi chạy đủ chu trình.

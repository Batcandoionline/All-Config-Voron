# Nhật ký chỉnh sửa - 2026-07-03

## 1. Tinh chỉnh Z-offset cho đầu in T2 dựa trên thực tế

### Mục tiêu
Cập nhật giá trị gcode_z_offset cho đầu in T2 để có lớp in đầu tiên bám dính đẹp sau khi người dùng điều chỉnh trực tiếp qua màn hình 5 inch.

### File đã sửa đổi
- [printer.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/printer.cfg) — Cập nhật gcode_z_offset của [tool T2]

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-t2-z-offset-tune-20260703-203957/printer.cfg)

### Chi tiết thay đổi
- Đầu in `[tool T2]`: `gcode_z_offset`: `-0.21000000002525155` → `-0.28500000002525155` (Hạ thêm `0.075mm` theo Lựa chọn 1 được người dùng xác nhận)

### Lý do
Khi in thực tế, lớp đầu tiên của đầu in T2 chưa đẹp do đầu phun hơi cao so với bàn in. Việc hạ thêm 0.075mm (điều chỉnh qua màn hình 5inch/KlipperScreen) giúp tối ưu hóa khoảng cách từ đầu phun đến bàn in, tăng cường độ bám dính của lớp đầu tiên.

### Kiểm tra
- Kiểm tra cú pháp: Đạt
- Khởi động lại Klipper: Người dùng sẽ thực hiện khởi động lại máy in để áp dụng
- Thử in: Chờ người dùng thực hiện chạy kiểm tra lớp in đầu tiên thực tế

### Kết quả
Đang chờ xác nhận từ việc in thực tế của người dùng sau khi áp dụng cấu hình mới.

### Vấn đề còn lại
Không có.

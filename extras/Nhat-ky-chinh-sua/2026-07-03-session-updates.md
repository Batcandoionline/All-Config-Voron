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

---

## 2. Cập nhật tài liệu README.md dự án

### Mục tiêu
Cập nhật file `README.md` chính của dự án để đảm bảo thông tin chính xác, ngắn gọn, súc tích và dễ đọc cho người phát triển hoặc AI assistant khi bắt đầu tiếp cận dự án.

### File đã sửa đổi
- [README.md](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/README.md) — Tái cấu trúc, tối ưu nội dung

### Chi tiết thay đổi
- Chuyển danh sách phần cứng thành dạng bảng biểu rõ ràng.
- Làm rõ vai trò của Cartographer V3 (đo bàn & homing Z chính) và SexBolt/SexBall (thiết bị hiệu chuẩn Z-offset, chỉ gắn tạm khi calib).
- Rút gọn mô tả thư mục.
- Làm sạch các lệnh SSH để cài đặt và cập nhật.
- Định dạng lại quy trình hiệu chuẩn SexBolt bằng mã G-code trực quan.
- Thêm ghi chú hướng dẫn chung cho maintainer/AI (sao lưu, quy tắc Git, file quy tắc).

### Lý do
Tài liệu README cũ trình bày dài dòng, chưa tối ưu định dạng và có một số thông số phần cứng thiếu tính nhất quán (ví dụ thông tin MCU). Việc tinh chỉnh lại giúp tài liệu trở nên chuyên nghiệp, trực quan và dễ tiếp cận hơn.

### Kiểm tra
- Định dạng Markdown: Đạt chuẩn GitHub Flavored Markdown (GFM).

### Kết quả
Tài liệu README mới ngắn gọn và súc tích hơn, hiển thị đẹp mắt trên giao diện GitHub.


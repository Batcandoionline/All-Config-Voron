# Nhật ký — 2026-07-25

## 1. Cấu hình Axiscope & Tắt xung đột [tools_calibrate]

### Mục tiêu
Cấu hình Klipper cho phép cài đặt và sử dụng Axiscope chính chủ (https://github.com/nic335/Axiscope) để căn chỉnh XY offset cho 5 đầu in (T0-T4). Tránh xung đột module `probe_multi_axis` với `[tools_calibrate]` (Sexbolt).

### File đã sửa đổi
- `config/toolchanger/toolchanger-config.cfg` — Comment out section `[tools_calibrate]` để tránh xung đột `probe_multi_axis`.
- `config/Printer-Setup/calibration.cfg` — Bổ sung section `[axiscope]` chính chủ.

### Sao lưu
- [toolchanger-config.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-setup-20260725-193800/toolchanger-config.cfg)
- [calibration.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-setup-20260725-193800/calibration.cfg)

### Chi tiết thay đổi
- Comment out section `[tools_calibrate]` trong `toolchanger-config.cfg`.
- Thêm `[axiscope]` với `move_speed: 200` và `config_file_path: ~/printer_data/config/printer.cfg` vào `calibration.cfg`.

### Lý do
Axiscope sử dụng module `probe_multi_axis`. Nếu giữ nguyên `[tools_calibrate]`, Klipper sẽ gặp lỗi `Duplicate chip name probe_multi_axis` khi khởi động.

### Kiểm tra
- Đã chuẩn bị cấu hình sạch sẵn sàng cho việc cài đặt script `bash install.sh` của Axiscope trên Pi.

### Kết quả
Cấu hình Klipper đã sẵn sàng cho Axiscope.

## 2. Cập nhật XY Offset chính xác cho T1-T4 từ đo đạc Camera Axiscope

### Mục tiêu
Khắc phục sự cố viền ô số 4 (T3) và ô số 3 (T2) bị đè lấn lên nhau trên bản in thử nghiệm do đo đạc SexBolt cũ bị lệch trục Y.

### File đã sửa đổi
- `config/printer.cfg` — Cập nhật `gcode_x_offset` và `gcode_y_offset` của `[tool T1]` đến `[tool T4]` theo giá trị đo trực quan bằng Camera Axiscope.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-update-axiscope-offsets-20260725-201100/printer.cfg)

### Chi tiết thay đổi
- `[tool T1]`: `gcode_x_offset: -0.243`, `gcode_y_offset: -0.252`
- `[tool T2]`: `gcode_x_offset: 0.746`, `gcode_y_offset: 0.086`
- `[tool T3]`: `gcode_x_offset: 0.304`, `gcode_y_offset: 0.449` (Tăng Y từ 0.109 -> 0.449 mm để triệt tiêu việc đè viền)
- `[tool T4]`: `gcode_x_offset: 0.041`, `gcode_y_offset: 0.352`

### Lý do
Do SexBolt bị sai số Y cho T3 (+0.340mm), làm cho T3 bị in thấp hơn vị trí thực tế và đè lên T2. Đo đạc Camera Axiscope phản ánh chính xác vị trí cơ học của từng đầu phun.

### Kết quả
Đã áp dụng các giá trị tối ưu mới nhất vào `printer.cfg`.


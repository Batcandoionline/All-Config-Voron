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

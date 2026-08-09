# Nhật ký — 2026-08-09

## 1. Cấu hình Axiscope Z-Offset Switch (Tọa độ X:68, Y:-10, Z:7)

### Mục tiêu
Cấu hình module `[axiscope]` và cập nhật tọa độ switch hiệu chuẩn Z-offset giữa các tool (T0-T4) tại vị trí X:68, Y:-10, Z:7.

### File đã sửa đổi
- `config/Printer-Setup/calibration.cfg` — Kích hoạt và cấu hình section `[axiscope]` với tọa độ công tắc (X:68, Y:-10, Z:7), pin `^PF4`, và macro gia nhiệt an toàn 150°C.
- `config/toolchanger/toolchanger-config.cfg` — Cập nhật tọa độ `_CALIBRATION_SWITCH` sang X:68, Y:-10, Z:15 và comment out `[tools_calibrate]` để tránh xung đột `probe_multi_axis`.

### Sao lưu
- [calibration.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-z-offset-switch-20260809-180500/calibration.cfg)
- [toolchanger-config.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-z-offset-switch-20260809-180500/toolchanger-config.cfg)

### Chi tiết thay đổi
- Section `[axiscope]`:
  - `pin: ^PF4`
  - `zswitch_x_pos: 68.0`
  - `zswitch_y_pos: -10.0`
  - `zswitch_z_pos: 7.0`
  - `lift_z: 2.0`
  - `move_speed: 100`
  - `z_move_speed: 5`
  - `start_gcode`: gia nhiệt tất cả tool lên 150°C trước khi probe để làm mềm nhựa đọng.
  - `finish_gcode`: tắt heater tất cả tool và chuyển về T0 sau khi hoàn tất.
- Macro `[gcode_macro _CALIBRATION_SWITCH]`:
  - `variable_x`: `257` → `68`
  - `variable_y`: `327` → `-10`
  - `variable_z`: `60` → `15` (chiều cao tiếp cận an toàn trên mặt switch Z:7)
- Section `[tools_calibrate]`: Commented out để tránh xung đột đăng ký `probe_multi_axis` với module Axiscope.

### Lý do
Chuyển sang phương pháp đo độ lệch Z bằng công tắc nhấn tích hợp Axiscope với vị trí công tắc cơ học mới tại X:68, Y:-10, Z:7.

### Kiểm tra
- Kiểm tra cú pháp Klipper: Đạt (cấu trúc section, tham số, gcode macro hợp lệ).
- Khởi động lại Klipper: Cần thực hiện sau khi cập nhật lên máy in Voron.

### Kết quả
Cấu hình đã sẵn sàng cho quy trình đo Z-Offset qua giao diện Axiscope.

### Vấn đề còn lại
1. Đồng bộ lên máy in qua `scripts/update.sh` hoặc copy config.
2. Kiểm tra thực tế trạng thái logic pin `^PF4` bằng tay trước khi chạy auto calibration.

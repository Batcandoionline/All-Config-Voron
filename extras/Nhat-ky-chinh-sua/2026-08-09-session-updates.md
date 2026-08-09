# Nhật ký — 2026-08-09

## 1. Cấu hình Axiscope Z-Offset Switch (Tọa độ X:68, Y:-10, Z:7)

### Mục tiêu
Cấu hình module `[axiscope]` và cập nhật tọa độ switch hiệu chuẩn Z-offset giữa các tool (T0-T4) tại vị trí X:68, Y:-10, Z:7.

### File đã sửa đổi
- `config/Printer-Setup/calibration.cfg` — Kích hoạt và cấu hình section `[axiscope]` với tọa độ công tắc (X:68, Y:-10, Z:7), pin switch, và macro gia nhiệt an toàn 150°C.
- `config/toolchanger/toolchanger-config.cfg` — Cập nhật tọa độ `_CALIBRATION_SWITCH` sang X:68, Y:-10, Z:15 và comment out `[tools_calibrate]` để tránh xung đột `probe_multi_axis`.

### Sao lưu
- [calibration.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-z-offset-switch-20260809-180500/calibration.cfg)
- [toolchanger-config.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-z-offset-switch-20260809-180500/toolchanger-config.cfg)

---

## 2. Đồng bộ cấu hình printer.cfg mới từ máy in

### Mục tiêu
Đồng bộ khối `SAVE_CONFIG` mới nhất từ máy in thực tế vào kho mã nguồn (chứa các hệ số Cartographer scan model, Cartographer touch threshold mới `1819`, reference_temperature `42.44`, PID calib, tool offsets).

### File đã sửa đổi
- `config/printer.cfg` — Cập nhật khối `SAVE_CONFIG` đồng bộ từ máy in.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-printer-cfg-20260809-180830/printer.cfg)

---

## 3. Cập nhật chân tín hiệu Z-Offset Switch sang PF2 (GND + PF2)

### Mục tiêu
Người dùng đã đấu nối dây công tắc microswitch Z-offset vào cổng PF2 và GND (G) trên board Manta M8P V2 thay vì PF4. Cập nhật pin cấu hình trong Klipper thành `^PF2`.

### File đã sửa đổi
- `config/Printer-Setup/calibration.cfg` — Đổi `pin: ^PF4` thành `pin: ^PF2` trong section `[axiscope]`.
- `config/toolchanger/toolchanger-config.cfg` — Đổi chú thích pin trong `_CALIBRATION_SWITCH` và `[tools_calibrate]` thành `PF2`.
- `config/README.md` — Cập nhật bảng pinout phần cứng: Z-Offset sensor kết nối Manta M8P `PF2`.

### Sao lưu
- [calibration.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-switch-pin-pf2-20260809-181000/calibration.cfg)
- [toolchanger-config.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-switch-pin-pf2-20260809-181000/toolchanger-config.cfg)

### Chi tiết thay đổi
- Section `[axiscope]`:
  - `pin: ^PF2` (Kích hoạt internal pull-up trên chân PF2 của Manta M8P V2).
  - Tọa độ: X:68.0, Y:-10.0, Z:7.0.

### Lý do
Thực tế phần cứng được cắm vào chân PF2 và G (GND) trên mainboard Manta M8P V2. Chân PF2 hoàn toàn trống và không bị trùng với bất kỳ stepper endstop nào khác.

### Kiểm tra
- Cú pháp Klipper hợp lệ.
- Pin `PF2` không bị trùng lặp trong toàn bộ cây thư mục `config/`.

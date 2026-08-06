# Nhật ký — 2026-08-06

## 1. Điều chỉnh Z-Offset thực tế cho T0–T4 do thay đổi phần cứng

### Mục tiêu
Cập nhật giá trị Z-offset cho các tool T1–T4 và Z-offset của Cartographer Touch (T0) theo kết quả đo đạc và thử nghiệm in thực tế sau khi thay đổi phần cứng.

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — Cập nhật section `#*# [cartographer touch_model default]` và `#*# [tool T1]` đến `#*# [tool T4]`

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-z-offset-hardware-adjust-20260806-202200/printer.cfg)

### Chi tiết thay đổi
- **T0 (Cartographer Touch `z_offset`):** `-0.05` → `-0.03` (+0.02mm)
- **T1 (`gcode_z_offset`):** `0.208` → `0.328` (+0.12mm)
- **T2 (`gcode_z_offset`):** `-0.285` → `-0.175` (+0.11mm)
- **T3 (`gcode_z_offset`):** `-0.258` → `-0.178` (+0.08mm)
- **T4 (`gcode_z_offset`):** `0.066` → `0.086` (+0.02mm)

### Lý do
Do chuyển đổi phần cứng và nâng Z thực tế khi in:
- T0 cần nâng Z thêm 0.02mm sau khi cartographer-touch-home để đạt chất lượng dính lớp đầu tối ưu.
- T1–T4 cần điều chỉnh Z bù chênh lệch độ cao thực tế của các nozzle so với reference tool.

### Kiểm tra
- Kiểm tra cú pháp Klipper: Đạt

### Kết quả
Đã áp dụng toàn bộ thông số Z-offset mới vào `printer.cfg`.

### Vấn đề còn lại
Cần người dùng chạy `FIRMWARE_RESTART` trên Klipper và in thử nghiệm để xác nhận lớp đầu tiên.

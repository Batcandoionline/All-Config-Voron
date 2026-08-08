# Nhật ký — 2026-08-08

## 1. Cập nhật dữ liệu hiệu chuẩn Cartographer Touch và Offset các Toolhead

### Mục tiêu
Cập nhật lại các thông số sau đợt hiệu chuẩn mới của người dùng:
1. Ngưỡng chạm Cartographer Touch (`threshold`) trong section `[cartographer touch_model default]`.
2. Giá trị bù trừ `gcode_z_offset` của các cụm đầu in T1, T2, T3, T4.
3. Sửa lỗi chính tả 2 giá trị trong ma trận `[bed_mesh default]` points.

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — Cập nhật `threshold`, `gcode_z_offset` (T1–T4), và hiệu chỉnh số liệu bed mesh.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-touch-calib-and-tool-offsets-20260808-201700/README.md)

### Chi tiết thay đổi
- **Cartographer Touch Threshold:** `2594` → `1818`
- **T1 (`gcode_z_offset`):** `0.20799999999127493` → `0.328`
- **T2 (`gcode_z_offset`):** `-0.28500000002525155` → `-0.175`
- **T3 (`gcode_z_offset`):** `-0.2580000000428268` → `-0.178`
- **T4 (`gcode_z_offset`):** `0.065999999939054135` → `0.086`
- **Bed Mesh Points:** Sửa lỗi thiếu số 0 (`-0.94642` → `-0.094642`, `-0.96387` → `-0.096387`)

### Lý do
Người dùng đã hoàn thành chu trình hiệu chuẩn lại `CARTOGRAPHER_TOUCH_CALIBRATE` và đo lại Z-offset của các đầu in T1–T4.

### Kiểm tra
- Cú pháp Klipper: Đạt chuẩn.

### Kết quả
Đã đồng bộ toàn bộ thông số mới vào `printer.cfg`, tạo bản ghi sao lưu và cập nhật Git.

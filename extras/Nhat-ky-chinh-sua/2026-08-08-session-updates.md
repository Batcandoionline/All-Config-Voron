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

### 2. Đồng bộ kết quả hiệu chuẩn Cartographer Touch và Bed Mesh hoàn chỉnh

### Mục tiêu
Cập nhật các số liệu sau chuỗi đo kiểm tra đạt chuẩn độ chính xác cao:
1. `threshold = 1652` (chính xác với độ lệch chuẩn 0.002040 mm).
2. Toàn bộ ma trận `[bed_mesh default]` phân giải 55x55 điểm đo quét thực tế từ Cartographer v3.
3. Đồng bộ hóa toàn diện cấu hình sản xuất lên GitHub.

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — Cập nhật `threshold = 1652` và toàn bộ ma trận `[bed_mesh default]`.

### Sao lưu
- [printer.cfg (Backup 21:09)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-final-calib-update-20260808-210900/README.md)

### Kết quả đo kiểm chứng
- `CARTOGRAPHER_TOUCH_ACCURACY`: `stddev = 0.002040 mm`, `range = 0.006 mm`.
- `QUAD_GANTRY_LEVEL`: `Probed points range: 0.004979 mm` (đạt dung sai < 0.0075 mm).

## 3. Áp dụng điều chỉnh Z offset khi in thực tế cho T1–T3

### Mục tiêu
Đồng bộ vào cấu hình các điều chỉnh Z offset tương đối mà người dùng đã thực hiện trên KlipperScreen khi in thực tế qua màn hình HDMI.

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — cập nhật ba giá trị `gcode_z_offset` đã lưu trong `SAVE_CONFIG`.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-print-z-offset-adjustments-20260808-215317/printer.cfg)

### Chi tiết thay đổi
- **T1:** `0.328` + `(-0.100)` → `0.228`
- **T2:** `-0.175` + `(-0.120)` → `-0.295`
- **T3:** `-0.178` + `(-0.090)` → `-0.268`

### Lý do
Các mức điều chỉnh được xác định khi in thực tế bằng KlipperScreen; giá trị âm được cộng vào `gcode_z_offset` hiện có để hạ nozzle tương ứng.

### Kiểm tra
- Kiểm tra cú pháp tĩnh: đạt — ba block `SAVE_CONFIG` của T1, T2, T3 có đúng giá trị số mới; `git diff --check` không báo lỗi khoảng trắng.
- Khởi động lại Klipper: chưa thực hiện từ workspace.
- Thử in: cần xác nhận lớp đầu tiên sau khi Klipper nạp lại cấu hình.

### Kết quả
Ba giá trị Z offset đã được đồng bộ trong cấu hình nguồn.

### Vấn đề còn lại
Khởi động lại Klipper và kiểm tra lớp đầu tiên của T1, T2, T3 trước khi in dài.

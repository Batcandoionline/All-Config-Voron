# Nhật ký — 2026-08-07

## 1. Khôi phục Cartographer Touch Z-Offset về -0.05mm

### Mục tiêu
Khôi phục giá trị `z_offset` của Cartographer Touch trong section `[cartographer touch_model default]` từ `-0.03` về `-0.05` theo yêu cầu người dùng, do mức offset `-0.03` làm lệch mặt phẳng tham chiếu Z chuẩn của T0 và ảnh hưởng gián tiếp đến độ cao in thực tế của các đầu in T1, T2, T3, T4.

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — Thay đổi `z_offset` trong section `#*# [cartographer touch_model default]` từ `-0.03` về `-0.05`.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cartographer-touch-z-offset-adjust-20260807-160500/printer.cfg)

### Chi tiết thay đổi
- **T0 (Cartographer Touch `z_offset`):** `-0.03` → `-0.05` (-0.02mm)

### Lý do
Ở mức `z_offset = -0.03`, Z reference datum thiết lập khi home bằng Cartographer Touch bị nâng lên 0.02mm, kéo theo điểm Z0 của tất cả các tool T1–T4 bị lệch so với đo đạc tiêu chuẩn. Việc hạ `z_offset` về `-0.05` giúp chuẩn hóa lại mặt phẳng Z gốc cho T0 và khôi phục sự đồng bộ offset chính xác giữa T0 và T1–T4.

### Kiểm tra
- Kiểm tra cú pháp Klipper: Đạt (cú pháp hợp lệ, đúng quy chuẩn SAVE_CONFIG Klipper).

### Kết quả
Đã cập nhật thông số `z_offset = -0.05` trong `printer.cfg`.

### Vấn đề còn lại
Cần người dùng thực hiện `FIRMWARE_RESTART` trên Klipper / Mainsail và in thử nghiệm lại để kiểm tra lớp in đầu tiên trên các tool T0–T4.

---

## 2. Đồng bộ Z-Offset toàn bộ 5 Toolhead (T0–T4) theo lựa chọn người dùng

### Mục tiêu
Đồng bộ hóa giá trị Z-offset cho toàn bộ 5 toolhead (T0 đến T4) sao cho T0 in đẹp (đặt `touch_model z_offset = -0.03`) và T1–T4 đồng thời đạt độ sâu ép nhựa hoàn hảo tương tự T0 (trừ -0.02mm vào `gcode_z_offset` của từng tool T1–T4).

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — Cập nhật `[cartographer touch_model default]` `z_offset` và `gcode_z_offset` của `[tool T1]` đến `[tool T4]`.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-align-all-tools-z-offset-20260807-161100/printer.cfg)

### Chi tiết thay đổi
- **T0 (Cartographer Touch `z_offset`):** `-0.05` → `-0.03` (+0.02mm Z datum cho T0)
- **T1 (`gcode_z_offset`):** `0.328` → `0.308` (-0.02mm)
- **T2 (`gcode_z_offset`):** `-0.175` → `-0.195` (-0.02mm)
- **T3 (`gcode_z_offset`):** `-0.178` → `-0.198` (-0.02mm)
- **T4 (`gcode_z_offset`):** `0.086` → `0.066` (-0.02mm)

### Lý do
Do T0 là reference tool, khi đặt `touch_model z_offset = -0.03` để T0 có lớp in đẹp nhất, toàn bộ gốc Z0 của máy nâng lên 0.02mm. Để T1–T4 không bị hở dây / kém dính, ta đồng thời giảm 0.02mm giá trị `gcode_z_offset` tương đối của T1–T4. Kết quả là T0, T1, T2, T3, T4 đều được ép vừa đủ và in đẹp đồng nhất.

### Kiểm tra
- Kiểm tra cú pháp Klipper: Đạt

### Kết quả
Đã áp dụng toàn bộ thông số Z-offset đồng bộ mới vào `printer.cfg`.

### Vấn đề còn lại
Cần người dùng chạy `FIRMWARE_RESTART` trên Klipper / Mainsail và thực hiện in thử nghiệm đa màu/đa tool để kiểm chứng.

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

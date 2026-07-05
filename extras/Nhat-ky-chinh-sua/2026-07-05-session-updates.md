# Nhật ký — 2026-07-05

## 1. Hạ resolution camera MF-500 từ 2560x1400 xuống 800x600

### Mục tiêu
Camera MF-500 không load được ảnh khi đặt resolution 2560x1400. Hạ xuống 800x600 để camera hoạt động ổn định.

### File đã sửa đổi
- `config/crowsnest.conf` — thay đổi `resolution` từ `2560x1400` → `800x600`

### Sao lưu
- [crowsnest.conf (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-camera-resolution-fix-20260705-180500/crowsnest.conf)

### Chi tiết thay đổi
- `resolution: 2560x1400` → `resolution: 800x600`
- Comment được cập nhật ghi rõ lý do hạ resolution

### Lý do
Theo datasheet nhà sản xuất (đọc từ ảnh cấu hình camera), MF-500 là camera 2K (5MP) sử dụng sensor 1/3 inch CMOS OV, kết nối USB 2.0. Ở resolution 2560x1400:
- MJPEG: 30fps (lý thuyết)
- YUY2: chỉ 1fps

Trên thực tế, camera không load được ảnh ở 2560x1400 qua camera-streamer trên Raspberry Pi. Bandwidth USB 2.0 (~480Mbps shared) có thể không đủ để xử lý stream 2K ổn định.

Ở 800x600:
- MJPEG: 30fps (đảm bảo)
- Đủ chất lượng cho giám sát in 3D

### Thông tin camera (từ datasheet)
| Thông số | Giá trị |
|----------|---------|
| Model | MF-500 2K |
| Sensor | 1/3 inch CMOS OV |
| Pixel size | 1.4μm x 1.4μm |
| Độ phân giải tối đa | 2560x1400 |
| Kết nối | USB 2.0 UVC |
| Dòng tiêu thụ | 150-200mA |
| Đầu ra | MJPG (mặc định), YUY2/YUYV |
| Tần số | 50Hz/60Hz (chống nhấp nháy) |

### Kiểm tra
- Kiểm tra cú pháp: ✅ đạt — cú pháp crowsnest.conf hợp lệ
- Khởi động lại Crowsnest: ⏳ người dùng cần restart trên máy in

### Kết quả
File đã được sửa đổi thành công. Cần khởi động lại Crowsnest trên Raspberry Pi để áp dụng.

### Vấn đề còn lại
- Nếu 800x600 vẫn không load: thử 640x480 hoặc 1280x720
- Có thể thử `mode: ustreamer` thay vì `camera-streamer` nếu vẫn gặp lỗi
- Cân nhắc nâng lên 1280x720 nếu 800x600 hoạt động tốt (vẫn 30fps MJPEG theo datasheet)

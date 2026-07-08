# Nhật ký - 2026-07-08

## 1. Cập nhật hướng dẫn Setup & Updates trong README

### Mục tiêu
Làm rõ rằng repository này là bộ cấu hình production cho hệ thống StealthChanger, không phải gói cài Klipper độc lập. Trên máy mới chỉ có Klipper, cần cài sẵn các phụ thuộc như `klipper-toolchanger-easy`, Cartographer support và `Klippain-ShakeTune` trước khi deploy cấu hình.

### File đã sửa đổi
- `Voron 5 Tool/README.md` - cập nhật phần `Setup & Updates`

### Chi tiết thay đổi
- Thêm cảnh báo rằng repo chỉ cung cấp cấu hình, không cài plugin.
- Nêu rõ các phụ thuộc cần có trước khi copy `config/`.
- Bổ sung thứ tự cài đặt khuyến nghị cho máy mới.
- Làm rõ script `install.sh` và `update.sh` chỉ sao chép config, không tự cài plugin.

### Lý do
Tránh hiểu nhầm rằng clone repo này là có thể chạy ngay trên một máy mới chỉ cài Klipper. Thực tế cần hoàn tất stack phụ thuộc của toolchanger/probe/shaketune trước để cấu hình nạp được bình thường.

### Kiểm tra
- Đọc lại README sau khi sửa: đạt

### Kết quả
Phần Setup & Updates đã phản ánh đúng hơn điều kiện tiên quyết của hệ thống thực tế.

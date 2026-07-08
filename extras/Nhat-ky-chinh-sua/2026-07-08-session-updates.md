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

## 2. Thêm link và lệnh SSH cài phụ thuộc cho README

### Mục tiêu
Giúp người dùng cài nhanh các phụ thuộc cần có trước khi áp dụng repo config, thay vì phải tự đi tìm tài liệu cho từng plugin.

### File đã sửa đổi
- `Voron 5 Tool/README.md` - thêm bảng links và lệnh SSH tham khảo

### Chi tiết thay đổi
- Thêm mục `Required Dependencies`.
- Gắn link chính thức tới `klipper-toolchanger-easy`, Cartographer và `Klippain-ShakeTune`.
- Bổ sung snippet SSH mẫu để cài `klipper-toolchanger-easy` và `Klippain-ShakeTune`.

### Lý do
Trên máy mới chỉ cài Klipper, repo này sẽ chưa hoạt động nếu các plugin phụ trợ chưa được cài. Đặt sẵn link và lệnh SSH giúp giảm ma sát cho bước khởi tạo.

### Kiểm tra
- Đọc lại README sau khi sửa: đạt

### Kết quả
README giờ có cả đường dẫn tài liệu lẫn lệnh cài nhanh để người dùng đi theo ngay từ đầu.

## 3. Bổ sung lệnh SSH cài Cartographer từ docs chính thức

### Mục tiêu
Thêm lệnh cài Cartographer đúng theo tài liệu chính thức của Cartographer3D để người dùng có thể nạp trực tiếp qua SSH mà không phải tìm lại.

### File đã sửa đổi
- `Voron 5 Tool/README.md` - bổ sung lệnh cài Cartographer plugin và legacy module

### Chi tiết thay đổi
- Cập nhật dòng Cartographer trong bảng `Required Dependencies` để trỏ tới docs chính thức.
- Thêm lệnh SSH cho workflow Cartographer plugin mới:
  - `curl -s -L https://raw.githubusercontent.com/Cartographer3D/cartographer3d-plugin/refs/heads/main/scripts/install.sh | bash -s -- --klipper ~/klipper --klippy-env ~/klippy-env`
- Thêm lệnh SSH cho workflow legacy/classic:
  - `git clone https://github.com/Cartographer3D/cartographer-klipper.git`
  - `./cartographer-klipper/install.sh`

### Lý do
Các máy mới thường chỉ có Klipper cơ bản. Việc đưa sẵn lệnh chính thức vào README giúp cài phụ thuộc nhanh hơn và giảm nguy cơ dùng nhầm hướng dẫn cũ hoặc không đúng nhánh plugin.

### Kiểm tra
- Đọc lại README sau khi sửa: đạt

### Kết quả
README đã có đường dẫn chính thức của Cartographer3D và command SSH để cài trực tiếp từ docs.

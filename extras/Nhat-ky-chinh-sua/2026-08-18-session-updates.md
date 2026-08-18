# Nhật ký — 2026-08-18

## 1. Tích hợp kTAMV và điều chỉnh cấu hình Axiscope

### Mục tiêu
Lên kịch bản tích hợp hệ thống kTAMV để tự động đo XY Offset bằng Nozzle Camera. Đồng thời, sửa lại tọa độ Y của cảm biến Z-Offset (Axiscope) từ `-10.0` thành `-1.0` theo thông số thực tế của người dùng.

### File đã sửa đổi
- `config/Printer-Setup/calibration.cfg` — sửa tham số `zswitch_y_pos` trong `[axiscope]`.
- `config/Printer-Setup/ktamv_auto_calibration.cfg` — tạo mới file chứa macro `AUTO_ALIGN_ALL_TOOLS` để tự động hóa kTAMV và Axiscope. (Chưa include vào `printer.cfg`).

### Sao lưu
- [Thư mục sao lưu](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-ktamv-auto-20260818-194300/)

### Chi tiết thay đổi
- Trong `calibration.cfg` section `[axiscope]`: `zswitch_y_pos: -10.0` → `zswitch_y_pos: -1.0`
- Tạo file macro nhận diện động vị trí camera.

### Lý do
Người dùng xác nhận Y thực tế của công tắc là -1, không phải -10. Việc tạo file macro kTAMV riêng giúp mã nguồn độc lập, đảm bảo an toàn khi máy đang trong quá trình in.

### Kiểm tra
- Macro kTAMV sẽ được đưa vào vận hành (include) khi người dùng hoàn thành lắp đặt phần cứng camera và máy in rảnh rỗi.

### Kết quả
Đã có sẵn kịch bản và macro hoàn chỉnh chờ được kích hoạt.

### Vấn đề còn lại
- Chờ người dùng lắp xong camera và gọi lệnh include để kích hoạt macro.

## 2. Tạo dự án độc lập Voron Tool Vision (VTV)

### Mục tiêu
Hợp nhất Axiscope và kTAMV thành một dự án tự chủ duy nhất, loại bỏ hoàn toàn sự phụ thuộc vào các repository bên ngoài.

### File và Thư mục đã thay đổi
- Tạo mới toàn bộ dự án tại `extras/Voron-Tool-Vision/`
- Trích xuất và dọn dẹp mã nguồn OpenCV từ kTAMV vào `vision_server/`
- Trích xuất mã nguồn Axiscope và kTAMV vào `klippy/extras/` (`vtv_z_probe.py` và `vtv_xy_vision.py`)
- Tạo file cài đặt tự động `install.sh` và `README.md`
- Xóa file macro `ktamv_auto_calibration.cfg` cũ, thay bằng `macros/vtv_auto_calibration.cfg` tích hợp lệnh mới.

### Chi tiết thay đổi
- Chuyển đổi tên class và reference để tránh xung đột với Klipper.
- Chuyển lệnh GCode từ `KTAMV_` thành `VTV_XY_` và module Z thành `VTV_Z`.

### Kết quả
Hệ thống hiện tại đã sở hữu mã nguồn lõi 100%. Người dùng chỉ cần chạy `install.sh` để kích hoạt toàn bộ hệ thống Vision Server và Klipper Plugin khi sẵn sàng.

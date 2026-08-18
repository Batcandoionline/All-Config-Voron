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

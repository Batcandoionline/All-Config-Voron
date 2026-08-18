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

## 2. Xóa bỏ bản sao chép, lập trình lại dự án "Tool Vision" từ đầu

### Mục tiêu
Người dùng yêu cầu xóa bỏ cách làm sao chép/chỉnh sửa mã nguồn cũ (Voron-Tool-Vision). Thay vào đó, yêu cầu đập đi xây lại toàn bộ, lập trình bằng Python từ con số 0 một Klipper Extension hoàn chỉnh tên là **Tool Vision**, kế thừa logic toán học gốc nhưng hiện đại và tối ưu hơn.

### File và Thư mục đã thay đổi
- **XÓA:** Toàn bộ thư mục `extras/Voron-Tool-Vision` (bản làm trước đó).
- **TẠO MỚI:** Thư mục `extras/Tool-Vision` với cấu trúc chuẩn.
- **Klipper Extension (`tool_vision.py`):** Lập trình mới hoàn toàn Klipper Plugin kế thừa `probe_multi_axis` để đo Z, tích hợp tự động HTTP Request tới máy chủ ảnh, và tính toán mm/pixel tự động bằng GCode thay vì bằng numpy phức tạp.
- **Vision Server (`vision_server.py`):** Viết lại máy chủ OpenCV cực nhẹ bằng Flask. Giữ nguyên thuật toán BlobDetector của kTAMV gốc nhưng tinh giản và nhanh hơn.
- **File Cấu hình (`tool_vision.cfg`):** Tạo file `.cfg` độc lập, tập trung toàn bộ tọa độ Z, Camera, URLs để dễ dàng tùy biến thay vì sửa code.
- **Cài đặt:** Viết `install.sh` và `tool_vision.service` cho Systemd.

### Kết quả
Hệ thống hiện tại có 1 lệnh duy nhất là `TOOL_VISION_CALIBRATE_ALL`. Khi gọi lệnh, máy sẽ tự động đo Z và dò Camera đồng thời một cách mượt mà nhất. Đã commit toàn bộ lên Git.

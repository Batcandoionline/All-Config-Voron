# Klipper Tool Vision

`Tool Vision` là một Klipper Extension độc lập, tự chủ hoàn toàn, được viết lại (rewrite) từ đầu nhằm tối ưu hóa quá trình đo Z-offset (bằng công tắc vi mô) và XY-offset (bằng OpenCV Camera) trên các máy in 3D Multi-Tool (điển hình là Voron).

Dự án này thay thế hoàn toàn Axiscope và kTAMV, gom mọi logic tính toán về một module Klipper duy nhất và một máy chủ OpenCV (Flask) nhẹ nhàng, dễ bảo trì.

## Cấu trúc
- `klippy/extras/tool_vision.py`: Giao tiếp Klipper, điều khiển máy in, gọi lệnh nội bộ đo đạc.
- `server/vision_server.py`: Nhận hình ảnh, phân tích bằng Canny Edge & HoughCircles.
- `tool_vision.cfg`: Nơi chứa toàn bộ cấu hình người dùng (Tọa độ X,Y,Z).

## Hướng dẫn Cài đặt
1. Mở SSH vào Raspberry Pi.
2. Chạy: 
   ```bash
   cd ~/printer_data/config/Voron\ 5\ Tool/extras/Tool-Vision
   chmod +x install.sh
   ./install.sh
   ```
3. Xóa hoặc comment các module cũ như `[axiscope]`, `[ktamv]` trong file cấu hình của bạn.
4. Thêm `[include Voron 5 Tool/extras/Tool-Vision/tool_vision.cfg]` vào `printer.cfg`.

## Hướng dẫn Sử dụng
- Chỉnh sửa `tool_vision.cfg` để khai báo đúng chân cắm công tắc (pin) và tọa độ (z_switch_x, camera_stream_url).
- Khởi động lại Klipper.
- Chạy lệnh `TOOL_VISION_CALIBRATE_ALL` trên giao diện Klipper. 
- Hệ thống sẽ tự động đo Z và Camera song song để thiết lập và lưu toàn bộ Offset cho các Tool.

# Voron Tool Vision (VTV)

Đây là dự án nội bộ được hợp nhất từ 2 dự án: `Axiscope` (đo Z Offset bằng công tắc vi mô) và `kTAMV` (đo XY Offset bằng Camera OpenCV). 

Mục tiêu của dự án này là đem lại khả năng đo đạc tự động **đồng thời** cả Z và XY cho toàn bộ các Tool trên máy in Voron Multi-Tool một cách độc lập và liền mạch, không còn phụ thuộc vào các repository bên thứ ba đã ngừng bảo trì.

## Tính năng
- `vtv_z_probe`: Klipper plugin quản lý công tắc vi mô đo Z.
- `vtv_xy_vision`: Klipper plugin giao tiếp với máy chủ nhận diện ảnh.
- `vision_server`: Máy chủ OpenCV độc lập chuyên nhận diện tâm lỗ kim phun (Nozzle).
- `macros/vtv_auto_calibration.cfg`: Kịch bản đo lường tự động "All In One" 1 click.

## Hướng dẫn Cài đặt

1. Đăng nhập SSH vào máy in (Raspberry Pi / BTT CB1, etc.).
2. Cấp quyền thực thi cho script cài đặt:
   ```bash
   cd ~/printer_data/config/Voron\ 5\ Tool/extras/Voron-Tool-Vision/
   chmod +x install.sh
   ```
3. Chạy script cài đặt:
   ```bash
   ./install.sh
   ```
4. Làm theo hướng dẫn trên màn hình:
   - Xóa bỏ hoặc Comment đoạn cấu hình `[axiscope]` cũ trong file `calibration.cfg` của bạn.
   - Thêm dòng `[include Voron 5 Tool/extras/Voron-Tool-Vision/macros/vtv_auto_calibration.cfg]` vào `printer.cfg`.

## Hướng dẫn Sử dụng

Quy trình sử dụng không thay đổi, nhưng sẽ diễn ra liên tục:
1. Lau chùi thủ công thật sạch sẽ toàn bộ 5 đầu in.
2. Đặt camera ngửa lên bàn in.
3. Kéo tay đầu `T0` ra nằm ngay giữa camera.
4. Chạy lệnh: `VTV_AUTO_ALIGN`
5. Máy sẽ tự động đo Z và XY cho T0, sau đó lặp lại cho T1->T4.
6. Chạy `SAVE_CONFIG` để lưu kết quả.

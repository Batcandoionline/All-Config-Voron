# Nhật ký thay đổi (Changelog)

Tất cả thay đổi đáng chú ý của cấu hình máy in được ghi nhận ở đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/).

---

## [1.5.0] — 2026-08-23

### Thay đổi
- Giao toàn quyền quản lý `toolchanger/readonly-configs/` cho KTC-Easy; All-Config chỉ deploy cấu hình người dùng và các override.
- Thêm preflight bắt buộc kiểm tra đủ sáu symlink KTC-Easy hợp lệ trước khi backup hoặc deploy.
- Xác nhận bộ Input Shaper production riêng cho T0–T4 và đồng bộ lại chú thích theo đúng giá trị đang dùng.
- Cập nhật tài liệu về Axiscope PF2 production, ToolVision inactive và kTAMV đã gỡ.

### Đã sửa
- Ghi nhận lỗi Cartographer và cảm biến T4 đã hết theo xác nhận của người vận hành.
- Sửa tài liệu nhầm `gcode_x_offset` của T2 thành Z-offset và loại bỏ hướng dẫn kTAMV không còn tồn tại.
- Bổ sung metadata submodule còn thiếu cho `extras/Axiscope-reference`.

## [1.4.0] — 2026-08-09

### Thêm mới
- Cấu hình module `[axiscope]` trong `Printer-Setup/calibration.cfg` hỗ trợ công tắc vi mô đo Z-offset cho các đầu in (T0–T4) tại tọa độ X:68, Y:-10, Z:7.
- Tự động loại trừ các file `README.md` và `*.md` trong `config/scripts/install.sh` và `config/scripts/update.sh` khi đồng bộ sang máy in.

### Thay đổi
- Cập nhật chân tín hiệu switch Z-offset sang `pin: ^PF2` trên Manta M8P V2 (khớp với kết nối thực tế PF2 + GND).
- Đồng bộ khối `SAVE_CONFIG` mới nhất từ máy in thực tế: Cartographer touch threshold mới `1819`, reference_temperature `42.44`, các hệ số scan model và PID calibration.
- Khôi phục bộ giá trị `gcode_z_offset` in thực tế đẹp cho các cụm đầu in (`T1: 0.228`, `T2: -0.295`, `T3: -0.268`, `T4: 0.086`).
- Làm mới và đồng bộ hóa toàn diện tài liệu dự án, hệ thống quy tắc `.agents/`, và các file README.

---

## [1.3.0] — 2026-07-02

### Thêm mới
- Nhật ký xử lý sự cố cho sự cố timeout CAN Cartographer.

### Đã sửa
- Timeout kết nối MCU Cartographer sau soft restart (giải pháp tạm: tắt nguồn hoàn toàn).

---

## [1.2.0] — 2026-06-30

### Thay đổi
- Cập nhật `zero_reference_position` trong `probe-mesh.cfg` từ `170, 203` sang `174, 168` để khớp vị trí homing nozzle.
- Cập nhật ngưỡng touch Cartographer từ `1968` lên `2594` sau khi hiệu chuẩn lại.
- Điều chỉnh Z-offset cho tool T1, T2, T3, T4 dựa trên hiệu chuẩn lại.
- Tinh chỉnh Z-offset T3 thêm -0.08mm dựa trên thử in thực tế.

### Thêm mới
- Quy tắc bảo mật trong `.gitignore` cho `*.secrets`, `moonraker.secrets`, `wpa_supplicant.conf`.

---

## [1.1.0] — 2026-06-23

### Thay đổi
- Tăng `check_gain_time` của `heater_bed` từ 120s lên 240s để ngăn shutdown giả từ nhiễu SSR.
- Điều chỉnh `retry_tolerance` QGL từ 0.005 lên 0.0075 để ngăn hủy giả do motor numbering.

### Thêm mới
- Cấu hình camera MF-500 ở độ phân giải 2K với chống nhấp nháy 50Hz.
- Hỗ trợ WebRTC qua camera-streamer.

---

## [1.0.0] — 2026-05-16

### Thêm mới
- Cấu hình production ban đầu cho Voron 2.4 StealthChanger 5-Tool.
- Cấu hình SexBolt Z endstop.
- Tất cả định nghĩa tool (T0–T4) với board EBB CAN bus.
- Cài đặt probe Cartographer v3.
- Bộ macro hoàn chỉnh (PRINT_START, PRINT_END, vệ sinh đầu phun, prime line).

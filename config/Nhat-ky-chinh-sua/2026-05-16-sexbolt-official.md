# Nhật ký chỉnh sửa - 2026-05-16

## Mục tiêu tại thời điểm đó

Tạm dừng hướng dùng Axiscope Cartographer và quay lại workflow chính thức của StealthChanger/KTC-Easy với SexBolt/SexBall probe và `tools_calibrate`.

## Backup đã tạo

Backup trước khi quay lại workflow SexBolt chính thức:

```text
config/_backups/sexbolt-official-20260516-210825/
```

Backup cho thay đổi dây M1-STOP/PF4:

```text
config/_backups/sexbolt-m1-stop-20260517-155108/
```

Backup trước khi chuyển comment/hướng dẫn sang tiếng Anh:

```text
config/_backups/english-comments-20260517-155728/
```

Các file được backup:

- `Printer-Setup/probe-mesh.cfg`
- `toolchanger/toolchanger-config.cfg`
- `Printer-Setup/calibration.cfg`

## Thay đổi cấu hình chính

- Comment toàn bộ block `[axiscope]` trong `Printer-Setup/probe-mesh.cfg`.
- Bật lại `[tools_calibrate]` trong `toolchanger/toolchanger-config.cfg`.
- Giữ cấu hình SexBolt/SexBall đang hoạt động:
  - `pin: ^PF4` trên M1-STOP của Manta M8P V2.0.
  - `trigger_to_bottom_z: 0.9`.
  - `samples: 5`.
  - `samples_result: median`.
  - `probe: probe`.
- Cập nhật tọa độ SexBolt/SexBall:
  - `_CALIBRATION_SWITCH.variable_x: 257`.
  - `_CALIBRATION_SWITCH.variable_y: 327`.
  - `_CALIBRATION_SWITCH.variable_z: 60`.
  - `Z55` chỉ là chiều cao tiếp xúc/top-of-ball ước lượng, không dùng làm Z tiếp cận an toàn.
- Cập nhật `Printer-Setup/calibration.cfg` để ghi rõ workflow `CALIBRATE_ALL_OFFSETS` cho XYZ offset.
- Thêm macro public `CHECK_OFFSETS`, gọi `_CHECK_OFFSETS`, để lệnh trong hướng dẫn có tồn tại.

## Tóm tắt việc đã làm trước đó với Axiscope

- Đọc và phân tích `Axiscope-cartographer-main/klippy/extras/axiscope.py`.
- Phát hiện hướng Axiscope Cartographer ban đầu đọc sai kết quả touch probe và trả về `2.000` thay vì `cartographer.touch.last_z_result`.
- Sửa `axiscope.py` để đọc `cartographer.touch.last_z_result` và bỏ fallback sai về Z hiện tại của toolhead.
- Kiểm tra log máy in: Axiscope đã trả về giá trị contact Z thật, ví dụ T1/T2/T3/T4 quanh `0.022`, `-0.114`, `-0.314`, `-0.324`.
- So sánh với offset first-layer kiểu Ellis3DP và kết luận giá trị touch của Cartographer không khớp trực tiếp với offset cho first layer đẹp.
- Tạo repo fork Axiscope Cartographer: `https://github.com/Batcandoionline/Axiscope-cartographer`, gồm `README.md`, `FORK_INFO.md`, script install/uninstall và cấu hình Moonraker Update Manager.
- Sau đó tạm dừng Axiscope và quay lại workflow SexBolt/SexBall chính thức.

## Workflow khuyến nghị sau khi nạp cấu hình này

```gcode
G28
QUAD_GANTRY_LEVEL
G28 Z
CALIBRATE_ALL_OFFSETS
```

Sau khi macro lưu offset bằng `SAVE_TOOL_PARAMETER`, chạy:

```gcode
FIRMWARE_RESTART
CHECK_OFFSETS
```

## Lưu ý

- Không bật `[axiscope]` và `[tools_calibrate]` cùng lúc, vì cả hai dùng helper `probe_multi_axis`.
- Nếu trạng thái SexBolt/SexBall sai, kiểm tra `^PF4` bằng `QUERY_ENDSTOPS`; nếu logic bị đảo thì đổi thành `^!PF4`.
- Nếu Z offset từ SexBolt khác kết quả first-layer thực tế, dùng test first layer/Ellis làm xác nhận chất lượng in cuối cùng.

## Cập nhật 2026-05-17 - chuyển dây SexBolt sang M1-STOP/PF4

- Theo pinout Manta M8P V2.0: `M1-STOP = PF4`, `M3-STOP = PF2`, `M5-STOP = PF0`.
- Giữ `stepper_x.endstop_pin: PF0` vì đây là M5-STOP và không xung đột với M1-STOP.
- Đổi `[tools_calibrate] pin` từ `^PF2` sang `^PF4`.
- Đổi tâm bi của `CALIBRATE_MOVE_OVER_PROBE` / `_CALIBRATION_SWITCH` thành `X257 Y327`.
- Giữ Z tiếp cận an toàn ở `60`; `Z55` chỉ là chiều cao tiếp xúc ước lượng khi đo lại `trigger_to_bottom_z`.

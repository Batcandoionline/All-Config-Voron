# 2026-05-18 - Tổng kết phiên cấu hình

## Mục đích

Lưu lại bối cảnh làm việc sau phiên cấu hình để các phiên sau có thể hiểu nhanh đã thay đổi gì và vì sao.

## Hướng chính

- Tạm dừng hướng hiệu chỉnh Z offset bằng Axiscope Cartographer.
- Quay lại workflow chính thức của StealthChanger/KTC-Easy dùng SexBolt/SexBall và `tools_calibrate` để hiệu chỉnh offset giữa các tool.
- Giữ Cartographer làm probe chính cho homing, touch home và bed mesh.
- SexBolt/SexBall chỉ dùng cho calibration XYZ giữa các tool.

## Cấu hình SexBolt/SexBall

- Cảm biến nối vào Manta M8P V2.0 `M1-STOP`, pin `PF4`.
- Cấu hình trong `toolchanger/toolchanger-config.cfg`:

```ini
[_CALIBRATION_SWITCH]
variable_x: 257
variable_y: 327
variable_z: 60

[tools_calibrate]
pin: ^PF4
trigger_to_bottom_z: 0.9
```

- `Z55` từ đo vật lý là chiều cao tiếp xúc ước lượng trên bi.
- `Z60` dùng làm chiều cao tiếp cận an toàn.

## Tool offset đã lưu từ SexBolt

Offset hiện tại trong `printer.cfg` tại thời điểm đó:

```ini
T1: X ~0,       Y 0.215625,  Z 0.05
T2: X -0.11875, Y -0.1125,   Z -0.210
T3: X -0.16875, Y -0.096875, Z -0.328
T4: X 0.100,    Y 0.003125,  Z -0.278
```

Giá trị X của T1 hiển thị dạng scientific notation, ví dụ `7.548e-11`, thực tế xem như bằng 0.

## Dịch comment cấu hình

- Các comment trong cấu hình active được dịch sang tiếng Anh ở thời điểm đó.
- Backup trước khi dịch:

```text
C:\Users\batca\OneDrive\Desktop\All\config_full_backup_before_english_comments_20260517-163340
```

- Các thư mục backup và bản copy cấu hình cũ không dịch.

## Căn chỉnh Y của dock

Do quan hệ vật lý giữa Y endstop và dock thay đổi, toàn bộ `params_park_y` được giảm tổng cộng `0.5 mm`.

Giá trị sau chỉnh:

```ini
T0 params_park_y: 1.8
T1 params_park_y: 2.3
T2 params_park_y: 2.5
T3 params_park_y: 2.5
T4 params_park_y: 2.8
```

Backup liên quan:

```text
config/_backups/park-y-minus-0.3-20260517-171800
config/_backups/park-y-minus-0.2-more-20260517-211156
```

## Tuning tốc độ toolchange

Giá trị đã cập nhật:

```ini
params_fast_speed: 15000  # khoảng 250 mm/s
max_z_velocity: 60
max_z_accel: 700
```

Backup trước khi tuning tốc độ:

```text
config/_backups/speed-tuning-20260518-155957
```

## OrcaSlicer / G-code

File G-code kiểm tra có toolchange thật dù preview OrcaSlicer hiển thị `0` filament changes.

Kết quả quan sát:

```text
T command count: 451
Toolchange comments: 450
```

Lý do: bộ đếm "filament changes" của Orca dùng cho single-extruder/MMU, không phản ánh các lệnh toolchanger vật lý `T1/T2/T3/T4`.

## PETG ooze và vụn nhựa nhỏ

Hiện tượng:

- Tool đi tới wipe tower trước.
- Sau wipe, PETG đôi khi vẫn cong/dính ở nozzle rồi rơi xuống sau đó.

Hướng tuning được đề xuất:

```text
PETG nozzle temperature: 220 -> 215C
Retraction: 2.0 -> 1.0-1.2mm
Bật wipe while retracting
Wipe distance: 1 -> 2mm
Wipe tower speed: 90 -> 60-70mm/s
Rib width: 8 -> 10/12
Tạm tắt ramming để test
```

## Mobileraker và Tailscale

Hướng truy cập từ xa:

- Dùng Tailscale thay vì mở port router.
- Dùng Mobileraker với Moonraker URL:

```text
http://<printer-tailscale-ip>:7125
```

Moonraker cần trust IP Tailscale của điện thoại/laptop hoặc dải CGNAT của Tailscale:

```ini
[authorization]
trusted_clients:
    127.0.0.1
    192.168.1.0/24
    100.64.0.0/10
```

Nếu muốn chặt hơn, chỉ trust IP Tailscale cụ thể của thiết bị cá nhân.

## GitHub config repository

Đã tạo và push repository cấu hình active:

```text
https://github.com/Batcandoionline/Stealth-changer-config
```

Ở thời điểm đó, chính thư mục `config` là Git repository.

Đã thêm:

```text
README.md
scripts/install.sh
scripts/update.sh
.gitignore
.gitattributes
```

Các mục ignore khỏi Git:

```text
_backups/
*.zip
*backup*
*.log
*.gcode
```

Cấu hình Moonraker Update Manager được thêm:

```ini
[update_manager stealth-changer-config]
type: git_repo
path: ~/printer_data/config
origin: https://github.com/Batcandoionline/Stealth-changer-config.git
primary_branch: main
managed_services: klipper
```

Cài lần đầu trên máy in:

```bash
cd /tmp
git clone https://github.com/Batcandoionline/Stealth-changer-config.git
cd Stealth-changer-config
bash scripts/install.sh
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

Cập nhật về sau:

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

## Review tool crash detection

Đã kiểm tra upstream:

```text
https://github.com/cekim-git/tool_crash
```

Kết luận:

- Plugin upstream vẫn alpha/WIP.
- Plugin load trong log Klipper hiện tại không có lỗi import/config.
- Plugin đọc `detection_pin` của từng tool; không dùng Cartographer và không dùng SexBolt/PF4.
- Cartographer vẫn độc lập với vai trò Z probe.
- Hệ thống đang dùng Klipper `v0.13.0-650-gca8230d50-dirty`, Cartographer V3 `6.1.0`, và `klipper-toolchanger-easy`.

Sửa quan trọng:

- `STOP_CRASH_DETECTION` được gọi trong `dropoff_gcode`.
- Trước khi sửa, crash detection có thể bị tắt sau toolchange đầu tiên trong lúc in.
- Thêm logic bật lại trong `after_change_gcode`: nếu `_PRINT_STATE == "printing"`, chạy `START_CRASH_DETECTION` sau khi đổi tool xong.

Commit đã push:

```text
cb985bc Fix tool crash detection after toolchange
```

## Smoke test khuyến nghị

Sau khi pull cấu hình về máy in:

```gcode
FIRMWARE_RESTART
INITIALIZE_TOOLCHANGER
T0
T1
T2
T3
T4
T0
START_TOOL_CRASH_DETECTION
STOP_TOOL_CRASH_DETECTION
```

Kết quả mong đợi trong console:

```text
tool_crash: enabled
tool_crash: disabled
```

Trong bản in thật, sau mỗi toolchange console nên hiện lại `tool_crash: enabled`.

## Review LED

Đã rà các file liên quan LED:

```text
Printer-Setup/fans-leds.cfg
toolchanger/toolchanger-config.cfg
Printer-Setup/print-macros.cfg
Printer-Setup/nozzle-clean.cfg
mainsail.cfg
toolchanger/tools/T0.cfg ... T4.cfg
```

Kết luận và sửa lỗi:

- Cả 5 toolhead đều định nghĩa `T0_LED` đến `T4_LED`, mỗi tool là chuỗi neopixel 3 LED, thứ tự màu GRB.
- Mọi tên trạng thái LED được macro gọi đều có trong `_SET_TOOL_LED`.
- Sửa thứ tự cleanup khi cancel: `_CUSTOM_CANCEL_CLEANUP` đặt `_PRINT_STATE` về `idle` trước mọi toolchange về T0, tránh `after_change_gcode` khôi phục LED printing hoặc bật lại crash detection trong cancel cleanup.
- Thêm `STOP_CRASH_DETECTION` sau toolchange T0 lúc cancel để làm lớp an toàn bổ sung.
- Đã cân nhắc thêm LED cho macro calibration, nhưng không copy toàn bộ macro SexBolt upstream chỉ để đổi màu LED vì rủi ro cao trên máy thật.

Kiểm tra tĩnh đã chạy:

```text
LED macro reference check: no missing LED macros
LED state check: all used states are defined
Toolhead LED check: T0-T4 all have chain_count=3 and color_order=GRB
git diff --check: clean
Line endings: LF per .gitattributes
```

## Dọn comment tiếng Việt trong cấu hình

Backup trước khi sửa:

```text
config/_backups/vietnamese-to-english-20260518-165324
```

Đã dịch các comment hoặc thông báo người vận hành còn tiếng Việt/không dấu trong cấu hình active:

```text
Printer-Setup/print-macros.cfg
Printer-Setup/fans-leds.cfg
```

Cũng dọn bản backup root bị ignore:

```text
printer.cfgbackup
```

Lưu ý:

- Không đổi giá trị vận hành như `KlipperScreen.conf` `language = vi`; đó là thiết lập UI.
- Không sửa `_backups/`, `.git/`, file zip hoặc nhật ký lịch sử ngoại trừ file tổng kết này.

## Sửa README phần hardware

- Cập nhật README để phần hardware chỉ mô tả phần cứng, không trộn giá trị tuning phần mềm.
- Bỏ các chi tiết tuning khỏi mục `Current Machine`: tốc độ toolchanger, giới hạn Z, workflow input shaper, pin SexBolt.
- Thay bằng mô tả phần cứng: Voron 2.4, toolchanger, motion system, Manta M8P V2.0 + CM4, Cartographer V3, EBB toolhead board, hotend/extruder, sensor, bed/chamber, fan và LED.
- Sửa mô tả T4 từ EBB46 V1.2 thành EBB36 V1.2 theo cấu hình active và xác nhận phần cứng.
- Sửa comment trong `toolchanger/tools/T4.cfg` từ EBB46 V1.2 thành EBB36 V1.2; không đổi pin hoặc giá trị runtime.

Phần cứng đã xác nhận:

- Khung nền Voron 2.4 350 mm.
- StealthChanger có phần nóc nâng thêm khoảng 250 mm.
- Cả 5 toolhead dùng TZ V6 2.0 hotend với WW BMG extruder.

## Review logic runtime và guard an toàn

Đã rà các phần vận hành như một state machine:

```text
PRINT_START
PRINT_END
CANCEL_PRINT cleanup hook
CLEAN_NOZZLE
toolchanger pickup/dropoff hooks
crash detection override
```

Sửa đã thực hiện:

- Xóa include trực tiếp trùng của `toolchanger/toolchanger-config.cfg` khỏi `printer.cfg`; file này đã được include qua `toolchanger/readonly-configs/toolchanger-include.cfg`.
- Giữ nguyên `toolchanger/readonly-configs`; mọi thay đổi behavior nằm ở file override/custom.
- Sửa logic chọn `START_CRASH_DETECTION` / `STOP_CRASH_DETECTION` để kiểm tra `[tool_crash]` đã cấu hình thay vì tìm command như gcode macro.
- Thêm override `M109` trong `toolchanger/toolchanger-config.cfg` để `M109 S...` không có `T` không bị lỗi khi macro upstream KTC không thấy tham số `T`.
- Thêm guard active extruder rỗng trong `CLEAN_NOZZLE` và `PRINT_END`, tránh lookup `printer[""]` và tránh heat/purge/retract không an toàn.
- Cập nhật `PRINT_END` và cancel cleanup để chỉ gọi `T0` khi thật sự có tool khác 0 đang active; nếu toolchanger đang `-1` thì bỏ qua pickup T0 và báo trạng thái.
- Làm rõ `_PRINT_START_SELECT_T0`: `T1..T4` nghĩa là chuyển về T0, `-1` nghĩa là pickup T0 sau full homing để clean/touch-home.
- Thêm `t_command_restore_axis: Z` trong override `[toolchanger]` để cố định hành vi restore trục Z của KTC-Easy.
- Đổi các kiểm tra tồn tại LED/fan sang dạng `printer["..."] is defined`.

Kiểm tra tham chiếu:

- So với tài liệu/ví dụ StealthChanger/KTC-Easy: cấu hình toolchange nên nằm trong file override/custom, print start nên home và dùng T0 cho calibration trước in, `safe_y`/`close_y` phải xem là giá trị cơ khí đã calib.
- Giữ nguyên `safe_y`, `close_y`, park position, speed và các giá trị calibration SexBolt/Cartographer hiện có.

Kiểm tra tĩnh:

```text
Include graph: 23 active files / 23 unique files
Missing includes: none
Repeated active file loads: none
toolchanger/readonly-configs diff: none
git diff --check: clean
```

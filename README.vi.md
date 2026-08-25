# Cấu hình production Voron 2.4 StealthChanger năm tool

[English](README.md) | [Tiếng Việt](README.vi.md) | [Chỉ mục tài liệu](extras/docs/README.vi.md) | [Tham khảo config đang hoạt động](config/README.vi.md)

Repository này chứa cấu hình production đã review, script triển khai, profile
OrcaSlicer và tài liệu vận hành cho một máy Voron 2.4 CoreXY 350 mm cụ thể với
năm tool StealthChanger. Đây không phải cấu hình mẫu có thể chép trực tiếp sang
máy khác.

> [!IMPORTANT]
> Mã phần cứng, giới hạn chuyển động, tọa độ dock và offset trong tài liệu là
> giá trị riêng của máy này. Hãy đọc file source được nêu cạnh từng giá trị
> trước khi áp dụng cho máy khác. Cấu hình được đọc lại ngày 2026-08-24 từ
> revision `1a09b7f`.

## Bắt đầu từ đây

| Tôi muốn… | Đọc hoặc chạy |
| --- | --- |
| Hiểu tổng thể máy | [Tổng quan hệ thống](#tổng-quan-hệ-thống) và [sơ đồ tool](#sơ-đồ-tool) |
| Chuẩn bị một bản in bình thường | [Quy trình in bình thường](#quy-trình-in-bình-thường) |
| Tìm lệnh Mainsail/Klipper | [Bảng macro vận hành](#bảng-macro-vận-hành) |
| Xem offset đang nạp mà không chuyển động | `CHECK_OFFSETS` |
| Xem backend calibration đang hoạt động | `CALIBRATION_STATUS` |
| Dùng ToolVision | [ToolVision calibration chỉ báo cáo](#toolvision-calibration-chỉ-báo-cáo) |
| Vệ sinh hoặc purge nozzle | [Vệ sinh nozzle và prime line](#vệ-sinh-nozzle-và-prime-line) |
| Sấy filament trên bed | [Hệ thống sấy filament bằng bed](#hệ-thống-sấy-filament-bằng-bed) |
| Cập nhật cấu hình máy | [Cài đặt và cập nhật](#cài-đặt-và-cập-nhật) |
| Khôi phục hoặc dọn backup | [Backup, rollback và dọn dẹp](#backup-rollback-và-dọn-dẹp) |
| Chẩn đoán lỗi thường gặp | [Xử lý sự cố](#xử-lý-sự-cố) |
| Sửa repository | [Quy trình đóng góp an toàn](#quy-trình-đóng-góp-an-toàn) |

## Quy ước trạng thái

Tài liệu dùng các nhãn sau một cách có chủ ý:

- **Đang hoạt động:** được `config/printer.cfg` nạp hoặc được script triển khai
  đang theo dõi sử dụng.
- **Đã quan sát:** đã xác nhận trong một phiên làm việc có ngày cụ thể; đây là
  bằng chứng cho máy này, không phải tuyên bố đúng với mọi phần cứng.
- **Đang phát triển:** đã cài đặt trong nhánh/dự án khác nhưng chưa deploy lên
  máy này nếu không ghi rõ.
- **Đã retired:** giữ cho rollback hoặc so sánh lịch sử, không được nạp.

## Tóm tắt an toàn

- Không deploy, home, probe, căn dock, đổi tool hoặc chạy ToolVision khi đang in.
- Giữ emergency stop sẵn sàng trong lần chuyển động đầu tiên sau khi sửa cơ khí
  hoặc cấu hình.
- Không sửa `config/toolchanger/readonly-configs/`; KTC-Easy sở hữu thư mục này.
- Không thay offset production đã thử nghiệm in bằng một lần đo duy nhất.
- Sao lưu trước khi sửa `.cfg`, `.conf` hoặc `.sh`.
- Không đưa `Generated-Data/`, credential và kết quả riêng của máy vào Git.
- Mở prompt Mainsail không gây chuyển động; xác nhận Setup, Calibrate, Align,
  Clean, Prime hoặc Dryer có thể làm máy di chuyển hoặc nóng.

## Tổng quan hệ thống

| Hạng mục | Cấu hình đang hoạt động |
| --- | --- |
| Máy in | Voron 2.4, CoreXY 350 mm |
| Vùng chuyển động | X `0..348`, Y `-10..336`, Z `-5..347` mm |
| Giới hạn chuyển động | Tốc độ XY `300 mm/s`, gia tốc `4000 mm/s²`, tốc độ Z `60 mm/s`, gia tốc Z `700 mm/s²` |
| Bộ điều khiển/host | BTT Manta M8P V2.0 với BTT CM4 |
| Toolchanger | KTC-Easy StealthChanger, năm dock phía sau, T0–T4 |
| Board tool | Năm BTT EBB36 V1.2 qua CAN |
| Extruder/hotend | Năm WW BMG, năm TZ V6 2.0, nozzle 0.4 mm |
| Z/mesh production | Cartographer V3 Touch + Scan, cố định trên shuttle |
| Chẩn đoán offset tool | ToolVision development canary; method PF2 switch và Cartographer Touch; chỉ báo cáo |
| Bed | Heater silicone AC 1000 W 220 V qua SSR |
| Vệ sinh nozzle | Purge bucket và pad silicone Bambu A1 ở vùng Y âm |
| Camera | MF-500 USB qua Crowsnest/camera-streamer |
| Giao diện | Mainsail và KlipperScreen tiếng Việt |
| Slicer | Profile OrcaSlicer multi-tool trong `Orca Config/` |

## Quyền sở hữu thành phần

| Thành phần | Chủ sở hữu/nguồn sự thật | Trách nhiệm của repository |
| --- | --- | --- |
| Macro lõi KTC | `~/klipper-toolchanger-easy` | Kiểm tra và giữ nguyên sáu symlink readonly |
| Đường máy và tool KTC | All-Config | `toolchanger-config.cfg` và `tools/T0.cfg`…`T4.cfg` |
| Plugin Cartographer | Update Manager Cartographer | Chỉ quản lý geometry/mesh riêng của máy |
| Runtime ToolVision | `~/Tool-Vision`, Moonraker updater | Pin máy, UI wrapper và đường generated data |
| Klipper/Moonraker/Crowsnest | Updater upstream tương ứng | Payload `.cfg`/`.conf` riêng của máy |
| Kết quả sinh tự động | Runtime máy in | Giữ local; không bị ghi đè bởi `rsync --delete` |

Ranh giới quan trọng nhất là quyền sở hữu KTC-Easy. All-Config từ chối deploy
nếu một entry readonly bị thiếu, không phải symlink hoặc target bị hỏng.

## Tham khảo phần cứng và pin

### Mainboard, sensor và output

Giá trị lấy từ `config/Printer-Setup/hardware.cfg` và `fans-leds.cfg`.

| Chức năng | Gán đang hoạt động |
| --- | --- |
| CAN UUID MCU chính | `19b203d75137` |
| CAN UUID Cartographer | `da13d909ce34` |
| X step/direction/enable/endstop | `PE6` / `PE5` / `!PC14` / `PF0` |
| Y step/direction/enable/endstop | `PE2` / `PE1` / `!PE4` / `PF1` |
| Pin step Z0 | `PG9` |
| Pin step Z1 | `PB4` |
| Pin step Z2 | `PG13` |
| Pin step Z3 | `PB8` |
| Switch ToolVision | `^PF2` với GND |
| SSR bed / thermistor bed | `PA1` / `PB0` |
| Thermistor chamber | Generic 3950 tại `PB1` |
| TMC fan / CM4 fan / enclosure fan / bed fan | `PF9` / `PF6` / `PF7` / `PF8` |
| Dải WS2812 chamber | `PD15`, 40 LED, thứ tự GRB |

Các driver stepper X/Y/Z dùng run current `0.8 A`. Bed có giới hạn 120 °C.
`[verify_heater heater_bed]` dùng `check_gain_time: 240` vì máy từng gặp shutdown
giả theo tốc độ gia nhiệt liên quan tín hiệu thermistor bed nhiễu.

### Bố trí chung trên toolboard

Mỗi EBB dùng cùng pin logic với prefix `EBBn` tương ứng:

| Chức năng | Pin EBB |
| --- | --- |
| Extruder step/direction/enable | `PD0` / `!PD1` / `!PD2` |
| Heater / thermistor | `PB13` / `PA3` |
| Fan hotend / fan part | `PA0` / `PA1` |
| TMC2209 UART / run current | `PA15` / `0.6 A` |
| Phát hiện tool trên shuttle | `^!PB6` |
| Filament switch | `^PB9` |
| Ba LED trên tool | `PD3` |
| Chip-select ADXL345 | `PB12` |

Mỗi tool dùng nozzle 0.4 mm, filament 1.75 mm, gear ratio 50:10 và
max extrude-only distance 101 mm. Hotend tối đa 290 °C. Pressure Advance vẫn bị
comment vì đang chờ calibration riêng theo tool/vật liệu.

## Sơ đồ tool

### Nhận dạng, dock và hiệu chuẩn extrusion

Tọa độ dock là tọa độ nozzle và phải khớp dock thật phía sau máy. Không dùng
chúng làm mặc định an toàn cho máy khác.

| Tool | MCU | CAN UUID | Dock X/Y/Z (mm) | Rotation distance |
| --- | --- | --- | --- | ---: |
| T0 | EBB0 | `441e1484ac41` | `30.20 / 1.30 / 343` | `22.321` |
| T1 | EBB1 | `6475b5b9e028` | `104.00 / 1.10 / 343` | `22.500` |
| T2 | EBB2 | `4ad9d622a836` | `176.00 / 1.60 / 343` | `22.277` |
| T3 | EBB3 | `c2465b7c36f8` | `249.50 / 2.50 / 343` | `22.727` |
| T4 | EBB4 | `28650279df58` | `321.50 / 2.60 / 343` | `22.059` |

Thông số chuyển động KTC trong `toolchanger-config.cfg`: `safe_y: 120`,
`close_y: 30`, travel nhanh `15000 mm/min`, tốc độ dock path `900 mm/min`.
Mỗi tool parked có standby target 150 °C.

### Offset production đã thử nghiệm in

Người vận hành đánh giá first layer tốt về hình thức với các giá trị
`SAVE_CONFIG` sau. T0 là mốc tham chiếu.

| Tool | Offset X (mm) | Offset Y (mm) | Offset Z (mm) |
| --- | ---: | ---: | ---: |
| T0 | `0.000` | `0.000` | `0.000` |
| T1 | `-0.243` | `-0.252` | `+0.228` |
| T2 | `+0.746` | `+0.086` | `-0.295` |
| T3 | `+0.304` | `+0.449` | `-0.268` |
| T4 | `+0.041` | `+0.352` | `-0.014` |

Chạy `CHECK_OFFSETS` để đọc giá trị Klipper đang nạp mà không làm máy chuyển
động. Nguồn lưu authoritative là khối `SAVE_CONFIG` cuối
`config/printer.cfg`.

### Input Shaper riêng từng tool

KTC áp profile đã đo sau mỗi lần đổi tool. `_ACTIVE_INPUT_SHAPER` tránh gửi lại
profile giống nhau, đồng thời giảm log console lặp.

| Tool | Profile X | Profile Y |
| --- | --- | --- |
| T0 | `3hump_ei`, 98.6 Hz, damping 0.081 | `mzv`, 35.0 Hz, damping 0.076 |
| T1 | `mzv`, 54.2 Hz, damping 0.057 | `mzv`, 35.4 Hz, damping 0.090 |
| T2 | `ei`, 67.0 Hz, damping 0.068 | `ei`, 45.8 Hz, damping 0.151 |
| T3 | `mzv`, 53.0 Hz, damping 0.078 | `mzv`, 35.2 Hz, damping 0.073 |
| T4 | `mzv`, 54.0 Hz, damping 0.080 | `mzv`, 35.2 Hz, damping 0.108 |

Section `[input_shaper]` toàn cục là fallback T0 để Klipper nạp module.
`resonance_tester` hiện trỏ `adxl345 T4`; chỉ đổi sang tool đang gắn trong một
phiên calibration có người giám sát. ShakeTune giữ tối đa năm kết quả dưới
`Generated-Data/ShakeTune/`.

## Chuyển động, QGL và Cartographer

### Giới hạn chuyển động

| Tham số | Giá trị |
| --- | ---: |
| Tốc độ XY tối đa | `300 mm/s` |
| Gia tốc XY tối đa | `4000 mm/s²` |
| Tốc độ Z tối đa | `60 mm/s` |
| Gia tốc Z tối đa | `700 mm/s²` |
| Square-corner velocity | `5 mm/s` |

### Quad Gantry Level

Các điểm QGL là `(20,0)`, `(20,280)`, `(330,280)`, `(330,0)`, tốc độ
200 mm/s, năm lần retry và final retry tolerance `0.0075`. Khi gantry chưa được
apply, wrapper chạy một pass thô clearance cao, sau đó pass bình thường và home
Z cuối. `G32` xóa mesh, home, chạy QGL và park tại `X180 Y180 Z30`.

### Cartographer Touch và Scan

| Setting | Giá trị đang hoạt động |
| --- | --- |
| Offset probe | X `0`, Y `35` |
| Vùng mesh | X `20..320`, Y `45..325` |
| Số mẫu | `55 × 55` |
| Tốc độ mesh / Z ngang | `600 mm/s` / `3 mm` |
| Adaptive margin | `10 mm` |
| Zero reference position | tọa độ nozzle `174,168` |
| Touch threshold / speed / Z offset đã lưu | `1819` / `2` / `-0.05` |
| Version Cartographer đã lưu | software `1.8.0`, MCU `CARTOGRAPHER V3 6.1.0` |

Cartographer cố định trên shuttle và là probe production cho Z-home/bed mesh.
ToolVision đo offset tool tương đối; nó không thay Cartographer trong homing
bình thường trước khi in.

## Cấu trúc repository và config

```text
Voron 5 Tool/
├── README.md / README.vi.md       # Tham khảo chính Anh/Việt
├── config/                        # Payload active deploy lên máy
│   ├── printer.cfg                # Entry point, kinematics, SAVE_CONFIG
│   ├── mainsail.cfg               # Macro bundle Mainsail
│   ├── moonraker.conf             # API và Update Manager
│   ├── crowsnest.conf             # Stream camera MF-500
│   ├── KlipperScreen.conf         # Màn cảm ứng tiếng Việt
│   ├── Printer-Setup/
│   │   ├── calibration-probe.cfg  # Cartographer và routing calibration
│   │   ├── tool-vision.cfg        # ToolVision riêng máy và panel
│   │   ├── hardware.cfg           # MCU, stepper, bed, sensor
│   │   ├── fans-leds.cfg          # Fan, LED và RESUME override
│   │   ├── input-shaper.cfg       # Shaper fallback, resonance, ShakeTune
│   │   ├── nozzle-clean.cfg       # Vệ sinh bằng bucket/pad
│   │   ├── prime-lines.cfg        # Prime line multi-tool
│   │   ├── print-macros.cfg       # Vòng đời print và dryer
│   │   └── tool-crash.cfg         # Bảo vệ crash theo active tool
│   ├── toolchanger/
│   │   ├── toolchanger-config.cfg # Path máy và override KTC
│   │   ├── tools/T0.cfg ... T4.cfg
│   │   └── readonly-configs/      # Symlink do KTC-Easy sở hữu; không sửa
│   └── scripts/
│       ├── install.sh             # Preflight, backup, deploy bảo vệ
│       ├── update.sh              # Updater archive tạm từ main
│       ├── cleanup-voron.sh       # Dọn path legacy có kiểm tra chặt
│       └── patches/               # Patch runtime downstream đã review
├── Orca Config/                   # Profile machine/process/filament + sync
└── extras/
    ├── docs/                      # Hướng dẫn song ngữ hiện hành
    ├── Nhat-ky-chinh-sua/         # Nhật ký kỹ thuật append-only
    ├── backups/                   # Snapshot rollback bất biến theo Git
    ├── retired-configs/           # File không còn include
    └── Config download/           # Snapshot lịch sử tải về
```

### Thứ tự include đang hoạt động

`config/printer.cfg` nạp theo thứ tự:

1. `mainsail.cfg`
2. `toolchanger-include.cfg` của KTC-Easy
3. `Printer-Setup/calibration-probe.cfg`
4. `Printer-Setup/tool-vision.cfg`
5. `hardware.cfg`, `fans-leds.cfg`, `input-shaper.cfg`
6. `nozzle-clean.cfg`, `prime-lines.cfg`, `print-macros.cfg`
7. `tool-crash.cfg`

Thứ tự này có chủ ý. `tool-crash.cfg` nạp sau object tool của KTC. Axiscope và
`[tools_calibrate]` chỉ còn nội dung rollback đã comment/tắt; lệnh public legacy
raise lỗi rõ ràng thay vì gọi probe owner không tồn tại.

### Generated data riêng trên máy in

Installer giữ các đường dẫn sau qua `rsync --delete`:

```text
Generated-Data/ToolVision/state.json
Generated-Data/ToolVision/results.json
Generated-Data/ShakeTune/
```

Markdown, archive tải về, chẩn đoán local, JSON ToolVision legacy và symlink
readonly KTC cũng bị loại khỏi đồng bộ cấu hình.

## Quy trình in bình thường

### Hợp đồng Start G-code từ OrcaSlicer

Các machine profile đang theo dõi gọi:

```gcode
PRINT_START TOOL_TEMP={first_layer_temperature[initial_tool]} \
  T0_TEMP=... T1_TEMP=... T2_TEMP=... T3_TEMP=... T4_TEMP=... \
  BED_TEMP=[first_layer_bed_temperature] \
  TOOL=[initial_tool] MATERIAL={filament_type[initial_tool]}
```

Chỉ extruder được dùng mới phát `Tn_TEMP` dương. `PRINT_START` từ chối tool
không tồn tại, nhiệt độ tool đầu tiên không dương hoặc target bed không dương.

Tham số tùy chọn:

| Tham số | Ý nghĩa |
| --- | --- |
| `SOAK=<giây>` | Thời gian heat soak tường minh |
| `AUTO_SOAK=0` | Tắt soak tự động theo vật liệu/chênh nhiệt |
| `FULL_BED=1` | Báo job dùng toàn bed cho soak helper |
| `MATERIAL=<tên>` | Nhóm PLA/TPU/PETG/ABS/ASA/PC/NYLON/PA |

### Trình tự `PRINT_START`

1. Kiểm tra tool và temperature từ slicer.
2. Hủy delayed fan shutdown cũ và chuyển quyền bed/fan từ dryer đang chạy mà
   không tắt chúng trong chốc lát.
3. Xóa pause/mesh/offset state, initialize KTC và dừng crash detection.
4. Bắt đầu gia nhiệt bed và tool slicer dùng theo kiểu bất đồng bộ. T0 giữ ở
   150 °C cho Cartographer trong giai đoạn này.
5. Chạy full `G28` trước mọi toolchange rồi nâng Z an toàn.
6. Chọn T0 và chạy `CLEAN_NOZZLE TEMP=150 WIPES=5` trong lúc bed nóng lên.
7. Đợi bed, bật fan tuần hoàn dưới bed và chạy heat soak.
8. Chạy QGL ở nhiệt độ ổn định.
9. Vệ sinh T0 lần nữa ngay trước `CARTOGRAPHER_TOUCH_HOME`.
10. Tạo adaptive bed mesh.
11. Prime mọi tool slicer sử dụng; tool không phải initial trước, initial cuối.
12. Bật crash detection, đặt LED printing và thả job G-code đã slice.

Soak tự động khi bed lạnh:

| Vật liệu | Full cold soak |
| --- | ---: |
| PLA/TPU | 30 giây |
| PETG | 60 giây |
| ABS/ASA/PC/NYLON/PA | 90 giây |

Bed cách target không quá 5 °C sẽ bỏ qua soak tự động. Chênh 5–15 °C dùng 20%
thời gian đầy đủ. `SOAK=` luôn ghi đè thời gian tính tự động.

### Trình tự `PRINT_END`

1. Đặt print state về idle, reset speed, flow và Pressure Advance.
2. Dừng crash detection.
3. Nếu XYZ đã home và extruder active có thể extrude, retract tổng 10 mm theo
   hai giai đoạn và nâng Z.
4. Nâng ít nhất tới Z 50 mm, có giới hạn bởi trục Z tối đa.
5. Đặt target heater mọi tool về 0 và thả tool active.
6. Park shuttle rỗng phía sau, giữa X và cách Y tối đa 20 mm.
7. Reset G-code offset; tắt fan part và nhiệt bed, sau đó disable stepper
   extruder.
8. Hẹn tắt bed fan sau 180 giây, xóa mesh/pause và hiển thị Complete.

`PRINT_END` chủ ý để shuttle rỗng; không kết thúc với T0 đang gắn. Nếu XYZ chưa
home, macro bỏ qua retract/lift/toolchange/park nhưng vẫn cleanup phần không
chuyển động.

### Filament runout và tool crash

Mỗi tool có bộ lọc filament switch trễ 0.5 giây. Runout chỉ pause một bản in
active khi tool bị ảnh hưởng chính là active tool của KTC; cạnh từ tool parked
chỉ được báo, không pause. Đường `RESUME` tùy chỉnh initialize lại KTC, xác nhận
có tool và bật lại crash detection trước khi resume.

`tool_crash.py` được cài nhận patch idempotent của All-Config để kiểm tra trạng
thái active tool trước khi xem cạnh detection pin là crash. Installer backup
runtime chưa patch nhưng khớp source trước khi áp dụng và từ chối source
upstream không tương thích.

## Bảng macro vận hành

| Macro | Mục đích | Chuyển động/nhiệt |
| --- | --- | --- |
| `G32` | Home toàn bộ, chạy QGL, park X180 Y180 Z30 | Có |
| `QUAD_GANTRY_LEVEL` | QGL thô/tinh và home Z cuối | Có |
| `PRINT_START ...` | Chuẩn bị đầy đủ do slicer gọi | Có, gia nhiệt |
| `PRINT_END` | Retract, thả tool, park shuttle rỗng và cooldown | Có |
| `CLEAN_NOZZLE [TEMP=150] [WIPES=5]` | Gia nhiệt nếu cần, flick và scrub nozzle active | Có, có thể nóng |
| `PURGE_AND_CLEAN [PURGE=15] [PURGE_TEMP=200]` | Purge vào bucket, cooldown và scrub | Có, gia nhiệt |
| `PRIME_LINES INITIAL_TOOL=n Tn_TEMP=...` | Prime mọi tool được liệt kê, initial cuối | Có, gia nhiệt |
| `START_DRYER` | Mở prompt chọn vật liệu | Chỉ prompt trước khi chọn |
| `START_DRYER MATERIAL=PETG ...` | Bắt đầu chu trình sấy bed/chamber | Có, có thể home và nóng |
| `STOP_DRYER` | Dừng dryer và tắt heat/fan do dryer sở hữu | Không di chuyển XY |
| `DRYER_STATUS` | Báo cycle/thermal hiện tại | Không |
| `CALIBRATION_STATUS` | Báo backend/method calibration | Không |
| `CHECK_OFFSETS` | Báo offset XYZ T0–T4 đang nạp | Không |
| `TOOL_VISION` | Mở panel ToolVision | Chỉ prompt trước khi chọn action |
| `TOOL_VISION_STATUS` | Báo readiness/error ToolVision | Không |
| `QUERY_ENDSTOPS` | Đọc trạng thái endstop/switch | Không |
| `BED_FAN_ON [SPEED=0.5]` / `BED_FAN_OFF` | Điều khiển tuần hoàn chamber | Chỉ fan |
| `LIGHTS_ON` / `LIGHTS_OFF` | Đèn chamber ở mức an toàn đã cấu hình | Chỉ LED |
| `START_CRASH_DETECTION` / `STOP_CRASH_DETECTION` | Điều khiển watchdog active tool | Không chuyển động |

Các lệnh căn dock nâng cao `TOOL_ALIGN_START`, `TOOL_ALIGN_TEST` và
`TOOL_ALIGN_DONE` có thể làm máy di chuyển và lưu vĩnh viễn tọa độ dock. Chỉ
dùng trong quy trình căn chỉnh có người giám sát và đã backup.

Các lệnh legacy `CALIBRATE_MOVE_OVER_PROBE`, `CALIBRATE_ALL_OFFSETS` và
`CALIBRATE_NOZZLE_PROBE_OFFSET` bị `calibration-probe.cfg` tắt có chủ ý và sẽ
raise hướng dẫn chuyển sang ToolVision.

## Vệ sinh nozzle và prime line

### Hình học vệ sinh thực tế

| Thành phần | Tọa độ/setting |
| --- | --- |
| Purge bucket | X `320`, Y `-8` |
| Y tâm brush | `-8` |
| X bắt đầu flick | `307` |
| Vùng scrub X | `277..309` |
| Z vệ sinh / Z an toàn | `1.2` / `15` mm |
| Bán kính vòng scrub | `1.5` mm |

`CLEAN_NOZZLE` yêu cầu có active tool thật theo KTC. Macro có thể home XYZ nếu
cần, nâng Z trước khi đi, purge tùy chọn, flick theo số lần yêu cầu, scrub vòng
thuận/nghịch và quay về bucket tại Z an toàn.

Ví dụ:

```gcode
CLEAN_NOZZLE
CLEAN_NOZZLE WIPES=8 TEMP=230
PURGE_AND_CLEAN
PURGE_AND_CLEAN PURGE=20 PURGE_TEMP=250 TEMP=150 WIPES=6
```

Khi `PURGE>0`, nhiệt độ purge thực tế ít nhất 200 °C và không thấp hơn nhiệt độ
purge/clean yêu cầu. Sau đó macro dùng part fan hạ về nhiệt độ vệ sinh rồi mới
scrub.

### Hành vi prime line

Prime-line controller dùng tối đa 52 mm mỗi tool, ba pass tại Z `0.28`, extrusion
13.33 mm cho mỗi pass đủ chiều dài, gap 6 mm giữa slot tool và spacing 3 mm giữa
pass. Macro tự scale chiều dài/extrusion khi nhiều tool phải cùng fit, retract
tool không cuối 1.8 mm, tool cuối 0.6 mm và giữ initial tool đang gắn.

## Hệ thống sấy filament bằng bed

Gọi `START_DRYER` không tham số sẽ mở một prompt vật liệu trên Mainsail. Gọi kèm
tham số sẽ chạy trực tiếp. Controller từ chối printer đang starting, printing
hoặc paused trước mọi chuyển động/nhiệt.

| Vật liệu | Bed | Target chamber | Thời gian | Bed fan nền |
| --- | ---: | ---: | ---: | ---: |
| PLA/PLA+ | 50 °C | 40 °C | 240 phút | 40% |
| TPU/TPE | 60 °C | 45 °C | 300 phút | 40% |
| PETG | 70 °C | 55 °C | 240 phút | 50% |
| ABS | 90 °C | 65 °C | 240 phút | 60% |
| ASA | 90 °C | 65 °C | 240 phút | 60% |
| NYLON/PA | 100 °C | 70 °C | 360 phút | 70% |
| PC | 105 °C | 75 °C | 360 phút | 70% |
| CUSTOM | 55 °C | tắt | 240 phút | 40% |

Override nâng cao:

```gcode
START_DRYER MATERIAL=PETG BED=70 CHAMBER=55 TIME=240 FAN=0.50 PARK=1
START_DRYER MATERIAL=CUSTOM BED=60 TIME_HOURS=6 FAN=0.45 PARK=0
```

Override hỗ trợ: `BED`, `CHAMBER`, `TIME`, `TIME_HOURS`, `FAN`, `PARK`,
`HUMIDITY`, `TARGET_HUMIDITY`. Humidity chỉ được dùng khi một sensor extension
đã cài expose `.humidity`; thermistor chamber Generic 3950 hiện chỉ cho nhiệt
độ.

Với `PARK=1`, dryer có thể home, nâng ít nhất Z 200, dock active tool và park
tại X175 Y310 trước khi nóng. Airflow boost khi chamber lạnh, chạy moisture
flush 30 giây mỗi 20 phút và giảm bed/fan khi chamber quá nóng. `PRINT_START`
chuyển quyền sở hữu an toàn từ timer dryer đang chạy.

## ToolVision calibration chỉ báo cáo

### Tích hợp đang deploy trên máy

| Hạng mục | Giá trị hiện tại |
| --- | --- |
| Runtime checkout | `~/Tool-Vision` |
| Môi trường Python | `~/tool-vision-env` |
| Host service/API | `tool-vision.service`, cổng loopback `8085` |
| Config riêng máy | `Printer-Setup/tool-vision.cfg` |
| Switch vật lý | Manta `^PF2` |
| Learned state | `Generated-Data/ToolVision/state.json` |
| Kết quả mới nhất | `Generated-Data/ToolVision/results.json` |
| Bằng chứng runtime production | ToolVision `204ae4c`, báo `3.4.0-rc2` |

ToolVision là backend offset tool đang hoạt động. Axiscope và
`[tools_calibrate]` tiếp tục tắt. Panel gọn có hai action Z đặt tên rõ
`Physical switch` và `Cartographer Touch`, cùng `Latest results` và
`Advanced setup`. Mỗi action truyền `METHOD=` tường minh và kết quả luôn
report-only. Mọi entry point của panel chặn `printing/paused`; nút Close gọi
helper riêng thay vì lồng `RESPOND`.

Máy này bật `INITIALIZE_TOOLCHANGER` làm hook recovery KTC sau lỗi ToolVision.
Đây là setting riêng đã review, không phải default để sao chép sang máy khác.

Camera XY tồn tại trong ToolVision nhưng chưa ready ở status máy gần nhất và
file này không cấu hình camera source/name. Không xem camera XY là đường
calibration production đang hoạt động.

### Ý nghĩa kết quả

Dấu Z đã cài đặt:

```text
measured Z(tool) = raw contact Z(tool) - raw contact Z(reference T0)
```

Đây là giá trị absolute ứng viên tương đối T0, không phải residual delta để cộng
vào offset production đang cấu hình. ToolVision không ghi file production
T0–T4.

Ba lượt 150 °C cho mỗi phương pháp ngày 2026-08-25 có mean sau:

| Tool | Z production | PF2 mean (range) | Cartographer mean (range) |
| --- | ---: | ---: | ---: |
| T0 | +0.000 | +0.000 | +0.000 |
| T1 | +0.228 | +0.121 (+0.114..+0.130) | +0.243 (+0.238..+0.248) |
| T2 | -0.295 | -0.385 (-0.386..-0.384) | -0.268 (-0.270..-0.266) |
| T3 | -0.268 | -0.179 (-0.186..-0.164) | -0.186 (-0.196..-0.178) |
| T4 | -0.014 | +0.093 (+0.090..+0.096) | +0.105 (+0.102..+0.108) |

Năm lượt Cartographer bổ sung dùng `G28` đầy đủ riêng trước mỗi lượt, bàn giữ
ở target PETG `70 °C` và nozzle đo ở `150 °C`. Mean (range) là T1 `+0.2464`
(`0.024`), T2 `-0.2688` (`0.026`), T3 `-0.1896` (`0.010`) và T4 `+0.1028 mm`
(`0.020`). Mean từng tool chỉ đổi dưới `0.004 mm` so với bộ bàn nguội trước đó;
T0 return drift nằm trong `0.000..0.020 mm`. Cả năm history có
`cleanup_errors=[]`, `applied=false` và không đổi cấu hình.

### Canary UI và console

Nhánh `codex/compact-mainsail-output` tại `204ae4c` đã qua GitHub Security Gate
và HIL. Guard mới ngăn prompt/action ToolVision khi đang in hoặc pause. Một
dialog đã cache vẫn do KlipperScreen sở hữu và có thể cần refresh frontend sau
khi bản in kết thúc. Không lọc `action:prompt_*`, warning hoặc error bằng regex
vì đây là giao thức prompt và bằng chứng chẩn đoán.

Đọc [hướng dẫn tích hợp](extras/docs/toolvision-integration-guide.vi.md) và
[nhật ký 2026-08-25](extras/Nhat-ky-chinh-sua/2026-08-25-session-updates.md)
trước khi đổi runtime, station hoặc panel.

## Camera và giao diện người dùng

`crowsnest.conf` cấu hình MF-500 ở 1280×720, yêu cầu 30 fps, input MJPEG và
output camera-streamer/WebRTC. Device được chọn bằng đường
`/dev/v4l/by-id/...` ổn định. Power-line frequency đặt 50 Hz theo điện lưới địa
phương.

Máy từng quan sát MJPEG chỉ 15–20 fps khi host tải cao; WebRTC
`/webcam/webrtc` là workaround đã ghi nhận. 1080p/1440p từng tạo màn hình đen,
nên 1280×720 vẫn là setting ổn định được tài liệu hóa.

Mainsail là web UI chính. KlipperScreen dùng tiếng Việt. ToolVision, dryer và
các thao tác phức tạp expose một macro nhìn thấy để mở prompt; helper có tên bắt
đầu `_` là nội bộ.

## Profile OrcaSlicer

`Orca Config/` chứa ba JSON machine, bốn process và 15 filament. Danh sách chính
xác và cách restore nằm trong [`Orca Config/README.vi.md`](Orca%20Config/README.vi.md).

Hai đường đồng bộ có chủ ý khác nhau:

```powershell
# Mặc định chỉ review: không diagnostic, commit hoặc push nếu không yêu cầu.
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File ".\Orca Config\Sync-OrcaProfiles.ps1"

# Wrapper nhấp đúp: diagnostic + scoped commit + push.
.\Orca Config\Sync-OrcaProfiles.cmd
```

PowerShell script chọn Orca user profile sửa gần nhất nếu không truyền
`-ProfileId`, kiểm tra mọi JSON, từ chối tên phẳng trùng, chỉ copy file đổi,
backup destination bị thay, ghi journal ngày và chỉ stage đường do đồng bộ sở
hữu khi dùng `-Commit`. `-Push` tự bật `-Commit`.

## Cài đặt và cập nhật

### Điều kiện trước

1. Printer idle, không paused hoặc calibrating.
2. KTC-Easy đã cài và sáu symlink readonly hợp lệ.
3. Checkout ToolVision, venv, service và năm symlink extension Klipper tồn tại
   vì config active đang include ToolVision.
4. Config hiện tại và generated calibration data có backup dùng được.
5. Operator sẵn sàng đọc output và restart service thủ công.

### Cài All-Config lần đầu mà không giữ clone

```bash
tmp_dir="$(mktemp -d /tmp/all-config-voron.XXXXXX)"
curl -fsSL https://github.com/IDcrazy123/All-Config-Voron/archive/refs/heads/main.tar.gz \
  | tar -xz -C "${tmp_dir}" --strip-components=1
bash "${tmp_dir}/config/scripts/install.sh"
rm -rf -- "${tmp_dir}"
sudo systemctl restart moonraker klipper
```

Git checkout All-Config không được giữ trên CM4. Checkout runtime ToolVision và
KTC-Easy là riêng biệt và phải tồn tại vì service, symlink và Update Manager
dùng trực tiếp chúng.

### Cập nhật All-Config bình thường

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

`update.sh` tạo thư mục tạm, tải archive `main` bằng `curl` hoặc `wget`, kiểm tra
có `config/printer.cfg`, gọi `install.sh` và xóa source tạm bằng trap.

`install.sh` sau đó:

1. Kiểm tra quyền sở hữu readonly của KTC-Easy.
2. Kiểm tra runtime/service/module link ToolVision.
3. Dry-run hoặc nhận biết patch `tool_crash.py` đã review.
4. Copy toàn bộ config máy hiện tại vào
   `~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/`.
5. Chạy `rsync --delete` có exclude runtime/generated/readonly.
6. Chỉ backup và áp patch tool-crash khi cần.
7. In đường dẫn backup và yêu cầu operator review trước restart.

Hai script không tự restart Moonraker/Klipper. Sau khi review deploy thành công:

```bash
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

### Kiểm tra sau update không chủ động chuyển động

Trên host:

```bash
systemctl is-active klipper moonraker crowsnest tool-vision
curl --fail --silent http://127.0.0.1:8085/api/v2/health
```

Trong Mainsail:

```text
CALIBRATION_STATUS
CHECK_OFFSETS
QUERY_ENDSTOPS
TOOL_VISION_STATUS
DRYER_STATUS
```

Mong đợi: Klipper ready, printer idle, ToolVision không busy, PF2 thường open,
heater target 0 và không có last error chưa giải thích. Các kiểm tra này không
chủ động home, probe hoặc chọn tool.

## Backup, rollback và dọn dẹp

### Vị trí backup

| Loại backup | Vị trí |
| --- | --- |
| Snapshot theo task trong repository | `extras/backups/pre-<task>-YYYYMMDD-HHMMSS/` |
| Snapshot config tự động trên máy | `~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/` |
| State/result ToolVision | `Generated-Data/ToolVision/` cộng bản off-device riêng trước khi đổi runtime/schema |

Snapshot backup được theo dõi và journal ngày là evidence bất biến. Không sửa
README backup cũ để mô tả hệ thống mới. Chỉ mục song ngữ liên kết ba rollback
point gần đây mà không thay nội dung chúng.

### Nguyên tắc rollback

1. Dừng khi printer idle và tạo thêm backup trạng thái hiện tại.
2. Xác định config, runtime revision và generated-data schema tương ứng.
3. Chỉ restore file mục tiêu; không thay mù quáng
   `Generated-Data/ToolVision/` trong rollback chỉ liên quan config.
4. Kiểm tra config/JSON, restart service có kiểm soát và chạy kiểm tra không
   chuyển động trước.
5. Ghi rollback vào journal ngày.

### Phạm vi cleanup script

`config/scripts/cleanup-voron.sh` mặc định dry-run:

```bash
bash ~/printer_data/config/scripts/cleanup-voron.sh
bash ~/printer_data/config/scripts/cleanup-voron.sh --apply
```

Script chỉ liệt kê/xóa đường legacy đã kiểm tra chặt khớp
`printer_data/config.update-backup-*`, `printer_data/config.backup-*` và
`~/axiscope.bak`. Nó không tự áp retention cho `config_backups/` bình thường.
Đọc từng đường dẫn được in trước `--apply`.

## Xử lý sự cố

| Triệu chứng | Kiểm tra đầu tiên | Hướng an toàn |
| --- | --- | --- |
| Klipper báo `Unknown section 'tool_vision'` | Năm symlink `tool_vision*.py` và checkout ToolVision | Sửa runtime, rồi restart Klipper lúc idle |
| All-Config từ chối KTC readonly | Sáu entry dưới `toolchanger/readonly-configs/` | Chạy `bash ~/klipper-toolchanger-easy/install.sh` lúc idle; không chép file thường vào đó |
| `ToolVision switch` triggered khi không chạm | Wiring PF2, pull-up/inversion và switch cơ khí | Dừng calibration; đọc `QUERY_ENDSTOPS` trước chuyển động |
| Setup/result ToolVision có vẻ mất | `Generated-Data/ToolVision/state.json` và `results.json` | Giữ file/log; không tạo JSON placeholder hoặc teach lại ngay |
| Result PF2 biến mất sau run Cartographer | Runtime hiện chỉ có một latest `results.json` | Dùng console/journal theo ngày; history mới chỉ ở nhánh UX chưa deploy |
| Cartographer lỗi sau restart | `klippy.log`, nhiệt Cartographer và trạng thái `can0` | Thu evidence trước power-cycle; không xem giả thuyết CAN cũ là kết luận |
| Bed báo sai tốc độ gia nhiệt | Wiring thermistor/SSR và nhiệt tăng thực tế | Dừng nếu nhiệt bất thường; không nới `[verify_heater]` khi chưa có evidence |
| Detection pin pause sai | Active KTC tool, pin detection và patch marker | Giữ log; kiểm tra tương thích patch thay vì tắt bảo vệ |
| Camera đen ở 1080p/1440p | Resolution/service Crowsnest | Quay về 1280×720 WebRTC đã tài liệu hóa |
| Dryer không chạy | Print/pause state và range override | Kết thúc/cancel print an toàn; sửa tham số thay vì bypass guard |
| `CLEAN_NOZZLE` báo không có active tool | `printer.toolchanger.tool_number` | Initialize/chọn tool chỉ sau khi kiểm tra home/clearance an toàn |
| Mainsail Config Files có dòng duplicate cũ | Filesystem thật và cache trình duyệt | Refresh/hard-refresh Mainsail; không xóa file chỉ vì ghost UI |

Các lệnh log hữu ích trên host:

```bash
journalctl -u klipper -n 100 --no-pager
journalctl -u moonraker -n 100 --no-pager
journalctl -u tool-vision -n 100 --no-pager
journalctl -u crowsnest -n 100 --no-pager
```

Không đăng camera URL riêng, credential hoặc toàn bộ config private chưa
redact lên issue công khai.

## Giới hạn hiện tại và công việc chờ

- ToolVision vẫn là development canary chỉ báo cáo. UI method/history cải tiến
  đã cài trên feature branch nhưng chưa deploy/HIL ở đây.
- Camera XY ToolVision chưa phải đường calibration production active.
- Pressure Advance chưa calibration riêng theo tool/vật liệu.
- Hành vi cooling riêng từng tool vẫn chờ review.
- Cảnh báo/giám sát nhiệt Cartographer bổ sung vẫn đang chờ.
- `cleanup-voron.sh` không có chính sách “giữ N bản mới nhất” cho backup
  installer bình thường.
- Runtime ToolVision hiện chỉ giữ latest result.
- Chế độ MF-500 ổn định được tài liệu hóa là 1280×720 WebRTC, không phải
  resolution danh nghĩa cao nhất.

Xem `.agents/TODO.md` và `.agents/KNOWN_ISSUES.md` ở workspace cha để biết danh
sách task/sự cố được duy trì.

## Sơ đồ tài liệu

| Tài liệu | English | Tiếng Việt |
| --- | --- | --- |
| Tham khảo hệ thống chính | [README](README.md) | [README](README.vi.md) |
| Payload config active | [Config README](config/README.md) | [Config README](config/README.vi.md) |
| Vận hành StealthChanger | [Hướng dẫn](extras/docs/huong-dan-he-thong-stealthchanger.en.md) | [Hướng dẫn](extras/docs/huong-dan-he-thong-stealthchanger.md) |
| Tích hợp ToolVision | [Hướng dẫn](extras/docs/toolvision-integration-guide.en.md) | [Hướng dẫn](extras/docs/toolvision-integration-guide.vi.md) |
| Evidence/trạng thái UX ToolVision | [Báo cáo](extras/docs/toolvision-z-calibration-ux-proposal.md) | [Báo cáo](extras/docs/toolvision-z-calibration-ux-proposal.vi.md) |
| Profile OrcaSlicer | [README](Orca%20Config/README.md) | [README](Orca%20Config/README.vi.md) |
| Chính sách docs/history | [Chỉ mục](extras/docs/README.md) | [Chỉ mục](extras/docs/README.vi.md) |

Journal lịch sử, file retired, snapshot tải về và nội dung backup giữ bằng chứng
theo ngày của chúng. Dùng tài liệu hiện hành bên trên để hiểu hành vi hiện tại.

## Quy trình đóng góp an toàn

1. Đọc file active và quy tắc project áp dụng trước khi sửa.
2. Giữ thay đổi người dùng không liên quan và generated data riêng của máy.
3. Backup mọi `.cfg`, `.conf` hoặc `.sh` sẽ thay.
4. Thực hiện thay đổi nhỏ nhất có source; không đoán giá trị phần cứng.
5. Kiểm tra cú pháp Klipper, shell và hợp đồng include/path liên quan.
6. Cập nhật cả tài liệu English và Tiếng Việt khi hành vi hoặc đường dẫn đổi.
7. Bổ sung journal kỹ thuật theo ngày.
8. Chỉ stage file của task, commit message tiếng Anh và push `main` khi được
   phép.

Repository là hạ tầng production. Một thay đổi chỉ hoàn tất khi source, tài
liệu, backup, kiểm tra và đường rollback thống nhất với nhau.

# Cấu hình production Voron 2.4 StealthChanger năm tool

[English](README.md) | [Tiếng Việt](README.vi.md) | [Chỉ mục tài liệu](extras/docs/README.vi.md) | [Tham khảo config đang hoạt động](config/README.vi.md)

Repository này chứa cấu hình production đã review, script triển khai, profile
OrcaSlicer và tài liệu vận hành cho một máy Voron 2.4 CoreXY 350 mm cụ thể với
năm tool StealthChanger. Đây không phải cấu hình mẫu có thể chép trực tiếp sang
máy khác.

> [!IMPORTANT]
> Mã phần cứng, giới hạn chuyển động, tọa độ dock và offset trong tài liệu là
> giá trị riêng của máy này. Hãy đọc file source được nêu cạnh từng giá trị
> trước khi áp dụng cho máy khác. Tích hợp calibration được đọc lại ngày
> 2026-08-31 theo commit upstream kTAMV `72421f2`.

## Bắt đầu từ đây

| Tôi muốn… | Đọc hoặc chạy |
| --- | --- |
| Hiểu tổng thể máy | [Tổng quan hệ thống](#tổng-quan-hệ-thống) và [sơ đồ tool](#sơ-đồ-tool) |
| Chuẩn bị một bản in bình thường | [Quy trình in bình thường](#quy-trình-in-bình-thường) |
| Tìm lệnh Mainsail/Klipper | [Bảng macro vận hành](#bảng-macro-vận-hành) |
| Xem offset đang nạp mà không chuyển động | `CHECK_OFFSETS` |
| Xem backend calibration đang hoạt động | `CALIBRATION_STATUS` |
| Đối chiếu offset XY bằng kTAMV | [kTAMV đối chiếu XY có giám sát](#ktamv-đối-chiếu-xy-có-giám-sát) |
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

- Không deploy, home, probe, căn dock, đổi tool hoặc chạy lệnh kTAMV có chuyển động khi đang in.
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
| Chẩn đoán offset tool | kTAMV camera chỉ đối chiếu X/Y; không có backend tool-offset Z active |
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
| Runtime kTAMV | Checkout `~/kTAMV` được pin, cập nhật thủ công | Camera URL, service port và các patch runtime đã review |
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
| Switch offset không active | `^PF2` với GND; giữ phần cứng nhưng kTAMV không dùng |
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
max extrude-only distance 101 mm. Hotend tối đa 290 °C. Pressure Advance được
hiệu chuẩn và quản lý động theo từng profile filament trong OrcaSlicer (theo dõi tại
`Orca Config/`) thông qua lệnh `SET_PRESSURE_ADVANCE` khi đổi tool/nhựa.

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
kTAMV chỉ đối chiếu X/Y bằng camera; nó không thay Cartographer và không đo Z
giữa các tool.

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
│   │   ├── ktamv.cfg              # Tích hợp kTAMV XY được pin và giám sát
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
4. `Printer-Setup/ktamv.cfg`
5. `hardware.cfg`, `fans-leds.cfg`, `input-shaper.cfg`
6. `nozzle-clean.cfg`, `prime-lines.cfg`, `print-macros.cfg`
7. `tool-crash.cfg`

Thứ tự này có chủ ý. `tool-crash.cfg` nạp sau object tool của KTC. Axiscope và
`[tools_calibrate]` chỉ còn nội dung rollback đã comment/tắt; lệnh public legacy
raise lỗi rõ ràng thay vì gọi probe owner không tồn tại.

### Generated data riêng trên máy in

Installer giữ các đường dẫn sau qua `rsync --delete`:

```text
Generated-Data/ShakeTune/
```

Markdown, archive tải về, chẩn đoán local và symlink readonly KTC cũng bị loại
khỏi đồng bộ cấu hình. Dữ liệu ToolVision đã retired được archive trước khi gỡ
và không còn trong cây config active.

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
| `KTAMV_STATUS` | Báo camera calibration, mm/pixel và origin | Không |
| `KTAMV_SETUP` | Gửi camera URL/options sang server | Không |
| `KTAMV_SIMPLE_NOZZLE_POSITION` | Nhận diện ảnh mà không jog | Không |
| `KTAMV_CALIB_CAMERA` | Calibrate camera bằng pattern mười điểm XY | Có |
| `KTAMV_FIND_NOZZLE_CENTER` | Nhận diện và jog X/Y về tâm camera | Có |
| `KTAMV_MEASURE_ACTIVE_TOOL_XY SAMPLES=3` | Đo ba residual XY, báo mean/spread | Có |
| `KTAMV_APPLY_ACTIVE_TOOL_XY` | Stage mean cuối vào offset XY của active tool | Không |
| `QUERY_ENDSTOPS` | Đọc trạng thái endstop/switch | Không |
| `BED_FAN_ON [SPEED=0.5]` / `BED_FAN_OFF` | Điều khiển tuần hoàn chamber | Chỉ fan |
| `LIGHTS_ON` / `LIGHTS_OFF` | Đèn chamber ở mức an toàn đã cấu hình | Chỉ LED |
| `START_CRASH_DETECTION` / `STOP_CRASH_DETECTION` | Điều khiển watchdog active tool | Không chuyển động |

Các lệnh căn dock nâng cao `TOOL_ALIGN_START`, `TOOL_ALIGN_TEST` và
`TOOL_ALIGN_DONE` có thể làm máy di chuyển và lưu vĩnh viễn tọa độ dock. Chỉ
dùng trong quy trình căn chỉnh có người giám sát và đã backup.

`CALIBRATE_ALL_OFFSETS` nguyên bản thuộc KTC `tools_calibrate` và dùng station
SexBolt/SexBall để đo XYZ; nó không phải lệnh ToolVision. Cả lệnh này,
`CALIBRATE_MOVE_OVER_PROBE` và `CALIBRATE_NOZZLE_PROBE_OFFSET` đang bị
`calibration-probe.cfg` tắt; dùng lệnh `KTAMV_*` riêng cho camera XY.

## Vệ sinh nozzle và prime line

### Hình học và thông số hệ thống vệ sinh đầu in trên tấm PEI

`CLEAN_NOZZLE` (kèm alias `CLEAR_NOZZLE`) triển khai quy trình vệ sinh đầu in trực tiếp trên mép trước của tấm bàn in PEI:
1. **Ép dính & Xoay tròn trên PEI (PEI Bed Rub):** Nozzle ở $Z = 0.1\text{mm}$ quét zíc-zắc chậm ($F200$) kết hợp 21 vòng xoay cung tròn $G2$ ($F600$) tại $X = 130 \dots 140, Y = 5 \dots 8$ để màng nhựa mềm bám dính chặt và bóc sạch khỏi vát đầu phun.
2. **Miết mép & Gạt flick nhanh (Edge Flick):** Di chuyển ra mép tấm thép PEI ($Z = -0.8\text{mm}$, $X = 164 \dots 180$) quét tốc độ vừa ($F2000$ tại $Y=3$) và gạt flick tốc độ cực cao ($F12000$ tại $Y=1$) để giật đứt hoàn toàn tơ nhựa thừa.

| Thông số / Khu vực | Giá trị mặc định | Mô tả |
| --- | --- | --- |
| `variable_safe_z` | `10.0 mm` | Độ cao Z an toàn khi di chuyển |
| `variable_travel_speed` | `12000 mm/min` | Tốc độ di chuyển XY nhanh |
| `variable_approach_x` | `125.0` | Tọa độ X tiếp cận ban đầu |
| `variable_rub_start_x` / `end_x` | `130.0` / `140.0` | Phạm vi quét X trên tấm PEI |
| `variable_rub_y1` / `y2` / `y3` | `5.0` / `6.0` / `8.0` | 3 đường tọa độ Y trên tấm PEI |
| `variable_rub_z` / `slow_speed` | `0.1 mm` / `200 mm/min` | Độ cao Z tiếp xúc PEI và tốc độ quét chậm |
| `variable_rub_swirl_count` / `speed` | `21` / `600 mm/min` | Số vòng xoay tròn G2 và tốc độ xoay |
| `variable_flick_start_x` / `end_x` | `164.0` / `180.0` | Phạm vi quét X miết mép bàn |
| `variable_flick_y_med` / `y_fast` | `3.0` / `1.0` | Tọa độ Y đường gạt vừa và flick nhanh |
| `variable_flick_z` / `hop_z` | `-0.8 mm` / `0.5 mm` | Độ sâu Z miết mép và độ nhấc Z |
| `variable_flick_med_speed` / `fast_speed` | `2000` / `12000 mm/min` | Tốc độ miết vừa và gạt flick nhanh |

`CLEAN_NOZZLE` yêu cầu có active tool thật theo KTC. Macro tự động nâng Z trước khi đi,
thực hiện chà PEI, gạt mép 2 cấp tốc độ và trở về Z an toàn.

Ví dụ:

```gcode
CLEAN_NOZZLE                          ; Chạy chu trình chà PEI chuẩn
CLEAR_NOZZLE                          ; Gọi qua tên alias
CLEAN_NOZZLE TEMP=150                 ; Gia nhiệt đầu in 150 C trước khi chà
CLEAN_NOZZLE SKIP_SWIRL=1             ; Chỉ gạt mép
CLEAN_NOZZLE SKIP_FLICK=1             ; Chỉ chà xoay trên mặt PEI
CLEAN_NOZZLE RUB_Z=0.1 FLICK_Z=-0.8   ; Ghi đè Z tạm thời
```

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

## kTAMV đối chiếu XY có giám sát

### Tích hợp đang deploy trên máy

| Hạng mục | Giá trị hiện tại |
| --- | --- |
| Upstream | [TypQxQ/kTAMV](https://github.com/TypQxQ/kTAMV), pin commit `72421f2` |
| Runtime checkout | `~/kTAMV` cùng các bản sửa detector, lọc calibration và đo XY lặp |
| Môi trường Python | `~/ktamv-env`, dùng OpenCV package hệ thống |
| Host service/API | user service `ktamv-server.service`, cổng `8086` |
| Config riêng máy | `Printer-Setup/ktamv.cfg` |
| Camera nguồn | `http://127.0.0.1/webcam/?action=snapshot` |
| Upload ảnh cloud | tắt |

kTAMV chỉ active như backend đối chiếu có người giám sát. Nó calibrate biến đổi
camera–chuyển động, đưa nozzle nhìn thấy về tâm và báo chênh X/Y raw so với
origin tham chiếu. Nó không đo Z, không ghi file tool và mất transform/origin
sau khi Klipper restart.

### Đối chiếu phương pháp

| Hành vi | kTAMV | Tích hợp ToolVision đã retired |
| --- | --- | --- |
| Trục | Chỉ X/Y | Camera X/Y cộng Z bằng PF2 hoặc Cartographer Touch |
| Setup | Gửi server config, calibrate camera, đặt origin T0 thủ công | Setup station/provider có hướng dẫn |
| Lưu trạng thái | Chỉ RAM; mất sau Klipper restart | State/result/history trên ổ đĩa |
| Áp offset | Chỉ báo số để operator ghi | Máy này cũng dùng report-only |
| Detector | Pipeline OpenCV cố định trên ảnh resize 640×480 | Profile học ở native resolution và kiểm tra ambiguity |
| Chuỗi tool | Operator tự chọn/jog từng tool | Batch năm tool và kiểm tra restore tích hợp |
| Bề mặt an toàn | Lệnh native có thể jog ngay | Prompt guard, full-home và cleanup/recovery |
| Khả năng Z | Không có | So sánh switch và Cartographer Touch |

Lần thử kTAMV ngày 2026-08-22 với MF-500 này thất bại camera calibration: chỉ
6/10 điểm hợp lệ, vùng phản xạ sáng bị chọn gần lỗ nozzle thật và ảnh 1280×720
bị kéo thành 640×480. Bằng chứng vẫn còn giá trị vì HEAD upstream chưa đổi. Không
nới `detection_tolerance` để ép một cảnh mơ hồ pass; hãy sửa focus, khoảng cách,
ánh sáng mềm và độ sạch nozzle trước.

### Ranh giới sử dụng

Các lệnh không chuyển động gồm `KTAMV_SETUP`, `KTAMV_STATUS`,
`KTAMV_SEND_SERVER_CFG`, bật/tắt preview, `KTAMV_SIMPLE_NOZZLE_POSITION`,
`KTAMV_SET_ORIGIN`, `KTAMV_GET_OFFSET` và `KTAMV_APPLY_ACTIVE_TOOL_XY`.
`KTAMV_CALIB_CAMERA`, `KTAMV_FIND_NOZZLE_CENTER` và
`KTAMV_MEASURE_ACTIVE_TOOL_XY` đều có chuyển động. Chúng yêu cầu home đầy đủ,
operator đứng tại máy và sẵn emergency stop.

Dùng T0 với offset X/Y bằng 0 làm reference: setup server, preview/kiểm tra nhận
diện, calibrate camera, đưa T0 về tâm, đặt origin đúng một lần; sau đó chọn từng
T1–T4 và chạy `KTAMV_MEASURE_ACTIVE_TOOL_XY SAMPLES=3`. Review mean/spread,
chạy `KTAMV_APPLY_ACTIVE_TOOL_XY` riêng cho từng tool rồi `SAVE_CONFIG` một lần.
Xem tài liệu song ngữ
[sử dụng kTAMV và đối chiếu phương pháp](extras/docs/ktamv-usage-comparison.vi.md).

## Camera và giao diện người dùng

`crowsnest.conf` cấu hình MF-500 ở 1280×720, yêu cầu 30 fps, input MJPEG và
output camera-streamer/WebRTC. Device được chọn bằng đường
`/dev/v4l/by-id/...` ổn định. Power-line frequency đặt 50 Hz theo điện lưới địa
phương.

Máy từng quan sát MJPEG chỉ 15–20 fps khi host tải cao; WebRTC
`/webcam/webrtc` là workaround đã ghi nhận. 1080p/1440p từng tạo màn hình đen,
nên 1280×720 vẫn là setting ổn định được tài liệu hóa.

Mainsail là web UI chính. KlipperScreen dùng tiếng Việt. kTAMV dùng lệnh native
trực tiếp thay vì prompt có guard; phải đọc bảng chuyển động trước khi gọi.
Dryer và các thao tác phức tạp khác vẫn dùng prompt wrapper.

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
3. Checkout kTAMV được pin, venv, user service và hai symlink extension Klipper
   chính xác tồn tại vì config active đang include kTAMV.
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

Git checkout All-Config không được giữ trên CM4. Checkout runtime kTAMV được pin
và KTC-Easy là riêng biệt vì owner service/symlink nằm ngoài payload config.
kTAMV không tự update khi còn patch local.

### Cập nhật All-Config bình thường

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

`update.sh` tạo thư mục tạm, tải archive `main` bằng `curl` hoặc `wget`, kiểm tra
có `config/printer.cfg`, gọi `install.sh` và xóa source tạm bằng trap.

`install.sh` sau đó:

1. Kiểm tra quyền sở hữu readonly của KTC-Easy.
2. Kiểm tra runtime kTAMV được pin, user service, module link và các patch runtime.
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
systemctl is-active klipper moonraker crowsnest
systemctl --user is-active ktamv-server
curl --fail --silent http://127.0.0.1:8086/
```

Trong Mainsail:

```text
CALIBRATION_STATUS
CHECK_OFFSETS
QUERY_ENDSTOPS
KTAMV_STATUS
DRYER_STATUS
```

Mong đợi: Klipper ready, printer idle, service kTAMV active, heater target 0 và
không có lỗi server chưa giải thích. Các kiểm tra này không
chủ động home, probe hoặc chọn tool.

## Backup, rollback và dọn dẹp

### Vị trí backup

| Loại backup | Vị trí |
| --- | --- |
| Snapshot theo task trong repository | `extras/backups/pre-<task>-YYYYMMDD-HHMMSS/` |
| Snapshot config tự động trên máy | `~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/` |
| Snapshot gỡ ToolVision | `pre-replace-toolvision-with-ktamv-20260831-113047/` trên repository và CM4 |

Snapshot backup được theo dõi và journal ngày là evidence bất biến. Không sửa
README backup cũ để mô tả hệ thống mới. Chỉ mục song ngữ liên kết ba rollback
point gần đây mà không thay nội dung chúng.

### Nguyên tắc rollback

1. Dừng khi printer idle và tạo thêm backup trạng thái hiện tại.
2. Xác định config, runtime revision và generated-data schema tương ứng.
3. Chỉ restore file mục tiêu; giữ dữ liệu ToolVision đã retired trong archive có
   ngày trừ khi rollback rõ ràng về tích hợp đó.
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
| Klipper báo `Unknown config object 'ktamv'` | Hai symlink `ktamv*.py` và checkout đã pin | Sửa link đã review, rồi restart Klipper lúc idle |
| All-Config từ chối KTC readonly | Sáu entry dưới `toolchanger/readonly-configs/` | Chạy `bash ~/klipper-toolchanger-easy/install.sh` lúc idle; không chép file thường vào đó |
| kTAMV báo `Camera URL not set` | Trạng thái config server | Chạy `KTAMV_SETUP`; lệnh này không di chuyển máy |
| kTAMV không thấy nozzle | Ảnh raw/processed, focus, ánh sáng, độ sạch | Sửa cảnh quang học; không tăng tolerance để nhận blob giả |
| Camera calibration mất hơn 25% điểm | Frame xử lý và độ phân tán mm/pixel | Dừng đối chiếu; không tiếp tục căn tâm/lấy offset |
| Calibration/origin biến mất | Lịch sử restart Klipper | Bình thường: kTAMV chỉ giữ RAM; setup lại có giám sát |
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
journalctl --user -u ktamv-server -n 100 --no-pager
journalctl -u crowsnest -n 100 --no-pager
```

Không đăng camera URL riêng, credential hoặc toàn bộ config private chưa
redact lên issue công khai.

## Giới hạn hiện tại và công việc chờ

- Upstream kTAMV chưa đổi từ năm 2024 và lần thử MF-500 trước thất bại vì cảnh
  có nhiều vật thể/phản xạ giống nozzle.
- kTAMV không lưu calibration, không có batch statistic, không đo Z và không tự
  lưu offset.
- Hành vi cooling riêng từng tool vẫn chờ review.
- Cảnh báo/giám sát nhiệt Cartographer bổ sung vẫn đang chờ.
- `cleanup-voron.sh` không có chính sách “giữ N bản mới nhất” cho backup
  installer bình thường.
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
| Sử dụng kTAMV và đối chiếu phương pháp | [Hướng dẫn](extras/docs/ktamv-usage-comparison.en.md) | [Hướng dẫn](extras/docs/ktamv-usage-comparison.vi.md) |
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

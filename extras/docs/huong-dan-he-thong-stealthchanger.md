# Hướng dẫn vận hành hệ thống StealthChanger năm tool

[Tiếng Việt](huong-dan-he-thong-stealthchanger.md) | [English](huong-dan-he-thong-stealthchanger.en.md)

Tài liệu được làm mới ngày 2026-08-31 sau khi đọc toàn bộ Markdown, config active,
source kTAMV và script triển khai. Nhật ký lịch sử không được viết lại thành
hiện trạng mới.

## 1. Ranh giới sở hữu

- KTC-Easy sở hữu `toolchanger/readonly-configs/` và sáu symlink do installer
  của nó tạo. Không sửa các file này trong All-Config.
- All-Config sở hữu `toolchanger-config.cfg`, `tools/T0.cfg`…`T4.cfg` và các
  override trong `Printer-Setup/`.
- Cartographer đang hoạt động cho Z homing và bed mesh.
- kTAMV đang hoạt động để đối chiếu X/Y bằng camera có người giám sát.
- Axiscope và `[tools_calibrate]` đã tắt, chỉ giữ comment để rollback.
- Không có backend tool-offset Z active; PF2 còn phần cứng nhưng kTAMV không dùng.

## 2. Include và thứ tự override

Thứ tự đang nạp trong `printer.cfg` là:

```text
mainsail.cfg
KTC-Easy readonly toolchanger include
calibration-probe.cfg
ktamv.cfg
hardware.cfg
fans-leds.cfg
input-shaper.cfg
nozzle-clean.cfg
prime-lines.cfg
print-macros.cfg
filament-dryer.cfg
test-speed.cfg
tool-crash.cfg
```

`tool-crash.cfg` nằm sau tool definitions để hook active-tool detection vào
đúng object KTC. Không thay thứ tự chỉ để “gọn” nếu chưa kiểm tra hành vi
override và parser Klipper.

## 3. Tool và toolchange

T0–T4 đều dùng EBB36, detection pin `^!EBBn:PB6`, run current extruder `0.6 A`
và thermistor Generic 3950. Dock được đặt ở Z `343 mm`:

| Tool | Dock X | Dock Y | Rotation distance |
| --- | ---: | ---: | ---: |
| T0 | 30.20 | 1.30 | 22.321 |
| T1 | 104.00 | 1.10 | 22.500 |
| T2 | 176.00 | 1.60 | 22.277 |
| T3 | 249.50 | 2.50 | 22.727 |
| T4 | 321.50 | 2.60 | 22.059 |

`toolchanger-config.cfg` dùng `safe_y: 120`, `close_y: 30`, tốc độ nhanh
`15000 mm/min` và tốc độ path `900 mm/min`. `require_tool_present` là `False`,
nhưng `tool-crash.cfg` vẫn kiểm tra detection pin, định tuyến qua KTC và pause
an toàn khi đang in. Safe pause không tự di chuyển XYZ.

Đổi input shaper chỉ phát lệnh khi target khác profile đang active, nhờ biến
`_ACTIVE_INPUT_SHAPER`; cách này giảm log lặp. M109 dùng deadband mặc định 4 °C
(±2 °C).

## 4. Homing, QGL và Cartographer

Giới hạn chuyển động chính:

- X `0..348`, endstop `PF0`.
- Y `-10..336`, endstop `PF1`.
- Z cấu hình `-5..347`; tốc độ Z tối đa `70 mm/s`, gia tốc Z `900 mm/s²`.
- Tốc độ XY tối đa `350 mm/s`, gia tốc `7000 mm/s²`.

Cartographer có offset X `0`, Y `35`. Bed mesh cấu hình X `20..320`,
Y `45..325`, 55 × 55 mẫu. Touch lấy mốc tại
`bed_mesh.zero_reference_position`; kTAMV không tham gia Z production.

`G32` thực hiện home/QGL theo macro hiện hành. Với mọi thao tác bảo trì thủ
công, kiểm tra carriage/tool/dock và khoảng hở trước khi home hoặc di chuyển.

## 5. `PRINT_START`

Trình tự thực trong `print-macros.cfg`:

1. Parse và kiểm tra tool, bed/nozzle temperature và tool list từ slicer.
2. Hủy callback dryer cũ, reset trạng thái và tắt crash detection.
3. Khởi động gia nhiệt bed và các tool cần dùng.
4. Home toàn bộ trục trước bất kỳ toolchange nào.
5. Chọn T0, gia nhiệt/đợi mức vệ sinh và chạy `CLEAN_NOZZLE`.
6. Đợi bed; thực hiện heat soak tự động hoặc `SOAK=` override.
7. Chạy QGL, vệ sinh T0 lần nữa và home Touch bằng Cartographer.
8. Tạo adaptive bed mesh.
9. Prime mọi tool slicer dùng; prime tool khởi đầu cuối cùng.
10. Bật crash detection và bắt đầu in.

Heat soak lạnh mặc định: PLA/TPU 30 giây, PETG 60 giây,
ABS/ASA/PC/NYLON/PA 90 giây. Chênh target không quá 5 °C thì bỏ qua; chênh
5–15 °C dùng 20% thời gian. `AUTO_SOAK=0` tắt tự động.

## 6. Prime, vệ sinh và kết thúc

`PRIME_LINES` dùng line dài 52 mm, ba pass, lượng extrusion 13.33 mm cho mỗi
pass đủ 52 mm, Z `0.28`, retract `1.8` và retract cuối `0.6`. Nó prime từng tool tại
vị trí riêng; không tự xem purge tower là bắt buộc.

`CLEAN_NOZZLE` yêu cầu KTC có active tool, có thể home khi cần, di chuyển tới
bucket/pad và vệ sinh tại vùng Y âm đã cấu hình. `PURGE_AND_CLEAN` purge vào
bucket rồi hạ nhiệt để chà. Không chạy các macro này nếu vật cản hoặc bucket/pad
không đúng vị trí cơ khí.

`PRINT_END` dừng crash detection, tắt heater/fan thuộc job, drop active tool và
park shuttle rỗng. `CANCEL_PRINT` đi qua đường cleanup tương ứng. Không viết tài
liệu hoặc slicer script dựa trên giả định T0 sẽ luôn còn gắn sau khi kết thúc.

## 7. Dryer

`START_DRYER` từ chối chạy nếu printer đang in. Với `PARK=1`, macro có thể home,
dock tool và park trước khi gia nhiệt. Preset thực trong code:

| Material | Bed | Chamber | Time | Fan |
| --- | ---: | ---: | ---: | ---: |
| PLA | 50 °C | 40 °C | 240 min | 40% |
| TPU | 60 °C | 45 °C | 300 min | 40% |
| PETG | 70 °C | 55 °C | 240 min | 50% |
| ABS/ASA | 90 °C | 65 °C | 240 min | 60% |
| NYLON | 100 °C | 70 °C | 360 min | 70% |
| PC | 105 °C | 75 °C | 360 min | 70% |

Các lệnh công khai là `START_DRYER`, `STOP_DRYER`, `DRYER_STATUS`. Macro có
handoff an toàn khi bắt đầu in; vẫn phải dọn nắp carton/vật liệu khỏi vùng
chuyển động trước job in.

## 8. Calibration và offset

Offset production hiện nằm trong `SAVE_CONFIG` của `printer.cfg`:

| Tool | X | Y | Z |
| --- | ---: | ---: | ---: |
| T0 | 0.000 | 0.000 | 0.000 |
| T1 | -0.243 | -0.252 | +0.228 |
| T2 | +0.746 | +0.086 | -0.295 |
| T3 | +0.304 | +0.449 | -0.268 |
| T4 | +0.041 | +0.352 | -0.014 |

Người vận hành đã đánh giá first layer của baseline này tốt bằng mắt. Hai phép
đo ToolVision đã retired ngày 2026-08-23 chỉ là evidence chẩn đoán:

| Tool | Production | PF2 switch | Cartographer Touch |
| --- | ---: | ---: | ---: |
| T0 | +0.000 | +0.000 | +0.000 |
| T1 | +0.228 | +0.098 | +0.242 |
| T2 | -0.295 | -0.384 | -0.256 |
| T3 | -0.268 | -0.154 | -0.160 |
| T4 | -0.014 | +0.078 | +0.102 |

Tích hợp ToolVision đã retired tính Z theo `raw(tool) - raw(reference)`. Đây là
candidate absolute
tương đối so với T0, không phải delta để cộng vào offset đang có. PF2 run có
T0 return drift `+0.028 mm`; Cartographer run `-0.008 mm`. Một run không đủ để
thay baseline đang in tốt; cần lặp cùng method/nhiệt độ và kiểm chứng độc lập.

kTAMV active không đo Z. Nó chỉ báo X/Y, giữ camera calibration/origin trong RAM
và không lưu offset tool. Xem [hướng dẫn sử dụng và đối chiếu kTAMV](ktamv-usage-comparison.vi.md).

## 9. Input shaper
 
Hệ thống sử dụng bộ lọc Input Shaper dùng chung (Unified Global Input Shaper) đo từ
Cartographer onboard ADXL345 trên carriage shuttle: X `mzv` 43.6 Hz/damping 0.124 và
Y `mzv` 33.4 Hz/damping 0.080. Cấu hình riêng trong T0–T4 được comment out để loại bỏ
độ trễ gọi lệnh khi đổi tool. Resonance tester sử dụng trực tiếp `accel_chip: adxl345`;
ShakeTune lưu 10 kết quả gần nhất dưới `Generated-Data/ShakeTune` và được đồng bộ lên Git.
Chi tiết xem [Tổng hợp kết quả đo kiểm TEST_SPEED & Input Shaper](danh-gia-input-shaper-va-test-speed-2026-09-04.md).

## 10. Cập nhật và kiểm tra

Chỉ cập nhật khi máy ở trạng thái rảnh rỗi (idle):

### Cách 1: Cập nhật 1-Click trực tiếp qua Mainsail (Khuyến nghị)
Sau khi đẩy code mới lên GitHub, trong giao diện web Mainsail:
- Vào **Settings > Machine / Update Manager**, tìm mục **All-Config-Voron**.
- Bấm nút **Update**: Moonraker sẽ tự động kéo code mới, tạo bản sao lưu an toàn, đồng bộ cấu hình và khởi động lại Klipper.
- Chi tiết xem [Hướng dẫn cập nhật Mainsail 1-Click](danh-sach-doi-chieu-va-huong-dan-update-mainsail.md).

### Cách 2: Cập nhật thủ công qua SSH
```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart moonraker klipper
```

`update.sh` tải archive `main` tạm và gọi installer. Installer kiểm tra KTC,
kTAMV được pin và hai patch runtime đã review, tạo backup rồi mới `rsync`. Nó
không tự restart.

Kiểm tra không chuyển động sau deploy:

```text
CALIBRATION_STATUS
QUERY_ENDSTOPS
KTAMV_STATUS
```

Sau đó mới xem trạng thái service/log. Chỉ home/toolchange/probe khi operator
đã xác nhận máy rỗng, dock đúng, đường đi an toàn và emergency stop sẵn sàng.

## 11. Quy tắc sửa an toàn

- Sao lưu trước khi sửa `.cfg`, `.conf` hoặc `.sh`.
- Không sửa `readonly-configs/`.
- Không thay offset production từ một lần đo.
- Không deploy khi đang in/paused/calibration.
- Giữ archive ToolVision đã retired bất biến; không restore vào config active
  trừ khi rollback rõ ràng.
- Không viết lại journal/backup cũ; tạo journal hoặc snapshot mới.

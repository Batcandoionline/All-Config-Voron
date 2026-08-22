# Hướng dẫn hệ thống Voron 2.4 StealthChanger 5 tool

Tài liệu này tổng hợp cách cấu hình trong repository `All-Config-Voron` hoạt động, các luồng vận hành chính, các điểm cần chú ý khi sửa, và danh sách rủi ro phát hiện khi rà soát mã cấu hình.

## 1. Phạm vi cấu hình

Máy hiện tại là Voron 2.4 StealthChanger dùng 5 toolhead độc lập:

- Mainboard: BIGTREETECH Manta M8P V2.0 + Raspberry Pi CM4.
- Toolhead board: 5x BIGTREETECH EBB36 V1.2 qua CAN bus.
- Probe chính: Cartographer V3 gắn trên shuttle, không gắn trên từng tool.
- Toolchanger: StealthChanger dùng KTC-Easy.
- Hotend/extruder: TZ V6 2.0 + WW BMG.
- Tool: T0 là tool tham chiếu, T1-T4 có offset so với T0.

Repository được chia làm hai phần:

- `config/`: payload thật, được copy về `~/printer_data/config` trên máy Voron.
- `extras/`: tài liệu, log, hình ảnh, G-code, Axiscope tham khảo. Phần này không được copy vào máy Voron khi chạy `install.sh` hoặc `update.sh`.

## 2. Thứ tự include và nguyên tắc override

File gốc là `config/printer.cfg`. Thứ tự include hiện tại:

1. `mainsail.cfg`: macro Mainsail chuẩn như `PAUSE`, `RESUME`, `CANCEL_PRINT`.
2. `toolchanger/readonly-configs/toolchanger-include.cfg`: nạp KTC-Easy readonly, homing, toolchanger, macro M104/M109, calibration, crash detection gốc và toàn bộ `T*.cfg`.
3. `Printer-Setup/calibration-probe.cfg`: Cartographer, mesh, quyền sở hữu PF2 của Tool Vision, dữ liệu rollback Axiscope và các macro trạng thái calibration.
4. Các file còn lại trong `Printer-Setup/`: hardware, fan/LED, input shaper, nozzle clean, prime line, print macro.
5. `Printer-Setup/tool-crash.cfg`: plugin `tool_crash`, override START/STOP và handler pause an toàn.
6. `Tool-Vision/tool_vision.cfg` là backend offset active; Axiscope được giữ dạng comment để rollback.

Nguyên tắc quan trọng:

- Không sửa trực tiếp các file trong `toolchanger/readonly-configs/`.
- Muốn thay đổi hành vi KTC-Easy thì thêm/ghi đè trong `toolchanger/toolchanger-config.cfg` hoặc `Printer-Setup/*.cfg`.
- Không đổi thứ tự include nếu chưa hiểu rõ. Nhiều section trùng tên là cố ý để Klipper merge/override, ví dụ `M109`, `START_CRASH_DETECTION`, `STOP_CRASH_DETECTION`, `homing_override_config`.

## 3. Tool definitions T0-T4

Mỗi tool nằm trong `config/toolchanger/tools/Tn.cfg` và gồm:

- MCU EBB riêng: `[mcu EBBn]`.
- ADXL345 riêng: `[adxl345 Tn]`.
- Extruder riêng: `[extruder]`, `[extruder1]` ... `[extruder4]`.
- TMC2209 extruder.
- Hotend fan và part fan.
- `[tool Tn]` của KTC-Easy:
  - `tool_number`
  - `extruder`
  - `fan`
  - `detection_pin`
  - `params_park_x/y/z`
  - `params_standby_temp`
  - input shaper params riêng từng tool
- Macro `Tn` gọi `SELECT_TOOL T=n`.
- Filament sensor riêng từng tool, debounce bằng `delayed_gcode`.

T0 là tool tham chiếu:

- `gcode_x_offset: 0`
- `gcode_y_offset: 0`
- `gcode_z_offset` không khai báo trực tiếp trong T0 cfg.

Offset T1-T4 hiện được lưu trong block `SAVE_CONFIG` cuối `printer.cfg`.

## 4. Toolchange hoạt động như thế nào

KTC-Easy quản lý pickup/dropoff bằng `[toolchanger]`.

Các thông số quan trọng trong `toolchanger/toolchanger-config.cfg`:

- `params_safe_y: 120`: trước khi chạy ngang vùng dock, gantry phải về Y an toàn.
- `params_close_y: 30`: vị trí tiếp cận trước dock.
- `params_fast_speed: 15000`: tốc độ di chuyển nhanh ngoài vùng dock.
- `params_path_speed: 900`: tốc độ trong đường pickup/dropoff.
- `require_tool_present: False`: cho phép homing/probing bằng Cartographer ngay cả khi shuttle không có tool.
- `params_dropoff_path` và `params_pickup_path`: đường cơ khí để thả/nhấc tool.

Luồng dropoff:

1. Nâng Z thêm 1 mm so với vị trí hiện tại.
2. Về `safe_y`.
3. Di chuyển X tới dock của tool.
4. Di chuyển Z/Y theo `params_dropoff_path`.
5. Tắt crash detection trong lúc dock.
6. Đặt LED tool vừa thả về standby.

Luồng pickup:

1. Về vùng trước dock.
2. Di chuyển X/Z/Y vào vị trí bắt đầu pickup.
3. Nếu tool có extruder, `M109 Tn S<target>` sẽ chờ tool đạt target đang đặt.
4. Chạy `params_pickup_path`.
5. `VERIFY_TOOL_DETECTED` tại điểm có `verify: 1`.
6. Khôi phục vị trí theo axis được KTC yêu cầu.

## 5. Homing, QGL và Cartographer

Homing được override bởi `toolchanger/readonly-configs/homing.cfg`.

Luồng `G28`:

1. `INITIALIZE_TOOLCHANGER`.
2. Vào docking mode.
3. Reset `GCODE_OFFSET`.
4. Nếu Z chưa home, set tạm Z=0 rồi nâng Z 10 mm.
5. Home Y trước, sau đó home X.
6. Thoát docking mode.
7. Nếu home Z, di chuyển về gần giữa bàn với offset ngẫu nhiên nhỏ rồi `G28 Z`.
8. Nâng Z 10 mm.

Macro `QUAD_GANTRY_LEVEL` trong `Printer-Setup/print-macros.cfg` là wrapper:

1. Set LED leveling.
2. `SAVE_GCODE_STATE`.
3. `BED_MESH_CLEAR`.
4. Nếu chưa home XYZ thì chạy `G28`.
5. Nếu QGL chưa applied, chạy một pass thô `horizontal_move_z=10 retry_tolerance=1`.
6. Chạy pass tinh `horizontal_move_z=2`.
7. Chạy `G28 Z` ở cuối.
8. `RESTORE_GCODE_STATE`.

Vì wrapper QGL đã tự `G28 Z`, không cần gọi thêm `G28 Z` sau `QUAD_GANTRY_LEVEL`.

## 6. PRINT_START hiện tại

Macro chính nằm trong `Printer-Setup/print-macros.cfg`.

OrcaSlicer phải gửi dạng:

```gcode
PRINT_START TOOL_TEMP={first_layer_temperature[initial_tool]}
  {if is_extruder_used[0]}T0_TEMP={first_layer_temperature[0]}{endif}
  {if is_extruder_used[1]}T1_TEMP={first_layer_temperature[1]}{endif}
  {if is_extruder_used[2]}T2_TEMP={first_layer_temperature[2]}{endif}
  {if is_extruder_used[3]}T3_TEMP={first_layer_temperature[3]}{endif}
  {if is_extruder_used[4]}T4_TEMP={first_layer_temperature[4]}{endif}
  BED_TEMP=[first_layer_bed_temperature] TOOL=[initial_tool]
```

Luồng PRINT_START:

1. Đọc tham số `TOOL`, `TOOL_TEMP`, `BED_TEMP`, `Tn_TEMP`.
2. Validate tool tồn tại và nhiệt độ hợp lệ.
3. `CLEAR_PAUSE`, `BED_MESH_CLEAR`, reset offset, `G90`, `M83`.
4. `INITIALIZE_TOOLCHANGER`.
5. Dừng crash detection để tránh báo sai trong homing/chuẩn bị.
6. Bật nóng bàn bằng `M140 S<BED_TEMP>`.
7. Preheat tool:
   - T0: 150 C để phục vụ clean/touch-home.
   - Tool được slicer dùng: 150 C standby.
   - Tool không dùng: tắt nhiệt.
8. Chạy full `G28` bằng Cartographer trên shuttle.
9. Nâng Z lên safe Z.
10. Sau khi đã home đủ, chọn T0 nếu cần.
11. Park T0 ở bucket và clean T0 ở 150 C.
12. Chờ bàn bằng `M190`.
13. Bật bed fan/chamber circulation 50%.
14. Heat soak nếu có `SOAK`, hoặc tự soak 100 s khi ABS/nhiệt bàn cao và bàn đang tăng nhiều.
15. Chạy QGL sau khi bàn ổn định nhiệt.
16. Đưa T0 về 150 C và chạy `CARTOGRAPHER_TOUCH_HOME`.
17. Nâng tool đầu tiên cần prime lên nhiệt in trong lúc chạy adaptive mesh; các tool dùng còn lại giữ standby.
18. `BED_MESH_CALIBRATE ADAPTIVE=1`.
19. `PRIME_LINES`, prime mọi tool được slicer dùng, tool in đầu tiên prime cuối.
20. Bật crash detection.
21. Đặt `_PRINT_STATE = printing`, set LED printing.

Điểm quan trọng:

- Không toolchange/dock trước khi full `G28`.
- QGL không chạy khi bàn đang nóng lên nữa; QGL chỉ chạy sau `M190` và heat soak.
- Touch-home chạy sau QGL, với bàn ổn định và T0 ở 150 C.

## 7. PRIME_LINES

File: `Printer-Setup/prime-lines.cfg`.

Mục tiêu:

- Prime tất cả tool có `Tn_TEMP > 0`.
- Tool in đầu tiên được prime cuối cùng để sau prime nó vẫn đang active và sẵn sàng in layer 1.
- Vẽ prime line ở phía trước giữa bàn, tránh quá gần góc.

Thông số hiện tại:

- `variable_line_length: 52.0`
- `variable_line_passes: 3`
- `variable_prime_amount: 13.33`
- `variable_prime_z: 0.28`
- `variable_retract_amount: 1.8`
- `variable_final_retract_amount: 0.6`
- `variable_wipe_distance: 12.0`

Luồng mỗi tool:

1. Set target nhiệt tool.
2. `Tn` để pickup tool.
3. `M109 Tn S<temp>` chờ tool đủ nhiệt.
4. Nếu biết tool kế tiếp, `M104` nâng nhiệt tool kế tiếp sớm.
5. Di chuyển tới slot prime.
6. Vẽ 3 pass song song theo trục X.
7. Retract để xả áp.
8. Nếu không phải tool cuối, hạ tool về standby.
9. Wipe ngang ở Z thấp để giảm string.
10. Nâng Z về travel Z.

## 8. PRINT_END, CANCEL, PAUSE/RESUME

`PRINT_END`:

1. Set `_PRINT_STATE = idle`.
2. Reset tốc độ/flow/pressure advance.
3. Dừng crash detection.
4. Nếu XYZ đã home:
   - Retract hai giai đoạn.
   - Nâng Z tối thiểu lên 50 mm hoặc thêm 10 mm.
   - Tắt toàn bộ heater tool.
   - Nếu đang cầm T1-T4 thì chuyển về T0.
   - Park sau bàn.
5. Reset offset.
6. Tắt heater, fan, stepper extruder.
7. Tắt bed sau đó hẹn tắt bed fan sau 180 s.
8. Clear mesh/pause, LED complete.

`CANCEL_PRINT` dùng hook trong `mainsail.cfg`:

- `_CLIENT_VARIABLE.variable_user_cancel_macro = "_CUSTOM_CANCEL_CLEANUP"`.
- Cleanup reset state, dừng crash detection, nâng Z an toàn, chuyển về T0 nếu cần, park sau bàn, tắt fan/stepper, clear mesh/offset.

`PAUSE` và `RESUME`:

- `PAUSE` và `CANCEL_PRINT` vẫn dùng logic Mainsail chuẩn qua hook trong `_CLIENT_VARIABLE`.
- `RESUME` được override ở cuối trong `fans-leds.cfg` để kết hợp hai yêu cầu:
  - KTC-Easy: `INITIALIZE_TOOLCHANGER` và `VERIFY_TOOL_DETECTED`.
  - Mainsail: khôi phục nhiệt/idle timeout, kiểm tra runout, hook LED, `_CLIENT_EXTRUDE`, rồi `RESUME_BASE`.
- Cách này tránh mất logic Mainsail do KTC readonly cũng khai báo macro `RESUME`.

## 9. Crash detection

Hệ này dùng plugin `tool_crash` vì Cartographer là probe chính và mỗi tool có `detection_pin`.

File liên quan: `Printer-Setup/tool-crash.cfg`.

Ý tưởng:

- Readonly KTC gốc chỉ hỗ trợ `tool_probe_endstop`.
- Override mới kiểm tra nếu `[tool_crash]` có trong config thì gọi:
  - `START_TOOL_CRASH_DETECTION`
  - `STOP_TOOL_CRASH_DETECTION`
- Nếu không có `[tool_crash]`, fallback về `START_TOOL_PROBE_CRASH_DETECTION`/`STOP_TOOL_PROBE_CRASH_DETECTION`.

Trong print:

- `PRINT_START` dừng crash detection trong giai đoạn home/clean/QGL/mesh/prime.
- Sau prime mới bật crash detection.
- Trong dropoff, crash detection bị dừng.
- Sau toolchange, nếu `_PRINT_STATE == printing`, `after_change_gcode` bật lại crash detection.

## 10. LED state machine

File: `Printer-Setup/fans-leds.cfg`.

Mỗi tool có 3 LED WS2812:

- LED 1: trạng thái tool.
- LED 2-3: chiếu sáng vùng in/hotend.

Các state chính:

- `standby`
- `ready`
- `heating`
- `toolchange`
- `leveling`
- `calibrating`
- `cleaning`
- `printing`
- `pause`
- `complete`
- `error`

`_PRINT_STATE` là biến nội bộ dùng để phân biệt `printing`, `paused`, `idle`, vì `printer.print_stats.state` không đủ tin cậy trong toolchange.

## 11. Calibration và tool offset

File:

- `Printer-Setup/calibration-probe.cfg`
- `toolchanger/readonly-configs/calibrate-offsets.cfg`
- `toolchanger/toolchanger-config.cfg`

Backend production hiện tại là Tool Vision với công tắc PF2 tại X=68, Y=-10,
Z=7; Axiscope và SexBolt/tools_calibrate đã tắt. Camera MF-500 vẫn dùng để soi
buồng, khi hiệu chuẩn mới tháo xuống gá nam châm có định vị. Người dùng phải tự
jog T0 và nhập X/Y/Z/safe-Z trước khi chạy camera-station calibration; khi các
tọa độ này còn trống, Tool Vision chặn chuyển động tới station. Không bật đồng
thời `axiscope`, `tools_calibrate` và `tool_vision` vì cả ba cùng sở hữu
`probe_multi_axis`.

Kiểm tra offset:

```gcode
CHECK_OFFSETS
```

Offset hiện tại đang lưu trong `SAVE_CONFIG` cuối `printer.cfg`, không nằm trực tiếp trong `T1.cfg` đến `T4.cfg`.

## 12. Cập nhật từ GitHub lên máy Voron

Trên máy Voron:

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart klipper
```

Chỉ restart Moonraker khi có thay đổi `moonraker.conf`:

```bash
sudo systemctl restart moonraker
```

`update.sh` làm các việc:

1. Tạo thư mục tạm bằng `mktemp` và tải archive nhánh `main` từ GitHub.
2. Giải nén source tạm, không tạo Git repository trên Pi.
3. `install.sh` backup config hiện tại vào `~/printer_data/config_backups/`.
4. Deploy file repo quản lý bằng `rsync --delete`, nhưng bảo vệ backup máy-local,
   KTC readonly và dữ liệu Tool Vision.
5. Đồng bộ riêng `Tool-Vision/tool_vision.cfg` mà không xóa kết quả cục bộ.
6. Xóa toàn bộ source/archive tạm khi kết thúc.

Khôi phục backup:

```bash
rsync -a --delete ~/printer_data/config_backups/config-YYYYMMDD-HHMMSS/ ~/printer_data/config/
sudo systemctl restart klipper
```

## 13. Rủi ro và đề xuất sửa

### R1 - Input shaper có thể chưa thật sự được áp dụng theo từng tool

Mức nguy hiểm: Trung bình.

Trạng thái: Đã sửa trong cấu hình ngày 2026-06-05.

Trước đó `input-shaper.cfg` ghi chú không dùng global `[input_shaper]`, nhưng `after_change_gcode` chỉ gọi `SET_INPUT_SHAPER` khi `input_shaper` tồn tại trong `printer.configfile.config`.

Rủi ro:

- Nếu không có `[input_shaper]`, dynamic input shaper trong `T0.cfg` đến `T4.cfg` có thể không được apply.
- In vẫn chạy, nhưng ringing/ghosting có thể không đúng theo từng tool.

Sửa đã áp dụng:

- Thêm section `[input_shaper]` mặc định dùng thông số T0 để Klipper tải module input shaper.
- Toolchange vẫn override bằng `params_input_shaper_*` của tool đang active.

```ini
[input_shaper]
shaper_type_x: 3hump_ei
shaper_freq_x: 88.4
damping_ratio_x: 0.078
shaper_type_y: 2hump_ei
shaper_freq_y: 58.4
damping_ratio_y: 0.164
```

Cần kiểm chứng sau restart Klipper: đổi tool và xem input shaper có thay đổi theo từng tool không.

### R2 - RESUME có nhiều nguồn khai báo

Mức nguy hiểm: Trung bình đến cao nếu merge sai.

Trạng thái: Đã sửa trong cấu hình ngày 2026-06-05 bằng final `RESUME` override trong `fans-leds.cfg`.

Có `RESUME` trong:

- `mainsail.cfg`
- `toolchanger/readonly-configs/toolchanger.cfg`
- `toolchanger/toolchanger-config.cfg` chỉ thêm description

Rủi ro:

- Nếu macro `RESUME` cuối cùng chỉ là logic Mainsail, có thể thiếu `INITIALIZE_TOOLCHANGER` và `VERIFY_TOOL_DETECTED`.
- Nếu macro `RESUME` cuối cùng chỉ là wrapper KTC readonly, có thể mất logic Mainsail như khôi phục nhiệt, runout check, hook LED và `_CLIENT_EXTRUDE`.

Sửa đã áp dụng:

- Thêm final `[gcode_macro RESUME]` trong `Printer-Setup/fans-leds.cfg`, tức phần override do repo này quản lý, không sửa `readonly-configs`.
- Final override khai báo rõ `rename_existing: RESUME_BASE`, giống pattern KTC-Easy/Mainsail, để `RESUME_BASE` luôn còn tồn tại và không phụ thuộc vào việc option này được merge từ section trước đó.
- Macro mới chạy `INITIALIZE_TOOLCHANGER` và `VERIFY_TOOL_DETECTED` trước khi resume.
- Sau đó chạy lại đầy đủ logic Mainsail: idle timeout restore, temperature restore, runout check, `user_resume_macro`, `_CLIENT_EXTRUDE`, `RESUME_BASE`.

Cần kiểm chứng sau khi máy rảnh:

- Pause một print nhỏ.
- Resume từ Mainsail.
- Console không được báo mất tool.
- LED phải về trạng thái printing.
- Nếu nozzle chưa đủ nóng, resume phải bị chặn như logic Mainsail.

### R3 - Tài liệu crash detection trong `tool-crash.cfg`

Mức nguy hiểm: Thấp đến trung bình.

Trạng thái: Đã sửa comment trong cấu hình ngày 2026-06-05.

Comment trong file vẫn mô tả kiểu bật detection trước G28/QGL/mesh rồi tắt sau đó. Macro thật hiện dừng detection trong chuẩn bị, chỉ bật lại sau prime.

Rủi ro:

- Người sửa sau có thể bật crash detection quá sớm trong homing/QGL/prime và gây false positive.

Sửa đã áp dụng:

- Comment trong `tool-crash.cfg` được cập nhật theo logic hiện tại:
  - Stop trong homing/clean/QGL/mesh/prime.
  - Start sau `PRIME_LINES`.
  - Stop khi dropoff/cancel/end.
  - Start lại trong `after_change_gcode` nếu `_PRINT_STATE == printing`.

### R4 - Prime line dài 52 mm mỗi pass

Mức nguy hiểm: Thấp.

Trạng thái: Đã giữ lại theo bản thực tế cho đường prime đẹp và ra nhựa ổn.

`prime-lines.cfg` hiện là:

```ini
variable_line_length: 52.0
variable_line_passes: 3
variable_prime_amount: 13.33
```

Với 3 pass song song, chiều dài này đang cho đường prime đẹp hơn bản 40 mm và có đủ thời gian ra nhựa. Macro vẫn tự co lại nếu số tool nhiều làm vùng X không đủ chỗ.

### R5 - T2 có offset Z rất lớn và từng có dấu hiệu cơ khí/nhiệt

Mức nguy hiểm: Cao nếu dùng T2 cho print quan trọng.

`SAVE_CONFIG` hiện có:

```ini
[tool T2]
gcode_z_offset = -0.746...
```

Độ lệch này lớn hơn nhiều so với T1/T3/T4 và trước đó T2 từng có hiện tượng bẹp sợi nhựa sau khoảng 20 phút.

Rủi ro:

- Có thể không chỉ là offset phần mềm.
- Có thể do heat creep, dòng extruder, ép idler, đường filament, hotend, quạt hotend, hoặc cơ khí dock/tool chưa ổn.

Đề xuất:

- Tạm không dùng T2 cho print dài nhiều màu.
- Test riêng T2:
  - kiểm tra fan hotend chạy đủ;
  - kiểm tra lực ép idler;
  - kiểm tra nhiệt motor extruder;
  - test extrude 100 mm ở nhiệt in;
  - test first layer riêng;
  - sau khi ổn mới chạy lại `CALIBRATE_ALL_OFFSETS` hoặc chỉnh Z bằng Ellis first layer.

### R6 - Tốc độ Z và gia tốc Z đã nâng cao

Mức nguy hiểm: Trung bình đến cao nếu cơ khí chưa ổn.

Trong `printer.cfg`:

```ini
max_z_velocity: 60
max_z_accel: 700
```

Rủi ro:

- Nếu cơ khí Z, belt, pulley, motor hoặc driver không ổn, có thể mất bước khi toolchange hoặc nâng Z nhanh.
- Mất bước Z sẽ ảnh hưởng QGL, touch-home, first layer và dock.

Đề xuất:

- Sau mỗi thay đổi cơ khí, chạy test Z repeatability.
- Nếu thấy QGL dao động tăng dần hoặc first layer lệch bất thường, thử giảm tạm:

```ini
max_z_velocity: 30
max_z_accel: 350
```

Sau đó tăng lại từng bước.

### R7 - `tmc_fan` comment và cấu hình có thể gây hiểu nhầm

Mức nguy hiểm: Thấp đến trung bình.

Trạng thái: Đã sửa trong cấu hình ngày 2026-06-05.

Trước đó trong `fans-leds.cfg`:

```ini
[controller_fan tmc_fan]
idle_speed: 1.0
idle_timeout: 0
```

Comment nói muốn quạt chạy 100% kể cả idle, nhưng cũng ghi `0 means off immediately`.

Rủi ro:

- Nếu hiểu sai, quạt TMC có thể không chạy sau khi stepper idle.
- Điện tử nóng khi máy chờ lâu trong chamber nóng.

Sửa đã áp dụng:

- Làm rõ comment: fan chạy khi stepper active và giữ chạy thêm trong thời gian cooldown.
- Đổi `idle_timeout` thành 3600 giây để quạt tiếp tục làm mát driver 1 giờ sau khi stepper idle.

Cần kiểm tra thực tế: sau khi stepper idle, quạt TMC còn chạy trong thời gian cooldown không.

### R8 - Nozzle clean dùng tọa độ ngoài vùng bàn

Mức nguy hiểm: Trung bình nếu copy sang máy khác hoặc lệch tọa độ.

`CLEAN_NOZZLE` dùng:

- Bucket: `X320 Y-8`
- Brush: quanh `Y=-8`

Rủi ro:

- Nếu endstop, dock, brush hoặc position_min/position_max thay đổi, đầu in có thể va bucket/brush/frame.

Đề xuất:

- Không port file này sang máy khác nếu chưa đo lại.
- Sau thay đổi cơ khí front brush/bucket, test:

```gcode
G28
G0 Z20
G0 X320 Y-8
```

Quan sát bằng tay trước khi chạy `CLEAN_NOZZLE`.

### R9 - Moonraker trusted_clients mở toàn bộ dải Tailscale

Mức nguy hiểm: Thấp đến trung bình.

`moonraker.conf` cho phép:

```ini
100.64.0.0/10
fd7a:115c:a1e0::/48
```

Rủi ro:

- Mọi thiết bị trong tailnet có thể được Moonraker tin cậy nếu kết nối tới được máy in.

Đề xuất:

- Chỉ dùng tailnet cá nhân đáng tin cậy.
- Không bật subnet router/exit node lạ trỏ vào máy in nếu không cần.
- Nếu muốn chặt hơn, dùng Moonraker authorization theo host/token thay vì trusted toàn dải.

### R10 - `update.sh` loại trừ nhật ký chỉnh sửa khỏi máy Voron

Mức nguy hiểm: Thấp.

Script có:

```bash
--exclude "Nhat-ky-chinh-sua/"
```

Rủi ro:

- Người dùng nhìn trên Mainsail file manager sẽ không thấy nhật ký.

Đề xuất:

- Giữ như hiện tại nếu muốn máy Voron gọn.
- Nếu muốn đọc nhật ký trên Voron, bỏ exclude này, nhưng không cần thiết cho vận hành.

## 14. Checklist sau mỗi lần cập nhật

Sau khi pull/update:

1. Chạy:

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart klipper
```

2. Nếu thay `moonraker.conf`:

```bash
sudo systemctl restart moonraker
```

3. Trong Mainsail:

```gcode
FIRMWARE_RESTART
```

4. Kiểm tra không có lỗi config.
5. Chạy `G28`.
6. Chạy `QUAD_GANTRY_LEVEL`.
7. Test pickup/dropoff từng tool ở Z an toàn.
8. Test `CLEAN_NOZZLE` nếu có thay đổi tọa độ bucket/brush.
9. Test `PRIME_LINES` bằng file nhỏ trước khi in nhiều màu dài.
10. Với print nhiều tool, quan sát console:
    - tool được heat standby;
    - QGL chạy sau khi bàn ổn định;
    - prime đủ nhựa;
    - crash detection bật lại sau prime;
    - sau toolchange, crash detection bật lại.

## 15. Quy tắc sửa cấu hình an toàn

- Không sửa readonly trừ khi có lý do rất rõ.
- Sửa trong `Printer-Setup/` hoặc `toolchanger/toolchanger-config.cfg`.
- Sau khi sửa macro động, restart Klipper.
- Sau khi sửa dock path, test pickup/dropoff không filament, nhiệt thấp, tay gần nút emergency.
- Sau khi sửa offset tool, in test first layer từng tool.
- Sau khi sửa heat/prime, test file nhỏ một tool trước, rồi mới test nhiều tool.
- Luôn giữ backup trong `~/printer_data/config_backups`.

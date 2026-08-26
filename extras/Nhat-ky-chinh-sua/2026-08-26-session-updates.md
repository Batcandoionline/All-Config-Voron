# Nhật ký chỉnh sửa — 2026-08-26

## 1. Phạm vi

- Cập nhật ToolVision mới nhất, thử panel `TOOL_VISION` và thực hiện HIL Z
  report-only ở điều kiện PETG: bàn 70 °C, nozzle 150 °C.
- Mỗi lượt hợp lệ tự chạy một `G28` đầy đủ qua action UI `HOME=1`.
- Thực hiện năm lượt Physical switch và năm lượt thử Cartographer Touch; không
  apply kết quả, không `SAVE_CONFIG` và không tự đổi offset production.
- Mã nguồn ToolVision không được sửa trong task All-Config. Mọi yêu cầu source
  được chuyển sang task Codex ToolVision riêng.
- Bốn ảnh mẫu in đa màu được dùng làm bằng chứng trực quan bổ sung cho bộ offset
  Cartographer đã áp dụng trước đó.

## 2. Backup và cập nhật ToolVision

- Backup local trước update:
  `extras/backups/pre-toolvision-ux-hil-20260826-161315/`.
- SHA-256 `tool-vision.cfg` trước update:
  `e6386c0910c179cb3ae10602639ab7b614851a7db70b05833d1fd97b8f1fa7b2`.
- Backup CM4:
  `/home/voron/printer_data/config_backups/pre-toolvision-ux-hil-20260826-161315/`.
- Moonraker updater đưa checkout live sạch tới branch
  `codex/compact-mainsail-output`, commit
  `aee9c3cabd753fdd7c1b55fb21fb06c79787531e`; runtime tiếp tục báo
  `3.4.0-rc2`.
- `tool_vision.service` active; health local `127.0.0.1:8085/api/v2/health`
  trả `ok`.
- Đồng bộ template mới rồi giữ lại setting riêng máy:
  - switch `^PF2`;
  - state/result trong `Generated-Data/ToolVision`;
  - recovery hook `INITIALIZE_TOOLCHANGER`.
- SHA-256 config live/local mới:
  `e5ae0b1f7899e350d05760b4e7eacd2dbdd10776092e125797668c7a7043bf81`.
- Validation đạt: một `[tool_vision]`, một `[respond]`, 23 section không trùng;
  macro block khớp template source; 15 contract test đạt; Klipper restart ready.

## 3. Panel mới

- `TOOL_VISION` mở panel `ToolVision XYZ calibration`, báo rõ report-only.
- Màn hình đầu có Physical switch, Cartographer Touch, camera XY, hai đường XYZ
  camera+Z, latest results và hai shortcut teach.
- Camera hiện `Camera setup required`; chưa thực hiện HIL XY/XYZ trong phiên này.
- Physical switch và Cartographer đều `Ready`; nút Close hoạt động.
- Mainsail và KlipperScreen dùng cùng macro. Tám action cộng phần mô tả có thể
  cần cuộn trên BTT 5-inch; đây là feedback UX, không phải hai implementation.

## 4. Lỗi tool detection sau update

- Session switch đầu tiên sau update đo T0/T1 rồi lỗi tại T2:
  `Expected tool tool T2 but active is None`.
- History loại khỏi thống kê:
  `20260826-092542-271-z-switch-01.json`, session
  `30e4106d88f242b09c39b11fc5c60fbd`.
- Người vận hành xác nhận có tác động cơ học và làm rơi nam châm giữ/nhận tool.
- Klipper log không có shutdown, traceback, CAN/MCU disconnect; mọi CAN counter
  vẫn `rx_error=0`, `tx_error=0`, `tx_retries=0`.
- Trước power-cycle, KTC lặp `No tool detected` và active bị xóa. Sau tắt/bật
  nguồn, đúng cùng commit/config đổi T0→T4→T0 thành công.
- Kết luận: bằng chứng phù hợp lỗi trạng thái nhận biết/giữ tool do can thiệp cơ
  học, không chứng minh lỗi update ToolVision.

## 5. HIL Physical switch — năm lượt hợp lệ

### Điều kiện

- Bàn đạt bốn mẫu ổn định `70.38, 70.55, 70.55, 70.50 °C` trước canary.
- Mỗi lượt có full `G28`, T0 active/detected, KTC ready, nozzle target 0 trước
  khi bắt đầu và ToolVision chờ cả năm nozzle ở 150 °C.
- Tất cả lượt trả T0, cleanup sạch, `applied=false`,
  `configuration_changed=false`.

| Lượt | T1 | T2 | T3 | T4 | Drift T0 | History |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | +0.104 | -0.368 | -0.156 | +0.108 | +0.044 | `20260826-100022-369-z-switch-01.json` |
| 2 | +0.102 | -0.486 | -0.172 | +0.076 | +0.008 | `20260826-100531-579-z-switch-01.json` |
| 3 | +0.076 | -0.382 | -0.158 | +0.066 | +0.004 | `20260826-100928-644-z-switch-01.json` |
| 4 | +0.070 | -0.380 | -0.156 | +0.072 | +0.006 | `20260826-101331-393-z-switch-01.json` |
| 5 | +0.064 | -0.386 | -0.148 | +0.064 | -0.000 | `20260826-101738-880-z-switch-01.json` |

| Tool | Mean | Median | Range | Sample SD | Mean - production |
| --- | ---: | ---: | ---: | ---: | ---: |
| T1 | +0.0832 | +0.076 | 0.040 | 0.01858 | -0.1632 |
| T2 | -0.4004 | -0.382 | 0.118 | 0.04832 | -0.1316 |
| T3 | -0.1580 | -0.156 | 0.024 | 0.00872 | +0.0316 |
| T4 | +0.0772 | +0.072 | 0.044 | 0.01787 | -0.0256 |

- T2 lượt 2 là ngoại lệ rõ; bốn lượt còn lại nằm `-0.368..-0.386 mm`.
- Mean/range drift T0: `+0.0124 / 0.044 mm`.
- `WARNING` chỉ vì chưa cấu hình `max_reference_z_drift`; các phép đo hoàn tất.
- Switch không phù hợp làm nguồn production trên dữ liệu này, đặc biệt T1/T2.

## 6. HIL Cartographer Touch — năm lượt thử

| Lượt | Trạng thái | T1 | T2 | T3 | T4 | Drift T0 | History |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | INVALID | +0.142 | -0.258 | — | — | — | `20260826-102122-528-z-cartographer_touch-01.json` |
| 2 | WARNING | +0.246 | -0.270 | -0.140 | +0.114 | +0.002 | `20260826-103127-777-z-cartographer_touch-01.json` |
| 3 | WARNING | +0.244 | -0.270 | -0.148 | +0.102 | -0.002 | `20260826-103621-562-z-cartographer_touch-01.json` |
| 4 | WARNING | +0.240 | -0.262 | -0.126 | +0.108 | +0.004 | `20260826-104948-744-z-cartographer_touch-01.json` |
| 5 | WARNING | +0.264 | -0.272 | -0.120 | +0.118 | +0.014 | `20260826-105431-421-z-cartographer_touch-01.json` |

### Lỗi lượt 1

- T3 không tìm được ba mẫu trong 0.010 mm sau mười lần Touch. Mười mẫu trải từ
  `-0.1388` tới `+0.1292 mm`, không được phép che bằng nới tolerance.
- CAN/MCU vẫn sạch lỗi. ToolVision lưu `INVALID`, không apply và heater cleanup
  đạt.
- Log cho thấy ToolVision chọn lại T0, nhưng trạng thái cuối KTC là
  `uninitialized/-1/0` dù `cleanup_errors=[]`. Một
  `INITIALIZE_TOOLCHANGER` không chuyển động khôi phục ngay `ready/0/0`.
- Lượt 2–5 đều vượt qua T3, cleanup sạch và trả T0 đúng.

### Thống kê bốn lượt hợp lệ

| Tool | Mean | Median | Range | Sample SD | Mean - production |
| --- | ---: | ---: | ---: | ---: | ---: |
| T1 | +0.2485 | +0.245 | 0.024 | 0.01063 | +0.0021 |
| T2 | -0.2685 | -0.270 | 0.010 | 0.00444 | +0.0003 |
| T3 | -0.1335 | -0.133 | 0.028 | 0.01279 | +0.0561 |
| T4 | +0.1105 | +0.111 | 0.016 | 0.00700 | +0.0077 |

- Mean/range drift T0: `+0.0045 / 0.016 mm`.
- Cartographer xác nhận rất sát production ở T1/T2/T4. T3 là ngoại lệ cần
  điều tra; không apply.
- Lượt 2 có dao động nhiệt quan sát ngoài metadata ngay sau tái gia nhiệt; lượt
  3–5 qua heat-soak ổn định và vẫn cho cùng kết luận.

## 7. So sánh với bộ offset đã in đẹp và ảnh mẫu

### Bộ số

| Tool | Git cũ | Mean 3 lượt 25/08 | Live dùng in | Mean 4/5 lượt 26/08 | 26/08 - 3 lượt | 26/08 - live |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T1 | +0.2280 | +0.24267 | +0.2464 | +0.2485 | +0.00583 | +0.0021 |
| T2 | -0.2950 | -0.26800 | -0.2688 | -0.2685 | -0.00050 | +0.0003 |
| T3 | -0.2680 | -0.18600 | -0.1896 | -0.1335 | +0.05250 | +0.0561 |
| T4 | -0.0140 | +0.10467 | +0.1028 | +0.1105 | +0.00583 | +0.0077 |

- Mean ba lượt Cartographer ghi riêng sáng 25/08 là T1-T4 `+0.24267`,
  `-0.26800`, `-0.18600`, `+0.10467 mm`. Đó không phải bộ đã load để in
  mẫu bốn mặt.
- Bộ live dùng để in là mean **năm lượt Cartographer hợp lệ** ở bàn
  70 °C chiều 25/08: T1 `+0.2464`, T2 `-0.2688`, T3 `-0.1896`, T4
  `+0.1028 mm`. Năm history từ `13:18` tới `13:39` tính ra đúng tuyệt đối
  bốn mean này.
- Moonraker ghi ba lần upload `printer.cfg` lúc `20:54:05`, `20:54:34` và
  `20:55:03`. Config dump đầu đã chứa đúng bốn mean năm lượt; hai giá trị
  âm ban đầu dùng nhầm Unicode minus và được sửa thành ASCII minus trong bản
  cuối. Klipper ready lúc `20:55:13`, job `Khoi lap phuong_PETG_3m16s.gcode`
  bắt đầu `20:59:09`. Chuỗi thời gian xác nhận mẫu in dùng bộ mean năm lượt.
- Năm **lần thử** Cartographer ngày 26/08 chỉ có bốn lượt hoàn tất; lượt
  1 INVALID do T3 không hội tụ. Mean 26/08 vì vậy là thống kê 4/5 lượt,
  không phải mean năm lượt hợp lệ.

### Đánh giá bốn mặt mẫu in

- Các dải màu giữ bề rộng và mặt phẳng tổng thể tốt; không thấy bậc nhô/lõm
  lặp lại ở cả bốn mặt đúng mỗi lần đổi tool.
- Dải đen khá sắc và đồng đều; một chấm sáng đơn lẻ không lặp ở mặt khác.
- Dải xanh/đỏ có chỗ bóng và gợn gần cạnh/seam, nhưng không chạy đồng nhất quanh
  toàn bộ vật thể; phù hợp flow, pressure/seam hoặc tính chất filament hơn lỗi Z.
- Mép đáy đỏ và dải trắng trên cùng chịu ảnh hưởng chamfer/top geometry, không
  dùng làm thước đo offset riêng.
- Ảnh ủng hộ bộ Cartographer production hiện hành và cho thấy thay đổi lớn so
  với bộ cũ không tạo step rõ. Không có ảnh mẫu in bằng bộ cũ trong cùng điều
  kiện nên không thể định lượng mức cải thiện chỉ bằng ảnh.
- T1/T2/T4 ngày 26/08 xác nhận lại baseline theo **phép đo** trong giới hạn
  độ lặp. Chưa có bản in dùng kết quả 26/08, nên không coi đây là xác
  nhận bằng in. T3 lệch `+0.0525 mm` so mean ba lượt và `+0.0561 mm`
  so live đã in, đủ lớn để cần A/B riêng; sampling failure làm giảm thêm
  độ tin cậy.
- Quyết định: giữ nguyên production; không đổi T3 hoặc bất kỳ tool nào từ phiên
  26/08.

## 8. Vấn đề cần chuyển sang ToolVision

1. UI/Moonraker request dài luôn nhận nginx `504 Gateway Time-out` khoảng 60
   giây trong khi calibration tiếp tục 3,5–4,3 phút và ghi kết quả hợp lệ. Cần
   cơ chế fast-ack/job-follow hoặc UI theo dõi `busy` + session/history thay vì
   coi response HTTP dài là completion.
2. Sau lỗi Cartographer T3, restore T0 được adapter xác nhận đồng bộ và
   `cleanup_errors=[]`, nhưng KTC chuyển trễ sang `uninitialized/-1/0`. Cần
   post-restore settle rồi xác minh status ready, active tool và detected tool;
   nếu sai phải ghi cleanup error cùng hướng dẫn operator.
3. Không tự retry Cartographer sampling failure và không nới tolerance. Hiển thị
   rõ tool/phase, 10-sample spread và khuyến nghị vệ sinh/kiểm tra seating.
4. Một ngưỡng drift chung không phù hợp hoàn toàn: switch quan sát tới 0.044 mm,
   Cartographer tối đa 0.014 mm. Cân nhắc threshold theo method với fallback
   global; không tự đặt limit từ máy khác.
5. Panel chính tám action hơi dày trên BTT 5-inch. Gợi ý routine-first:
   `Measure Z`, `Measure XY camera`, `Measure XYZ`, `Latest results`, `Setup`,
   `Close`; trang Z/XYZ tiếp theo cho người dùng chọn switch hoặc Cartographer.
6. Camera chưa ready nên XY/XYZ chưa HIL. Không bỏ camera khỏi UI; cần trạng thái
   setup rõ và fail-closed trước motion.
7. Thêm khả năng chọn subset tool, ví dụ T0/T3, để điều tra lặp một tool mà không
   phải đổi đủ năm tool; vẫn bắt buộc reference T0 và report-only.
8. Success hiện mang nhãn generic `WARNING` chỉ vì threshold chưa cấu hình. UI
   nên phân biệt “measurement completed; validation limit not configured” với
   warning phần cứng/thực nghiệm.

Toàn bộ raw data, thống kê, lỗi T3, KTC delayed-uninitialized, HTTP 504,
UX camera/Z/XYZ và yêu cầu test đã được gửi sang task Codex ToolVision
`01a02382-e5a5-7c93-952f-f01783f6cd55` ngày 26/08. Task All-Config không
sửa mã nguồn ToolVision.

## 9. Đồng bộ Git và trạng thái cuối

- `printer.cfg` trong Git/máy tính còn bốn offset trước thử nghiệm trong khi máy
  live dùng bộ mean năm lượt Cartographer 70 °C ngày 25/08 đã được nhập thủ công và
  kiểm chứng bằng bản in. Chỉ đồng bộ bốn giá trị live vào Git; không kéo mesh,
  PID, Cartographer model hoặc axis twist khác.
- Backup trước đồng bộ:
  `extras/backups/pre-live-production-offset-sync-20260826-180847/`, SHA-256
  `916c9d8c695b9af1902793e0550ce502b109622786ccc9e57ed1234610806964`.
- Đây là sync bằng chứng production đã tồn tại, không phải apply kết quả ngày
  26/08.
- Trạng thái máy cuối: Klipper `ready`, print `standby`, ToolVision idle,
  `last_error=null`, KTC `ready`, T0 active/detected, bàn target/power 0, cả năm
  nozzle target/power 0.
- Hai mục untracked `extras/Config download/config-20260821-172111*` thuộc người
  dùng được giữ nguyên và không stage.

## 10. Dừng HIL bổ sung do driver X báo ShortToSupply

### Mục tiêu và preflight

- Mục tiêu là chạy thêm năm attempt switch và năm attempt Cartographer,
  xen kẽ, report-only, full `G28` trước từng attempt, nozzle 150 °C và bàn
  PETG 70 °C.
- Trước chuyển động: Klipper ready, print standby, ToolVision idle, KTC ready,
  T0 active/detected, camera cho thấy bàn và dock không có vật cản.
- Bàn đạt bốn mẫu liên tiếp `70.33, 70.18, 70.10, 70.04 °C` trong
  ±0.5 °C sau khi overshoot ngắn tới 74.57 °C.

### Sự cố attempt đầu

- Attempt 1 dùng `METHOD=SWITCH HOME=1`; session
  `20260826-114524-081-z-switch-01.json`, duration `18.681 s`, trạng thái
  `INVALID`.
- Lỗi chính xảy ra trong full `G28`, trước gia nhiệt nozzle/measure T0:
  `TMC 'stepper_x' reports error: DRV_STATUS: c01f0010 s2vsa=1(ShortToSupply_A!) cs_actual=31 stealth=1 stst=1`.
- History có `offsets={}`, `waited_tools=[]`, `reference_z_drift=null`,
  `configuration_changed=false`, `applied=false`. Không có dữ liệu Z để đưa
  vào thống kê.
- Klipper shutdown lúc `18:45:23`; log sau đó ghi reset EBB0-EBB4,
  Cartographer và main MCU rồi `Start printer` lúc `18:45:27`; Moonraker xác
  nhận ready lại lúc `18:45:36`. Chuỗi test không gửi
  `FIRMWARE_RESTART` và không coi trạng thái ready lại là bằng chứng phần cứng
  đã an toàn.
- Cleanup ToolVision không thể chạy abort/recovery/heater/G-code-state trong
  khi printer shutdown và ghi đúng các `cleanup_errors`; original tool không được
  restore trong session lỗi.

### Hành động an toàn và trạng thái

- Dừng toàn bộ chuỗi; 0/5 switch và 0/5 Cartographer hợp lệ trong
  batch bổ sung này. Không tự retry, không initialize toolchanger và không
  có chuyển động tiếp theo.
- Gửi `TURN_OFF_HEATERS` sau khi Klipper ready lại; xác nhận bàn và cả năm
  nozzle target/power 0. ToolVision idle; KTC sau khi Klipper nạp lại báo ready,
  T0 active/detected, nhưng XYZ không được coi là đã home.
- Bằng chứng off-device trước khi có bất kỳ retry nào:
  `extras/backups/pre-resume-toolvision-z-hil-20260826-184826/`.
- Log nguồn: `/home/voron/printer_data/logs/klippy.log` dòng 25071-25072 và
  26706-26715; `/home/voron/printer_data/logs/moonraker.log` các event
  `18:45:23-18:45:36`.
- Cần tắt nguồn, kiểm tra dây/connector motor X và driver X trước khi
  tiếp tục. Không chỉ gửi `FIRMWARE_RESTART` để bỏ qua cờ short-to-supply.

## 11. HIL Cartographer bổ sung sau khi xử lý driver X

### Khôi phục và canary

- Người vận hành xác nhận đã xử lý phần cứng. Preflight sau đó cho
  `DUMP_TMC STEPPER=stepper_x` =
  `DRV_STATUS: 80190000 cs_actual=25 stst=1`, không còn
  `ShortToSupply_A`; cold `G28 X Y` và full `G28` đều thành công.
- Klipper ready, print standby, ToolVision idle, T0 active/detected và bàn được
  heat-soak tại 70 °C trước khi chạy lại.
- Chuỗi xen kẽ ban đầu sau sửa phần cứng có một switch hợp lệ
  (`T1 +0.104, T2 -0.364, T3 -0.086, T4 +0.090`, drift `+0.028`) và một
  Cartographer hợp lệ
  (`T1 +0.258, T2 -0.268, T3 -0.118, T4 +0.120`, drift `+0.004`).
- Attempt Cartographer tiếp theo bị `INVALID` tại T2:
  `CARTOGRAPHER_TOUCH_PROBE failed: Unable to find 3 samples within 0.010mm in a window of 5 after 10 touches`;
  history `20260826-121300-706-z-cartographer_touch-01.json`. Không có lỗi
  TMC/CAN/Klipper, không apply và cleanup không báo lỗi, nhưng KTC lại kết thúc
  trễ ở `uninitialized/-1/0`. Detector vẫn thấy T0; macro không chuyển động
  `INITIALIZE_TOOLCHANGER` khôi phục đúng `ready/0/0`.
- Theo yêu cầu người vận hành, bỏ chuỗi xen kẽ dang dở và bắt đầu lại bộ
  Cartographer từ 0/5. Các attempt trước đó không trộn vào thống kê năm lượt
  mới bên dưới.

### Năm lượt Cartographer mới từ đầu

- ToolVision `3.4.0-rc2`, report-only, bàn 70 °C, nozzle 150 °C. Mỗi lượt dùng
  `HOME=1`, vì vậy có full `G28` riêng trước khi đo.
- Cả năm lượt hoàn tất; `applied=false`, `configuration_changed=false`,
  `last_error=null`, cleanup sạch và trả T0 `ready/0/0`.
- Nhãn `WARNING` chỉ do chưa cấu hình `max_reference_z_drift`, không phải lỗi
  phép đo.

| Lượt | T1 | T2 | T3 | T4 | Drift T0 | Duration | History |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | +0.272 | -0.264 | -0.102 | +0.128 | +0.020 | 252.09 s | `20260826-122023-520-z-cartographer_touch-01.json` |
| 2 | +0.246 | -0.280 | -0.118 | +0.114 | +0.000 | 239.63 s | `20260826-122433-553-z-cartographer_touch-01.json` |
| 3 | +0.250 | -0.288 | -0.128 | +0.120 | +0.000 | 232.51 s | `20260826-122833-740-z-cartographer_touch-01.json` |
| 4 | +0.256 | -0.268 | -0.108 | +0.132 | +0.010 | 251.35 s | `20260826-123259-936-z-cartographer_touch-01.json` |
| 5 | +0.248 | -0.268 | -0.136 | +0.118 | -0.006 | 252.50 s | `20260826-123723-967-z-cartographer_touch-01.json` |

| Tool | Mean | Median | Range | Sample SD | Mean - production |
| --- | ---: | ---: | ---: | ---: | ---: |
| T1 | +0.2544 | +0.250 | 0.026 | 0.01053 | +0.0080 |
| T2 | -0.2736 | -0.268 | 0.024 | 0.01004 | -0.0048 |
| T3 | -0.1184 | -0.118 | 0.034 | 0.01396 | +0.0712 |
| T4 | +0.1224 | +0.120 | 0.018 | 0.00740 | +0.0196 |

- Mean/median/range/sample SD drift T0 lần lượt là
  `+0.0048 / +0.000 / 0.026 / 0.01026 mm`; nhiệt bàn trong metadata toàn bộ
  năm lượt nằm `69.94..70.02 °C` tại các mốc before-home/start/end.
- So với bộ Cartographer production đã cho bản in tương đối đẹp
  (`T1 +0.2464, T2 -0.2688, T3 -0.1896, T4 +0.1028`), T1/T2 tiếp tục xác nhận
  rất gần. T4 cao hơn `+0.0196 mm`, còn T3 cao hơn `+0.0712 mm`, vượt xa độ
  phân tán nội bộ của phép đo.
- Gộp chín lượt Cartographer hợp lệ ngày 26/08 (bốn lượt mục 6 và năm lượt
  mới), mean là `T1 +0.25178, T2 -0.27133, T3 -0.12511, T4 +0.11711 mm`;
  sample SD tương ứng `0.01037, 0.00806, 0.01490, 0.00923 mm`. T3 vẫn lệch
  production `+0.06449 mm`, nên đây là sai khác có hệ thống trong điều kiện đo,
  không phải một outlier đơn.

### Quyết định

- Giữ nguyên bộ offset production đã kiểm chứng bằng bản in; không apply mean
  hay median của batch mới, đặc biệt không tự đổi T3.
- Chọn Cartographer làm phương pháp Z ưu tiên khi phần cứng hỗ trợ vì độ lặp tốt
  hơn switch và bám production ở T1/T2. Switch tiếp tục là tùy chọn/fallback,
  không được trộn hai phương pháp trong cùng baseline.
- ToolVision nên tổng hợp batch bằng median kèm min-max/sample SD, so với
  configured production và fail-closed/report-only khi chênh lệch vượt ngưỡng
  cấu hình. Một candidate đo được chỉ được đưa sang A/B print sau khi người vận
  hành xác nhận; không tự `SAVE_CONFIG`.
- Sau khi hoàn tất, `TURN_OFF_HEATERS`; xác nhận Klipper ready, print standby,
  ToolVision idle, KTC `ready/0/0`, bàn và cả năm nozzle target/power bằng 0.

## 12. Batch sau vệ sinh T3 bị chặn tại T2

- Người vận hành phát hiện một miếng nhựa cũ bị ép dẹt trên T3 và yêu cầu đo
  lại năm lượt Cartographer sau khi loại bỏ nhiễu này.
- Preflight đạt: Klipper ready, print standby, ToolVision idle, KTC
  `ready/0/0`, `DRV_STATUS` X vẫn `80190000 cs_actual=25 stst=1`. Bàn đạt bốn
  mẫu liên tiếp `70.00, 70.47, 70.41, 70.32 °C` trong ±0.5 °C.
- Canary đầu không tới T3 mà `INVALID` tại T2 do
  `Unable to find 3 samples within 0.010mm in a window of 5 after 10 touches`.
  History `20260826-125222-292-z-cartographer_touch-01.json`, duration
  `162.248 s`, T1 `+0.262`, waited tools `[0,1,2]`, bàn before/start/end
  `70.27/70.21/70.08 °C`.
- Sau recovery hook, KTC và detector trở lại `ready/0/0`; driver X sạch. Bắt
  đầu lại batch chính thức 0/5 nhưng attempt 1 tiếp tục `INVALID` tại T2 với
  cùng lỗi. History `20260826-125850-285-z-cartographer_touch-01.json`, duration
  `160.472 s`, T1 `+0.258`, waited tools `[0,1,2]`, bàn before/start/end
  `70.03/70.00/70.04 °C`.
- Cả hai session đều report-only, không apply, không thay đổi config và không có
  lỗi TMC/CAN/Klipper. Vì đều dừng trước T3, không có dữ liệu sau vệ sinh T3 để
  so sánh; không được diễn giải hai lỗi này là T3 đã tốt hoặc xấu hơn.
- Cả hai terminal path `INVALID` lại để KTC ở `uninitialized/-1/0` dù detector
  thấy T0 và `cleanup_errors=[]`. Recovery hook khôi phục đúng `ready/0/0`.
- Phát hiện thêm lỗi state: `last_history_file`, error, duration và results cập
  nhật theo session lỗi mới, nhưng `tool_vision.last_run` vẫn giữ timestamp
  session hợp lệ cũ `1787747843.9670157`. Client poll theo `last_run` vì vậy có
  thể treo sau `busy=false`.
- Dừng retry sau hai lỗi T2 liên tiếp; không nới tolerance và không tự retry.
  Tắt toàn bộ heater; trạng thái cuối Klipper ready, print standby, ToolVision
  idle, KTC `ready/0/0`, driver X sạch, mọi heater target/power 0.
- Hai history và yêu cầu sửa sampling diagnostics, terminal state, cleanup
  verification/recovery đã được gửi sang task ToolVision
  `01a02382-e5a5-7c93-952f-f01783f6cd55`.

## 13. Thử lại sau power reset

- Một attempt ngay trước reset tiếp tục `INVALID` tại T2, history
  `20260826-130820-281-z-cartographer_touch-01.json`, duration `167.993 s`,
  T1 `+0.262`. Raw Touch 3-10 ở T2 có spread tối thiểu `0.3820 mm`
  (`-0.3979..-0.0159`), trong khi CAN, Cartographer và driver đều không báo
  lỗi truyền thông/phần cứng.
- Người vận hành power-reset máy. Sau boot: Klipper ready, ToolVision
  `3.4.0-rc2`, detector thấy T0; `INITIALIZE_TOOLCHANGER` khôi phục
  `ready/0/0`, driver X `80190000`. Reset cũng làm `last_run` nạp lại đúng
  timestamp history lỗi trước và xóa `last_error`, khác state stale trước reset.
- Bàn đạt bốn mẫu `70.22, 70.41, 70.34, 70.27 °C`; bắt đầu batch mới 0/5.

| Attempt | Status | T1 | T2 | T3 | T4 | Drift | History |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | WARNING | +0.250 | -0.266 | -0.164 | +0.120 | +0.008 | `20260826-131652-546-z-cartographer_touch-01.json` |
| 2 | WARNING | +0.238 | -0.276 | -0.190 | +0.106 | -0.008 | `20260826-132117-268-z-cartographer_touch-01.json` |
| 3 | INVALID tại T2 | +0.254 | — | — | — | — | `20260826-132403-319-z-cartographer_touch-01.json` |

- Hai lượt đầu sau reset vượt T2 và hoàn tất sạch. T3 `-0.164/-0.190 mm` gần
  production `-0.1896 mm` hơn rõ so mean trước vệ sinh `-0.1184 mm`; bằng chứng
  này ủng hộ miếng nhựa dẹt trên T3 đã gây bias, nhưng hai mẫu chưa đủ để chốt
  mean năm lượt.
- Attempt 3 tái lỗi sampling ở T2 dù bàn before/start/end là
  `70.01/70.01/70.02 °C`. Mười raw touch T2:
  `-0.1519, -0.4759, -0.4939, -0.4759, -0.4859, -0.4539, -0.4239, -0.4739, -0.4799, -0.4159 mm`;
  full spread `0.3420 mm`, bỏ outlier đầu vẫn spread `0.0780 mm`.
- Power reset chỉ khôi phục tạm thời hai lượt rồi lỗi quay lại; chưa đủ bằng
  chứng để quy thuần software. Cần phân biệt nhựa/nozzle T2, tool seating/compliance
  và state Cartographer bằng raw-sample telemetry.
- Batch dừng tại 2 lượt hợp lệ/3 attempts; không nới tolerance, không apply.
  `TURN_OFF_HEATERS`, recovery hook và `DUMP_TMC` xác nhận trạng thái cuối
  Klipper ready, print standby, ToolVision idle, KTC `ready/0/0`, driver X sạch,
  mọi heater target/power 0.
- Raw values và ba history sau reset đã gửi sang task ToolVision để triển khai
  diagnostics/state/cleanup fixes.

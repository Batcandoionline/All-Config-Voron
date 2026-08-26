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

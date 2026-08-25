# Nhật ký chỉnh sửa — 2026-08-25

## 1. Giao diện ToolVision hai phương pháp Z và giảm nhiễu console

### Phạm vi và quyền sở hữu mã nguồn

- Người vận hành yêu cầu giao diện `TOOL_VISION` tập trung vào phép đo Z bằng
  hai phương pháp: physical switch và Cartographer Touch; kết quả vẫn chỉ để
  báo cáo, không tự áp dụng vào offset production.
- Người vận hành quy định mọi thay đổi mã nguồn ToolVision phải được chuyển sang
  task Codex `Đơn giản hóa tự động căn chỉnh`. Từ thời điểm nhận quy định này,
  task All-Config chỉ sửa cấu hình máy, triển khai canary và thực hiện HIL;
  không tự sửa thêm repository `D:\Desktop\Tool-Vision`.
- Yêu cầu rà soát source đã được gửi sang task ToolVision kèm commit, CI,
  backup, số liệu console và toàn bộ lỗi HIL bên dưới.

### Sao lưu trước thay đổi

- Backup cấu hình local trước sửa:
  `extras/backups/pre-toolvision-compact-panel-20260825-154839/`.
- SHA-256 `tool-vision.cfg` trước sửa:
  `4a24f095abf647442f8a6a911dff5a2a65d0ec2048b22c4de571ed4ea70caa66`.
- Backup source ToolVision được tạo trước thay đổi giao diện:
  `D:\Desktop\Tool-Vision\.local-backups\pre-compact-mainsail-output-20260825-154327`.
- Backup máy trước triển khai được xác minh ở cả hai nơi:
  - `/home/voron/printer_data/config_backups/tool-vision/manual-dual-z-ui-before-20260825-155125`.
  - `D:\Desktop\Tool-Vision\.local-backups\printer-dual-z-ui-before-20260825-155125`.

### Giao diện và triển khai canary

- `config/Printer-Setup/tool-vision.cfg` được đổi thành panel Z gọn gồm:
  `Physical switch`, `Cartographer Touch`, `Latest results` và
  `Advanced setup`.
- Hai hành động Z gọi rõ phương pháp và mức log:
  - `MODE=Z METHOD=SWITCH VERBOSITY=QUIET`.
  - `MODE=Z METHOD=CARTOGRAPHER_TOUCH VERBOSITY=QUIET`.
- Panel cũ ghi 12 mục G-code store khi mở: một command và 11 phản hồi
  `action:prompt_*`. Panel mới ghi 9 mục: một command và 8 phản hồi, giảm
  27,3% số response và 25% tổng số mục.
- Không dùng regex để ẩn `action:prompt_*`, vì đây là giao thức điều khiển
  prompt của Mainsail và việc lọc có thể làm prompt/macro không chạy.
- SHA-256 cấu hình mới đã triển khai:
  `6947c09f402f30fe20985d69f40ceb9236ce5f6b9bcf58846b80427d110f7809`.
- Canary ToolVision live đang chạy branch `codex/compact-mainsail-output`,
  commit `bc5a7893f548c637b9d48844fce004de731eb64d`, version `3.4.0-rc2`.
  Security gate GitHub của commit này đạt.
- Kiểm tra cấu hình local đạt: 13 macro, mọi reference/Jinja hợp lệ, panel
  chính có đúng 8 response và chỉ có một macro public `TOOL_VISION`.

## 2. Dạy station switch tại X68 Y-8 Z2

- Trước setup đã `G28` đầy đủ, xác nhận T0 active/detected, toolchanger ready,
  switch open và tất cả heater target/power bằng 0.
- Di chuyển lift-first tới `X68 Y-8 Z2`, sau đó chạy
  `TOOL_VISION_SETUP_Z METHOD=SWITCH`.
- Setup thành công và state schema 4 lưu:
  - `position=[68.0,-8.0,2.0]`.
  - `safe_z=7.0`.
  - `trigger_z=1.3985049154729698`.
  - `reference_offset=[0.0,0.0,0.0]`.
- Sau setup, cả `switch_ready` và `cartographer_touch_ready` đều `true`;
  Cartographer tiếp tục dùng station `[174.0,168.0,15.0]`, model `default`.

## 3. HIL so sánh SWITCH và CARTOGRAPHER_TOUCH

### Quy trình kiểm thử

- Kế hoạch là ba cặp xen kẽ switch và Cartographer, luôn `G28` đầy đủ trước
  mỗi lượt, dùng 150 °C, giữ T0 làm reference và không áp kết quả.
- Chuỗi được dừng ngay khi có lỗi INVALID; không lặp mù trên phần cứng.

### SWITCH lượt 1 — INVALID trước chuyển động

- Sau `G28`, máy homed XYZ, T0 active/detected, toolchanger ready và năm heater
  target bằng 0.
- Lệnh:
  `TOOL_VISION_CALIBRATE MODE=Z METHOD=SWITCH VERBOSITY=QUIET`.
- ToolVision từ chối tức thời với lỗi
  `Z target -8.000 is outside [-5.000, 347.000]`, dù station đúng là
  `X68 Y-8 Z2`. Dấu hiệu này cho thấy Y âm bị dùng như tọa độ Z trên đường chạy
  switch.
- History:
  `/home/voron/printer_data/config/Generated-Data/ToolVision/tool-vision-history/20260825-090432-020-z-switch-01.json`;
  session `1f6fd8c9a7504f4980da951f87288505`.
- Kết quả `INVALID`, duration 0,00176 s, `offsets={}`, `cleanup_errors=[]` và
  không có thay đổi production.
- Sau lỗi, heater vẫn target/power 0 và T0 vẫn detected, nhưng KTC chuyển sang
  `uninitialized`. `G28` khôi phục trạng thái ready/T0 trước bước tiếp theo.
- Bằng chứng và yêu cầu regression test Y âm/Z hợp lệ đã được gửi sang task
  ToolVision; không sửa source trong task này.

### CARTOGRAPHER_TOUCH lượt 1 — INVALID tại T2

- Sau một `G28` riêng, điều kiện đầu vào tiếp tục đạt và lệnh explicit
  Cartographer được chạy ở 150 °C.
- Hai phép đo hợp lệ trước khi lỗi:
  - T0: `trigger_z=-0.313507`, `z=0.000`.
  - T1: `trigger_z=-0.055507`, `z=+0.258`.
- T2 được pickup/detected nhưng Cartographer thất bại:
  `Unable to find 3 samples within 0.010mm in a window of 5 after 10 touches`.
- History:
  `/home/voron/printer_data/config/Generated-Data/ToolVision/tool-vision-history/20260825-090849-227-z-cartographer_touch-01.json`;
  session `5ee260781605410c9be298447d84bac8`.
- Kết quả `INVALID`, duration 142,705 s; không apply. Heater cleanup đạt nhưng
  recovery không khôi phục active tool:
  - `recover toolchanger: toolchanger active state is still unavailable after toolchanger_recovery_gcode`.
  - `restore original tool: skipped because active tool state was not recovered`.
- Console cho thấy phần nhiễu lớn không thuộc ToolVision: 18 dòng nhiệt trong
  thời gian chờ heater và nhiều dòng KTC/Cartographer khi đổi tool/probe.
  `VERBOSITY=QUIET` không được dùng để che warning/error hoặc log của thành phần
  khác.
- Bằng chứng sampling failure, cleanup failure và console noise đã được gửi
  sang task ToolVision để phân tích/sửa source.

### Khôi phục an toàn và trạng thái chờ

- Sau lỗi Cartographer, năm heater đều target/power 0, T2 còn detected nhưng
  KTC uninitialized.
- Thực hiện `G28` để KTC nhận đúng T2, đổi về `T0`, rồi `G28` đầy đủ lần nữa.
- Trạng thái chờ sau khôi phục: XYZ homed, ToolVision idle, toolchanger ready,
  T0 active/detected, tất cả heater target/power bằng 0.
- Không có offset production nào được ghi hoặc áp dụng. HIL tạm dừng chờ task
  ToolVision cung cấp commit đã test và hướng dẫn cập nhật live.

### CARTOGRAPHER_TOUCH retry — hoàn tất report-only

- Theo yêu cầu người vận hành, thực hiện lại Cartographer với một `G28` đầy đủ
  mới. Điều kiện đầu vào: XYZ homed, KTC ready, T0 active/detected và tất cả
  heater target bằng 0.
- Retry vượt qua vị trí T2 từng lỗi, đo đủ T0–T4, đổi lại T0 và cleanup thành
  công. HTTP trả `ok`; kết quả `WARNING` chỉ vì
  `max_reference_z_drift` chưa được cấu hình, không phải lỗi phép đo.
- Kết quả report-only:
  - T0: `+0.000 mm`.
  - T1: `+0.238 mm`.
  - T2: `-0.270 mm`.
  - T3: `-0.184 mm`.
  - T4: `+0.104 mm`.
  - T0 return drift: `0.000000 mm`.
- History:
  `/home/voron/printer_data/config/Generated-Data/ToolVision/tool-vision-history/20260825-091729-285-z-cartographer_touch-01.json`;
  session `2910375f1d4e47b4a9b081f5b422b778`; duration 232,741 s;
  `cleanup_errors=[]`; `applied=false`.
- Trạng thái cuối: XYZ homed, KTC ready, T0 active/detected, ToolVision idle,
  toàn bộ heater target/power bằng 0.
- G-code store của calibration có một command và 75 response. ToolVision chỉ
  sở hữu đúng ba message ở mức quiet: bắt đầu, đang đo và tóm tắt cuối. Có 20
  dòng nhiệt; các dòng còn lại chủ yếu thuộc KTC/Cartographer.

### Kiểm tra giao diện Latest results trên máy thật

- `_TOOL_VISION_UI_RESULTS` render đủ T0–T4 và đúng các giá trị của retry.
- Phát hiện hai lỗi UI/source template:
  - Hiển thị `Method: switch` dù result vừa đo bằng Cartographer Touch, vì panel
    dùng method mặc định/setup thay vì method của kết quả cuối.
  - Hiển thị drift `n/a` khi giá trị thật là `0.0`, vì biểu thức Jinja coi số 0
    là falsy.
- Hai lỗi và yêu cầu regression test đã được gửi sang task ToolVision. Task
  All-Config không tự sửa source/template này.

## 4. Nhận bản sửa từ task ToolVision và triển khai canary

### Bản sửa do task ToolVision thực hiện

- Task `Đơn giản hóa tự động căn chỉnh` tự điều tra, sửa source, bổ sung test,
  cập nhật tài liệu, commit và push; task All-Config không sửa repository
  ToolVision.
- Commit bàn giao:
  `dd645103c709d1312347dd09193aee586536ca19`
  (`fix: bound switch preflight and label session evidence`).
- GitHub Security Gate đạt:
  `https://github.com/IDcrazy123/Tool-Vision/actions/runs/32831695689`.
- Full gate của source task: 167/167 test; coverage tổng 85%,
  `tool_vision.py` 77%; compile, Ruff/security lint, dependency audit, Bash
  syntax, diff/link và Gitleaks đều đạt.
- Phân tích source xác nhận lỗi switch không phải đảo Y/Z. Preflight cũ lấy
  approach Z `2 - 10 = -8 mm` rồi từ chối điểm lý thuyết dưới Z-min `-5 mm`.
  Primitive probe thật của KTC kẹp target tại axis minimum. Mã mới mirror đúng
  primitive: `max(approach_z - max_distance, axis_minimum_z)` và vẫn từ chối Y
  thật sự ngoài bounds với đúng tên trục.
- Source mới thêm metadata `last_result_mode`/`last_result_method`, giữ drift
  chính xác `0.0`, và phân biệt hook recovery rỗng với hook đã cấu hình.

### Backup và cập nhật máy

- Trước update, tạo và kiểm tra backup 22 file tại:
  - `/home/voron/printer_data/config_backups/tool-vision/manual-before-dd645103-20260825-162745`.
  - `D:\Desktop\Tool-Vision\.local-backups\printer-before-dd645103-20260825-162745`.
- Backup All-Config trước sync panel/hook:
  `extras/backups/pre-toolvision-dd645103-sync-20260825-162745/`, SHA-256
  `6947c09f402f30fe20985d69f40ceb9236ce5f6b9bcf58846b80427d110f7809`.
- Refresh metadata Moonraker xác nhận đúng một commit behind, sau đó update qua
  `/machine/update/client?name=tool-vision`; không chạy `git pull` thủ công.
- Checkout live sau update sạch, branch `codex/compact-mainsail-output`, HEAD
  `dd645103c709d1312347dd09193aee586536ca19`.
- Đồng bộ panel đã sửa và thêm hook riêng của máy:
  `toolchanger_recovery_gcode: INITIALIZE_TOOLCHANGER`. Hook này đã được review
  cho KTC Easy hiện tại; ToolVision vẫn xác minh active state trước restore T0.
- SHA-256 CFG live mới:
  `c53a5368bb4a60a9ea96013d98f15ccb9dc40a09abea2fd619af5629a97190c7`.
- SHA state/result không đổi qua update/restart:
  - state: `3ce127655ace27c2ff5fdd51ef261daf95d6803c359d5b0bed3081b12da75e8f`.
  - result trước HIL hậu-fix:
    `323302857efc57e99f7904b88b928d8779216e9421e014e225050fc2687b9afb`.

## 5. HIL hậu-fix — ba lượt mỗi phương pháp

### Điều kiện chung

- Mỗi lượt đều chạy một `G28` đầy đủ riêng trước calibration.
- Precondition mọi lượt: XYZ homed, KTC ready, T0 active/detected, năm heater
  target bằng 0.
- Dùng 150 °C, T0 reference, `MODE=Z`, method explicit và
  `VERBOSITY=QUIET`; không apply kết quả.

### Physical switch — ba lượt hợp lệ

| Lượt | T1 | T2 | T3 | T4 | Drift T0 | History |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | +0.120 | -0.386 | -0.164 | +0.094 | +0.036 | `20260825-093855-408-z-switch-01.json` |
| 2 | +0.130 | -0.384 | -0.186 | +0.096 | +0.030 | `20260825-094308-892-z-switch-01.json` |
| 3 | +0.114 | -0.384 | -0.186 | +0.090 | +0.034 | `20260825-094715-333-z-switch-01.json` |

- Mean T1–T4: `+0.12133`, `-0.38467`, `-0.17867`, `+0.09333 mm`.
- Range T1–T4: `0.016`, `0.002`, `0.022`, `0.006 mm`.
- Sample SD T1–T4: `0.00808`, `0.00115`, `0.01270`, `0.00306 mm`.
- Mean/range drift T0: `+0.03333 / 0.006 mm`.
- Cả ba lượt cleanup sạch, report-only `WARNING` duy nhất vì
  `max_reference_z_drift` chưa cấu hình. Lỗi preflight `Z target -8` không còn
  tái hiện.

### Cartographer Touch — ba lượt hợp lệ

| Lượt | T1 | T2 | T3 | T4 | Drift T0 | History |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | +0.238 | -0.270 | -0.184 | +0.104 | +0.000 | `20260825-091729-285-z-cartographer_touch-01.json` |
| 2 | +0.248 | -0.266 | -0.196 | +0.102 | +0.014 | `20260825-095200-233-z-cartographer_touch-01.json` |
| 3 | +0.242 | -0.268 | -0.178 | +0.108 | +0.018 | `20260825-095639-268-z-cartographer_touch-01.json` |

- Lượt 1 là retry hợp lệ ngay trước update `dd645103`; commit mới không đổi
  tính toán/probe path Cartographer. Hai lượt sau chạy trực tiếp trên commit
  hậu-fix.
- Mean T1–T4: `+0.24267`, `-0.26800`, `-0.18600`, `+0.10467 mm`.
- Range T1–T4: `0.010`, `0.004`, `0.018`, `0.006 mm`.
- Sample SD T1–T4: `0.00503`, `0.00200`, `0.00917`, `0.00306 mm`.
- Mean/range drift T0: `+0.01067 / 0.018 mm`.
- Sampling failure T2 trước đó không tái hiện trong ba lượt hợp lệ; mọi cleanup
  đều sạch và kết quả không apply.

### So sánh phương pháp và production

| Tool | Switch mean | Cartographer mean | Cartographer - switch | Production hiện hành |
| --- | ---: | ---: | ---: | ---: |
| T1 | +0.12133 | +0.24267 | +0.12133 | +0.228 |
| T2 | -0.38467 | -0.26800 | +0.11667 | -0.295 |
| T3 | -0.17867 | -0.18600 | -0.00733 | -0.268 |
| T4 | +0.09333 | +0.10467 | +0.01133 | -0.014 |

- Hai phương pháp lặp lại tốt trong nội bộ, nhưng có sai khác hệ thống khoảng
  0,12 mm ở T1/T2. Cartographer gần production hơn ở T1/T2; cả hai cùng lệch
  production đáng kể ở T3/T4. Đây không phải bằng chứng đủ để coi production
  hoặc một method là ground truth.
- Không lấy trung bình hai method, không ghi `SAVE_CONFIG`, không chỉnh
  `gcode_z_offset`; cần điều tra tiếp cơ học tiếp xúc switch, bề mặt nozzle và
  hệ đo nếu muốn thay production.
- Cartographer 2026-08-25 tiếp tục gần baseline ba lượt 2026-08-24, với chênh
  mean tuyệt đối tối đa khoảng 0,011 mm trên T1–T4.

## 6. UI, console và trạng thái bàn giao

- `Latest results` sau switch hiển thị đúng `Mode: Z`,
  `Method: Physical switch`, drift `0.0360` và T0–T4.
- Sau Cartographer, panel hiển thị đúng `Method: Cartographer Touch`, drift
  `0.0180`; lỗi method sai và `0.0 -> n/a` đã đóng bằng HIL.
- Panel chính tiếp tục có tám prompt response thay vì mười một.
- Quiet mode giữ đúng ba message do ToolVision sở hữu. Hai lượt switch sạch có
  89–90 response, gồm 30 dòng tiếp xúc probe và 10–11 dòng nhiệt; hai lượt
  Cartographer sạch có 64–65 response, gồm 9–10 dòng nhiệt. Phần còn lại chủ
  yếu thuộc KTC/toolchange/probe và không bị che.
- Có hai lần panel được gọi giữa switch lượt 1, tạo thêm 16 response prompt;
  các dòng đó được tách khỏi lượt console sạch, không quy cho calibration.
- Bằng chứng hậu-fix, thống kê và trạng thái cuối đã được gửi lại task
  `Đơn giản hóa tự động căn chỉnh` để ToolVision lưu vết source/HIL.
- Trạng thái cuối: Klipper ready, XYZ homed, KTC ready, T0 active/detected,
  ToolVision idle, cả năm heater target/power bằng 0. Không áp production
  offset.

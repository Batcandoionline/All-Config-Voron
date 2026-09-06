# Nhật ký — 2026-09-06

## 1. Tích hợp macro đo thời gian gia nhiệt toolhead (MEASURE_TOOL_HEATUP)

### Mục tiêu
Bổ sung macro đo thời gian gia nhiệt đầu in (hotend) từ nhiệt độ A sang B (mặc định 150°C -> 220°C) cho từng tool riêng lẻ (T0–T4), thiết kế theo phong cách chuẩn của `nozzle-clean.cfg`.

### File đã sửa đổi
- `config/Printer-Setup/tool-temp-bench.cfg` — Tạo mới module macro đo thời gian gia nhiệt, bao gồm `MEASURE_TOOL_HEATUP`, `BENCH_TOOL_TEMP`, `STOP_TOOL_HEATUP`, biến trạng thái và delayed_gcode timer.
- `config/printer.cfg` — Include module `Printer-Setup/tool-temp-bench.cfg`.
- `config/README.md`, `config/README.vi.md` — Bổ sung module mới vào danh mục module `Printer-Setup`.
- `README.md`, `README.vi.md` — Bổ sung macro vào bảng tra cứu macro vận hành cốt lõi (nhóm Chẩn đoán).

### Sao lưu
- [printer.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-add-tool-heating-benchmark-macro-20260906-090500/printer.cfg)
- [README.md (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-add-tool-heating-benchmark-macro-20260906-090500/README.md)
- [README.vi.md (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-add-tool-heating-benchmark-macro-20260906-090500/README.vi.md)

### Chi tiết thay đổi
- Thêm macro `[gcode_macro MEASURE_TOOL_HEATUP]` với các tham số:
  - `TOOL` / `T` (0..4, mặc định tool đang gắn hoặc T0).
  - `START_TEMP` / `TEMP_A` / `START` / `A` (mặc định 150°C).
  - `TARGET_TEMP` / `TEMP_B` / `TARGET` / `B` (mặc định 220°C).
  - `TIMEOUT` (mặc định 180s).
  - `PARK_BUCKET` (tùy chọn di chuyển về hộc xả X=320 Y=-8.0 nếu tool active).
  - `COOLDOWN` (tự động tắt gia nhiệt sau khi đo xong).
- Tích hợp `[delayed_gcode _TOOL_HEATUP_TIMER]` với nhịp 0.5s đo thời gian thực, hiển thị tiến trình live trên `M117` và console Mainsail.
- Tự động tính toán độ tăng nhiệt $\Delta T$, tổng thời gian (giây) và tốc độ gia nhiệt trung bình (°C/s).
- Thêm lệnh ngắt khẩn cấp `[gcode_macro STOP_TOOL_HEATUP]` và alias tiện dụng `[gcode_macro BENCH_TOOL_TEMP]`.

### Lý do
Giúp người vận hành kiểm tra công suất thanh nhiệt, đánh giá sức khỏe cảm biến nhiệt điện trở (thermistor), kiểm chứng hiệu năng PID và phát hiện sớm các đầu in bị suy hao nhiệt trên hệ thống Voron StealthChanger 5-Tool mà không cần bấm giờ thủ công.

### Kiểm tra
- Kiểm tra cú pháp: Đạt (cú pháp Jinja2 và Klipper macro hợp lệ, không xung đột).
- Kiểm tra an toàn: Có guard kiểm tra biên nhiệt độ ($30^\circ\text{C} \le \text{Start} < \text{Target} \le 290^\circ\text{C}$), timeout ngắt khẩn cấp sau 180s.
- Kiểm tra git: `git diff --check` sạch, không lỗi whitespace.

### Kết quả
Đã thêm thành công macro đo thời gian gia nhiệt toolhead độc lập, chuẩn xác, sẵn sàng sử dụng trên Mainsail.

### Vấn đề còn lại
Không có.

---

## 2. Khắc phục lỗi quyền thực thi deployment scripts và tối ưu Moonraker Update Manager

### Mục tiêu
Khắc phục sự cố không thể cập nhật cấu hình qua Moonraker Update Manager trên giao diện Mainsail khi thêm macro `tool-temp-bench.cfg`.

### Nguyên nhân gốc
1. **Thiếu quyền thực thi (`chmod +x`)**: Các script triển khai (`config/scripts/install.sh`, `config/scripts/update.sh`, `config/scripts/cleanup-voron.sh`) được lưu trữ trong Git index với mode `100644`. Moonraker Update Manager yêu cầu `install_script` phải có quyền thực thi. Khi Moonraker chạy script trên Linux, hệ thống trả về lỗi `Permission denied (code 126)`, làm quá trình update bị dừng khẩn cấp.
2. **Xung đột Shallow Clone (`--depth=1`) & Sparse Checkout**: Trước đó tài liệu hướng dẫn dùng shallow clone kết hợp sparse checkout. Khi commit `418086b` thay đổi cả các file ngoài phạm vi sparse checkout, Git trên máy in không thể phân giải commit behind dẫn đến trạng thái `INVALID` hoặc `DIRTY`.

### File đã sửa đổi
- `config/scripts/install.sh` — Cấp quyền thực thi `100755` trong Git index.
- `config/scripts/update.sh` — Cấp quyền thực thi `100755` trong Git index.
- `config/scripts/cleanup-voron.sh` — Cấp quyền thực thi `100755` trong Git index.
- `extras/docs/danh-sach-doi-chieu-va-huong-dan-update-mainsail.md` — Cập nhật quy trình thiết lập repo chuẩn trên máy in, loại bỏ shallow clone để tương thích hoàn toàn với Moonraker Update Manager.

### Lý do
Đảm bảo Moonraker Update Manager trên Mainsail có thể tự động thực thi script cài đặt an toàn sau mỗi lần `git pull` mà không bị chặn quyền hoặc xung đột Git.

### Kiểm tra
- Đã chạy `git update-index --chmod=+x` cho cả 3 script shell.
- Kiểm tra `git ls-files --stage`: Mode đã chuyển sang `100755` chính xác.
- Kiểm tra tài liệu: Hướng dẫn đồng bộ và rõ ràng.

### Kết quả
Đã giải quyết triệt để lỗi phân quyền thực thi trên Git repo, sẵn sàng để đồng bộ trơn tru lên máy in qua Update Manager.

---

## 3. Cập nhật giới hạn trục Z và đồng bộ PID Extruder T0 từ máy in

### Mục tiêu
- Nâng giới hạn vận tốc trục Z (`max_z_velocity`) từ 70 mm/s lên 80 mm/s và gia tốc trục Z (`max_z_accel`) từ 900 mm/s² lên 1000 mm/s² theo yêu cầu của người vận hành.
- Kéo và đồng bộ các tham số hiệu chuẩn PID mới nhất của đầu phun T0 (`[extruder]`) từ máy in thực tế (`192.168.1.43`) về kho cấu hình Git để tránh bị ghi đè dữ liệu cũ khi cập nhật.

### File đã sửa đổi
- `config/printer.cfg` — Thay đổi `max_z_velocity: 80`, `max_z_accel: 1000` và cập nhật các tham số PID `[extruder]`:
  - `pid_kp = 23.911` (cũ: 39.664)
  - `pid_ki = 7.971` (cũ: 12.592)
  - `pid_kd = 17.933` (cũ: 31.235)

### Sao lưu
- [printer.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-update-z-limits-and-t0-pid-20260906-101100/printer.cfg)
- [README.md (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-update-z-limits-and-t0-pid-20260906-101100/README.md)

### Chi tiết thay đổi
- Kết nối tới Moonraker API trên máy in (`192.168.1.43:7125`) để tải cấu hình runtime `printer.cfg` mới nhất.
- So sánh `git diff` khối `#*# <SAVE_CONFIG>`: Xác nhận các đầu in T1–T4, Cartographer scan/touch model, Bed Mesh 55x55 và Axis Twist Compensation hoàn toàn trùng khớp 100%; chỉ có PID của T0 vừa được người dùng hiệu chuẩn lại trên máy in.
- Cập nhật thông số PID T0 mới vào `config/printer.cfg`.
- Điều chỉnh `max_z_velocity: 80` và `max_z_accel: 1000` trong section `[printer]`.

### Lý do
Tăng tốc độ di chuyển trục Z khi chuyển đổi đầu in (tool change) và bảo toàn chính xác dữ liệu hiệu chuẩn PID nhiệt độ thực tế của hotend T0 trên máy in.

### Kiểm tra
- Đối chiếu cú pháp file `printer.cfg`: Hợp lệ, giữ nguyên toàn bộ comment và khối SAVE_CONFIG.
- Kiểm tra `git diff`: Khớp đúng các thay đổi mong muốn.

### Kết quả
Đã cập nhật thành công giới hạn Z và đồng bộ chính xác dữ liệu PID T0 vào Git repo.

---

## 4. Tích hợp và thử nghiệm hệ thống Tool-Klipper-Calibration (TKC)

### Mục tiêu
- Nghiên cứu kiến trúc dự án mã nguồn mở tự phát triển `IDcrazy123/Tool-Klipper-Calibration` (TKC).
- Tích hợp module cấu hình TKC vào dự án `Voron 5 Tool`, thiết lập toạ độ an toàn $Z=40\text{mm}$, kết nối camera macro MF-500 và trạm Cartographer Touch V4.
- Triển khai daemon thị giác máy tính trên máy in (`192.168.1.43`), điều khiển thử nghiệm lấy dữ liệu log thực tế để phân tích cơ chế hoạt động, đánh giá độ ổn định và chỉ ra các điểm lưu ý kỹ thuật/rủi ro.

### File đã sửa đổi
- `config/Printer-Setup/tool-calibrator.cfg` — Tạo mới module cấu hình TKC: khai báo section `[tool_calibrator]`, tham số trạm camera ($X:170, Y:20, Z:40$), safe_z 40mm, hook điều khiển đèn LED chống lóa và các macro vận hành (`CALIBRATION_TEST_VISION`, `CENTER_NOZZLE`, `CALIBRATE_ALL_TOOLS`).
- `config/printer.cfg` — Include module `Printer-Setup/tool-calibrator.cfg`.
- `config/Printer-Setup/calibration-probe.cfg` — Đổi tên macro cũ `[gcode_macro CALIBRATION_STATUS]` thành `[gcode_macro KTAMV_CALIBRATION_STATUS]` để tránh xung đột với lệnh C/Python cùng tên của TKC.

### Sao lưu
- [printer.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-integrate-tkc-testing-20260906-173500/printer.cfg)
- [calibration-probe.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-integrate-tkc-testing-20260906-173500/calibration-probe.cfg)

### Chi tiết thay đổi & Thiết lập môi trường thực tế
1. **Thiết lập Daemon Thị giác nền trên Host (`192.168.1.43`):**
   - Clone repo `Tool-Klipper-Calibration` vào `/home/voron/Tool-Klipper-Calibration`.
   - Cấu hình user systemd service `~/.config/systemd/user/tool_calibrator.service` chạy trên cổng `8090` với môi trường Python `~/ktamv-env`.
   - Tạo các liên kết tượng trưng (symlinks) từ `klippy/extras/` của TKC vào `/home/voron/klipper/klippy/extras/` (`tool_calibrator.py`, `tool_calibrator_station.py`, `safe_navigator.py`, `config_manager.py`, `z_backends/`).
2. **Cấu hình an toàn trong Klipper:**
   - Đặt `safe_z: 40.0` và toạ độ mục tiêu camera `camera_target_x: 170.0`, `camera_target_y: 20.0`, `camera_target_z: 40.0`.
   - Cấu hình hook tắt LED đầu in (`_CALIBRATION_NOZZLE_LED_OFF`) tự động dập tắt `T{tool}_LED` khi vào trạm để chống lóa chói sensor camera.
   - Định tuyến file lưu trữ offset cách ly vào `Generated-Data/tool_offsets.cfg` để bảo vệ cấu hình gốc.

### Kết quả kiểm tra & Đo đạc thực tế
- **Khởi động Klipper:** Thành công nạp module `tool_calibrator`, trạng thái Klipper chuyển sang `ready`.
- **Thử nghiệm quang học trực tiếp (`CALIBRATION_TEST_VISION`):**
  - Số mẫu: 3/3 frame nhận diện thành công $100\%$.
  - Toạ độ tâm lỗ vòi phun T0: $U = 679.35\text{ px}, V = 311.65\text{ px}$ (độ phân giải 1280×720).
  - Bán kính nhận diện: $R = 22.70\text{ px}$.
  - Độ tin cậy (Confidence): $98.0\%$.
  - Độ phân tán (Dispersion): $0.20\text{ px}$ (đạt độ ổn định dưới nửa pixel).
  - Thuật toán khớp: **Tier 0 Curvature (Symmetric)** — trích xuất độ cong và tính nhất quán gradient $360^\circ$ hoàn hảo, hoàn toàn không bị đánh lừa bởi 2 vệt lóa sáng hình tam giác trên nón nozzle TZ V6 2.0.
- **Tải hệ thống:** Thời gian xử lý frame $\approx 0.4\text{s}$, không gây trễ reactor Klipper, không gây quá tải CPU hay drop packet CAN bus.

### Các điểm lưu ý & Khuyến nghị khắc phục (Dự án tự phát triển TKC)
1. **Xung đột tên lệnh Gcode/Macro (`CALIBRATION_STATUS`):**
   - Klipper không cho phép một module Python đăng ký lệnh trùng tên với một `[gcode_macro]` đã tồn tại trong cấu hình.
   - *Khắc phục đã thực hiện:* Đổi tên macro kTAMV cũ thành `KTAMV_CALIBRATION_STATUS`.
   - *Khuyến nghị cho TKC:* Trong `tool_calibrator.py`, nên thêm tiền tố rõ ràng như `TKC_STATUS` hoặc kiểm tra `self.gcode.commands` trước khi đăng ký để tránh xung đột trên các máy in có macro cộng đồng.
2. **Nguy cơ lỗi trùng Section `[tool T*]` khi lưu file cấu hình:**
   - Trong Klipper, parser không cho phép trùng lặp section header (ngoại trừ khối SAVE_CONFIG do `save_config.py` quản lý).
   - Nếu TKC lưu file `tool_offsets.cfg` chứa `[tool T1]` mà file đó được `[include]` vào `printer.cfg`, Klipper sẽ báo lỗi dừng máy `Section 'tool T1' already exists`.
   - *Khuyến nghị cho TKC:* Với các hệ thống chạy KTC-Easy, nên hỗ trợ backend lưu offset qua macro KTC (`SAVE_TOOL_PARAMETER T={t} PARAMETER=gcode_x_offset`) hoặc chỉ lưu tọa độ trạm mà không tự động tạo lại header `[tool T*]`.
3. **Đường dẫn Snapshot trên Crowsnest Camera-Streamer:**
   - Camera-streamer WebRTC phục vụ endpoint ảnh tĩnh tại `/snapshot.jpg`. Cấu hình cũ `/?action=snapshot` của mjpg-streamer trả về mã lỗi 404.
4. **Import tương đối trong Server Daemon:**
   - File `server/tool_calibrator_server.py` chứa các lệnh import dạng `from .stream_grabber ...`. Cần bắt buộc chạy dưới dạng package module (`python3 -m server.tool_calibrator_server`).

### Vấn đề ghi nhận thêm trong quá trình thử nghiệm
- Lỗi `Unknown command: "AUTO_TEACH_CAMERA"`: Macro này nằm trong `macros/safe_staging_macros.cfg` nhưng chưa được tự động đăng ký trong Python hay include trong cấu hình mẫu.
- Lỗi `Centering failed: [ERR_CAM_101] Cannot connect to Vision Service on http://127.0.0.1:8090/calculate_offset: HTTP Error 400: BAD REQUEST`: Khi chưa hoàn tất `CALIBRATE_CAMERA_SCALE`, biến `mpp` và `transform_matrix` là `None`. Khi gọi `/calculate_offset`, solver ném ngoại lệ khiến Flask trả về HTTP 400. Đây là lỗi phụ thuộc vòng (chicken-and-egg bug) cản trở việc căn tâm ban đầu.

---

## 5. Khôi phục trạng thái máy in về trước khi cài TKC theo yêu cầu

- **Lý do:** Người dùng yêu cầu khôi phục hoàn toàn cấu hình máy in về trạng thái gốc trước khi cài đặt TKC để tập trung hoàn thiện mã nguồn repo TKC.
- **Thư mục sao lưu:** `extras/backups/revert-tkc-20260906-174400/`
- **Các bước thực hiện:**
  1. Loại bỏ dòng `[include Printer-Setup/tool-calibrator.cfg]` trong `config/printer.cfg`.
  2. Đổi lại macro `[gcode_macro KTAMV_CALIBRATION_STATUS]` về nguyên trạng `[gcode_macro CALIBRATION_STATUS]` trong `config/Printer-Setup/calibration-probe.cfg`.
  3. Xóa file `config/Printer-Setup/tool-calibrator.cfg`.
  4. Trên máy in (`192.168.1.43`):
     - Dừng và xóa service `tool_calibrator.service` (`systemctl --user stop/disable`).
     - Gỡ bỏ toàn bộ symlink Klipper extras liên quan (`tool_calibrator*`, `safe_navigator*`, `config_manager*`, `z_backends`).
     - Xóa file `tool-calibrator.cfg` trên máy in.
     - Đồng bộ file `printer.cfg` và `calibration-probe.cfg` đã khôi phục.
     - Khởi động lại firmware Klipper qua Moonraker API (`POST /printer/restart`).
  5. **Kiểm tra trạng thái:** Klipper đã khởi động lại thành công và đạt trạng thái `ready` ("Printer is ready"). Không còn daemon hay module phụ trợ nào của TKC chạy ngầm.



## 6. Tái tích hợp TKC 780a492 và chạy thử XY trên máy thật

### Mục tiêu
Đọc toàn bộ quy tắc `.agents/`, cấu hình production và source TKC mới; tích hợp có thể hoàn tác, chạy máy thật `192.168.1.43` và thu bằng chứng hoạt động. Người dùng xác nhận dùng `G28` thông thường, nâng Z lên 40 trước khi đổi tool.

### File đã sửa đổi / bổ sung
- `extras/experiments/tkc-20260906/` — cấu hình thử nghiệm, user service, tọa độ/ma trận camera đã đo, README, REPORT, CSV và bằng chứng.
- **Live only:** `printer.cfg` thêm một include `/home/voron/printer_data/tkc-experiment/tool-calibrator.cfg` trước SAVE_CONFIG. Payload production `config/` trong Git giữ nguyên.
- `.agents/KNOWN_ISSUES.md` tại workspace — cập nhật lỗi X đã được xử lý theo nhật ký 26/08 mục 11 và bổ sung các vấn đề TKC. Thư mục này nằm ngoài git repo; patch được lưu cùng bộ thử nghiệm.

### Sao lưu
- [pre-tkc-hil-20260906-180201](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-tkc-hil-20260906-180201/README.md>) — bản gốc local/live printer.cfg, calibration-probe.cfg và năm file tool; các trạng thái cấu hình thử nghiệm trước khi sửa.
- Remote: `/home/voron/printer_data/config_backups/pre-tkc-hil-20260906-180420/`.
- Tọa độ trạm được sao lưu trước phép đo scale; TKC cũng tạo backup riêng cho station-data.cfg.

### Triển khai và kiểm tra
- Pin source tại `780a492bad45399698491a355ab62db6954da9d7`, không patch source.
- Venv riêng `~/tkc-env` dùng OpenCV hệ thống 4.6.0, NumPy 1.24.2; Flask 3.0.3 và Waitress 3.0.2. Không chạy installer upstream, không đổi apt hoặc venv kTAMV.
- User service `tool-calibrator-experiment.service`, bind loopback `127.0.0.1:8090`; liên kết các extras vào Klipper. Không thêm updater tự động.
- 78/78 unit tests upstream đạt trên host (5,640 giây).
- Soft RESTART lần đầu giữ module Python từ lần cài trước nên báo trùng `CALIBRATION_STATUS`; restart **dịch vụ Klipper** nạp bản mới thành công. Không cần đổi tên macro production.
- `DUMP_TMC STEPPER=stepper_x`: `DRV_STATUS: 80190000 cs_actual=25 stst=1`; G28 thành công.
- Chỉ thử XY lạnh, `SAVE_CONFIG=0`, `CALIBRATE_Z=0`, `WIGGLE=0`, giữ ngưỡng 0,015 mm và 5 bước. Backend Z có hook báo lỗi để chưa thể probe bằng TKC.

### Số đo camera và kết quả vòng lặp
- Kiểm tra ảnh đầu: 7/7 frame, UV 680,15 / 310,50 px, radius 22,50 px, dispersion 0,20 px.
- Dịch độc lập ±0,5 mm xác nhận cả X/Y ảnh đảo chiều so với fallback của TKC: du/dX=-44,0; dv/dY=-42,95 px/mm. Chỉ dùng ma trận đo thật để điều khiển; không cho fallback điều khiển máy.
- Camera scale native đạt đủ bốn hướng: **0,022750 mm/px**, affine solved. Trạm đã lưu **X170,923 Y18,905 Z40**, approach X171,456 Y43,920.
- **Vòng 1 và vòng 2:** hoàn thành đủ T0–T4 và trở về T0.
- **Vòng 3:** dừng ở T2 lúc 18:17:38 với `ERR_CV_202`; burst cuối dispersion 5 px, không hội tụ ngưỡng 0,015 mm sau 5 bước. Không tăng tolerance hoặc ép chạy lại để lấy đủ vòng đạt.
- T2 sau lỗi đứng yên nhận 20/20 frame, V chỉ dao động 0,10 px; chưa đủ bằng chứng quy lỗi cho nhiễu quang học liên tục. Cần phân biệt lag/settling sau chuyển động và số bước hội tụ.
- Hai vòng hoàn chỉnh cho biên độ lặp lớn nhất **0,022 mm X / 0,032 mm Y**. Chỉ hai vòng đạt, không xem đây là chứng nhận độ chính xác.
- Bảng từng tool, số đo vòng 3 chưa hoàn chỉnh và phân tích chi tiết ở `REPORT.md`, `xy-measurements.csv`, `summary.json`. Cache sau vòng lỗi vẫn là số liệu vòng 2; không gộp thành vòng 3.

### Điểm cần lưu ý cho TKC
1. Fallback MPP 0,040 và hướng trục giả định có thể ra lệnh sai chiều; cần bootstrap Jacobian từ chuyển động nhỏ có kiểm soát.
2. Confidence 98% là hằng số theo thuật toán. Burst gate 15 px quá rộng so với tolerance 0,015 mm; cần kiểm tra số frame hợp lệ, cluster và độ phân tán theo mm.
3. Trạng thái API không đặt RUNNING, vẫn có thể hiện SUCCESS cũ trong khi chạy. Sau lỗi KTC chuyển về uninitialized nên phải kiểm tra tool thực/detected rồi INITIALIZE_TOOLCHANGER.
4. Request qua nginx port 80 bị HTTP 504 sau 60,020 giây nhưng chuỗi tiếp tục. Không gửi lại lệnh; dùng Moonraker 7125 trực tiếp hoặc WebSocket. Vòng 2 qua 7125 chạy 173,714 giây và trả ok.
5. `DRY_RUN=1` vẫn đổi tool/căn XY. `[tool_offsets]` mới chỉ lưu/đọc số, chưa áp offset vào KTC.
6. Ghi chú mục 4 trước đó về mọi section trùng đều gây lỗi là quá rộng: parser Klipper trên máy dùng `strict=False`, có thể ghi đè option. Không dùng section trùng để tạo quyền sở hữu offset không rõ ràng.
7. Cần phân biệt hardware Cartographer V3 và API plugin 1.9.0. Chưa chạy/đánh giá backend Z của TKC trong phiên này.

### Xác minh cuối và tình trạng máy
- Sau restart cả daemon và Klipper, daemon bắt đầu với matrix_solved=false; CENTER_NOZZLE khôi phục đúng MPP/ma trận từ file và hội tụ. Bỏ manual camera X/Y khỏi overlay để trạm đã học không bị giá trị cũ ghi đè sau restart.
- Máy **ready**, XYZ homed, T0 active/detected, pose **X170,8882 Y18,8799 Z40**; heater targets/power bằng 0, tool LEDs tắt.
- Ảnh cuối: 7/7 frame, dispersion 0,35 px. Matrix solved, MPP 0,022750, session lock đã nhả.
- Năm file tool và calibration-probe.cfg giống byte bản gốc; SAVE_CONFIG giữ nguyên. Không ghi offset production, không hiệu chuẩn Z, không gia nhiệt, không thử in.
- Phân tích 918 dòng Stats trong toàn cửa sổ thử: bảy node CAN active, RX/TX error và TX retries bằng 0; không có lỗi scheduling/shutdown. **print_stall đã tăng tới 2 trước restart**, sau restart về 0; chưa xác định nguyên nhân, không kết luận runtime không gây stall.
- Raw log: [klippy.log](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/logs/tkc-20260906/klippy.log>), [moonraker.log](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/logs/tkc-20260906/moonraker.log>), [vision-service.log](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/logs/tkc-20260906/vision-service.log>). Log lớn không đưa lên Git; console, ảnh và JSON rút gọn được theo dõi.

### Kết quả / vấn đề còn lại
Tích hợp thử nghiệm hoạt động, đã có số liệu và lỗi thực tế tái hiện. **Chưa đủ ổn định để tự áp offset hoặc dùng không giám sát.** Giữ TKC như overlay thử nghiệm, source pin, Z guard và SAVE_CONFIG=0; tiếp tục sửa bootstrap, bộ lọc frame, số bước căn tâm và state machine ở dự án TKC trước khi đánh giá production.

## 7. Cài TKC b6c3328 mới và đo lại ba vòng trên máy thật

### Mục tiêu
Theo yêu cầu người dùng, cài bản mới GitHub lên máy `192.168.1.43`, đo thực tế, kiểm tra nhu cầu gỡ kTAMV và chỉ ra lỗi/cải tiến TKC. Tiếp tục dùng xác nhận G28 thông thường và Z40 trước đổi tool; đã đọc lại các quy tắc `.agents/`.

### Sao lưu
- [pre-tkc-b6c3328-20260906-190133](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-tkc-b6c3328-20260906-190133/README.md>) — printer.cfg, ktamv.cfg, overlay, station, user services, trạng thái dịch vụ, source HEAD và lịch sử backup station từ máy thật; kèm KNOWN_ISSUES.md trước sửa.
- Remote: `/home/voron/printer_data/config_backups/pre-tkc-b6c3328-20260906-190126/`.

### File và triển khai
- Nâng `~/Tool-Klipper-Calibration` từ `780a492` lên `b6c332862a87043238b068dd55b5f5ee433efdb6` (0.8.18).
- Source gốc kiểm tra trong worktree riêng: thiếu import `Tuple`, `Optional`, server không import được; 91 tests chạy với 10 errors. Bổ sung đúng hai typing import, lưu `startup-imports.patch`; sau vá **91/91 tests đạt trong 6,938 s**. Chỉ vá lỗi khởi động, không sửa thuật toán để che lỗi đo.
- Cập nhật mô tả revision trong overlay và user service; restart vision và **process Klipper**. Không dùng installer upstream hoặc thay dependency môi trường. Symlink extras và include thử nghiệm từ phiên trước giữ nguyên.
- Sau sao lưu, bỏ MPP/ma trận cũ khỏi station thử nghiệm để kiểm tra bootstrap native; giữ waypoint đã đo. Backend Z vẫn chặn bằng macro báo lỗi.
- kTAMV dùng cổng 8086, TKC dùng 8090 loopback. Tạm dừng ktamv-server khi đo, bật lại sau đó; không phát hiện xung đột cần gỡ source/config/include.
- Thêm báo cáo, README, bản vá, cấu hình, ảnh, JSON, CSV, console, script tái hiện offline trong `extras/experiments/tkc-b6c3328-20260906/`. Production Git `config/` không thay đổi.

### Kiểm tra máy và camera
- Klipper process mới bắt đầu **19:03:02 giờ máy in**. G28 và Z40 thành công, T0 đúng active/detected, heater targets bằng 0.
- Chưa có matrix: `/calculate_offset` từ chối HTTP 400 `ERR_CV_203`; không chạy correction fallback.
- `CALIBRATE_CAMERA_SCALE DISTANCE=0.5`: đủ bốn hướng, X 21,90/22,00 px, Y 20,55/22,60 px; **MPP=0,023000 mm/px**, affine solved. Tự căn tâm sau fit, lưu target **X170,910 Y18,917 Z40**, approach X171,456 Y43,920.
- Đo XY bằng `TKC_TEST_XY`: SAVE_CONFIG=0, CALIBRATE_Z=0, WIGGLE=0, SAMPLES=3, tolerance 0,015 mm không đổi; default mới 8 bước.

### Kết quả đo thực tế

| Tool | Vòng 1 X/Y (mm) | Vòng 2 X/Y (mm) | Vòng 3 X/Y (mm) |
|---|---:|---:|---:|
| T1 | -0,166 / -0,274 | -0,159 / -0,287 | -0,157 / -0,296 |
| T2 | +0,872 / +0,270 | +0,886 / +0,266 | +0,891 / +0,256 |
| T3 | +0,351 / +0,536 | +0,369 / +0,527 | +0,377 / +0,529 |
| T4 | +0,150 / +0,214 | +0,173 / +0,225 | +0,163 / +0,192 |

- **3/3 vòng hoàn chỉnh**, thời gian TKC 165,30 / 172,22 / 171,77 s. Biên độ lặp lớn nhất **0,026 mm X / 0,033 mm Y**; ba vòng chưa đủ chứng nhận độ chính xác tuyệt đối. T0 là gốc riêng mỗi vòng.
- Trong vòng 3, gửi đúng một `CALIBRATION_ABORT` khi T1 active. Request bị giữ **156,027 s**, cả vòng vẫn chạy tới T4 và trả T0, sau đó báo `No calibration cycle is currently running.` API trả ok không có nghĩa đã hủy.
- API RUNNING/valid=false hoạt động, nhưng `active_tool` vẫn là 4 sau khi tool thực đã về T0; duration trong lúc chạy vẫn 0.

### Lỗi và cải tiến đã xác nhận
1. **Khởi động:** thiếu typing imports; bản vá tối thiểu đã cài và lưu để upstream sửa.
2. **Abort:** handler đi chung G-code mutex với chuỗi calibration đồng bộ. Cần webhook ngoài hàng đợi/state machine và test hai request đồng thời.
3. **Dấu bù XY cho Z:** raw offset là carriage target trừ reference, nhưng code trạm Z lại trừ. Mô phỏng X68, offset +0,865: thực tế code ra X67,135, hình học đúng cần X68,865, lệch 1,730 mm. Không thử lỗi này bằng probe thật; giữ Z guard.
4. **Session:** scale tiếp tục approach sau lỗi lấy lock; health lỗi sau khi đã lấy lock ở full cycle không nhả lock/finalize end_time. Đã tái hiện offline.
5. **Trạng thái scale:** centering sau solve thất bại vẫn lưu và báo CAMERA CALIBRATION SUCCESS. Đã tái hiện offline.
6. **Burst gate:** `max(6 px, 0,08/MPP)` thành 0,138 mm tại scale này, vẫn nhận cụm 5 px = 0,115 mm. Đã tái hiện offline; cần gate theo mm và frame freshness.
7. **Runtime:** print_stall tăng tới 3, mỗi lần quan sát gần đoạn trả T4→T0. Có một `BlockingIOError: [Errno 11] Resource temporarily unavailable` trong `_respond_raw` khi ghi G-code response ở T3 vòng 3; đo vẫn hoàn tất. Có reactor busy 0,069 s gần chuyển T3/T4. Chưa xác định nguyên nhân buffering/scheduling, không quy lỗi cơ khí/CAN.

### Log và xác minh cuối
- Phân tích **811 Stats samples** từ process mới: bảy CAN node active, RX/TX error và retries bằng 0; không thấy Timer too close, mất liên lạc, short-to-supply hoặc shutdown trong cửa sổ này. Ngoại lệ phản hồi G-code nêu trên được ghi riêng.
- Raw logs: [klippy.log](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/logs/tkc-b6c3328-20260906/klippy.log>), [moonraker.log](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/logs/tkc-b6c3328-20260906/moonraker.log>), [vision-service.log](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/logs/tkc-b6c3328-20260906/vision-service.log>). Log lớn không commit; trích đoạn và kết quả phân tích được theo dõi.
- Restart riêng vision sau đo: health mất MPP/matrix như dự kiến; CENTER_NOZZLE nạp lại từ file và hội tụ. Không restart/rehome Klipper lần nữa sau đo.
- Cuối kiểm tra: **ready, XYZ homed, T0 active/detected, X170,9101 Y18,8941 Z40**, heater targets/power bằng 0. Vision 7/7 frame, dispersion 0,40 px, confidence score 99%; session lock đã nhả.
- Hai user services TKC/kTAMV active/running, NRestarts=0. Printer.cfg/ktamv.cfg giống byte backup đầu phiên, năm tool cfg và calibration-probe.cfg khớp hash production đã xác minh, runtime offsets trước/sau giống nhau.
- Đồng hồ PC nhanh hơn máy in khoảng 9 s; timeline/request dùng giờ PC, run record/log dùng giờ máy in. Thời lượng so sánh trong cùng đồng hồ.

### Kết quả và giới hạn
Đã cài và đo bản mới, bootstrap và ba vòng XY thành công sau vá import. **Chưa dùng TKC cho XYZ không giám sát hoặc tự áp offset.** Cần ưu tiên sửa abort ngoài hàng đợi, dấu bù Z, cleanup phiên và gate chất lượng. Không gia nhiệt, probe Z, áp offset hay thử in. Báo cáo chi tiết: [REPORT.md](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/experiments/tkc-b6c3328-20260906/REPORT.md>).

## 8. Xác minh TKC đã cài thật và đối chiếu hướng dẫn cài đặt

### Yêu cầu và phạm vi
Người dùng hỏi TKC đã cài lên máy hay chỉ chạy thử Python, cách cài có theo hướng dẫn không và yêu cầu xác minh báo cáo để sửa đổi. Kiểm tra chỉ đọc qua SSH, proc/systemd, Moonraker và source đúng revision b6c3328; không chạy đo mới, restart, đổi cấu hình, dependency hoặc offset.

### Bằng chứng cài thật
- Host `voron-local`, vision PID **7088**, chạy `~/tkc-env/bin/python -m server.tool_calibrator_server` tại 127.0.0.1:8090, 2 workers, camera snapshot thật. User service active/running, enabled; Linger=yes. Không reboot để thử trong phiên audit.
- Process Klipper thật dùng `/home/voron/printer_data/config/printer.cfg`, có include overlay TKC; năm file extras và thư mục z_backends liên kết tới repo TKC thật.
- `gcode/help` trả các lệnh core và `TKC_TEST_XY`; `configfile.settings` có macro wrapper thật, gọi CALIBRATE_TOOL_OFFSETS. Object runtime còn giữ run `run_1788696733` và đúng kết quả vòng 3 trong báo cáo.
- Môi trường ảo Python là cách chạy daemon thật, không đồng nghĩa máy giả lập. Script ở PC gửi G-code tới Moonraker; Klipper và camera trên máy thật thực thi ba vòng XY.

### Những điểm khác với hướng dẫn/installer
- Không chạy `scripts/install.sh`; cài thủ công để thử nghiệm XY trên phần cứng.
- Dùng **user service `tool-calibrator-experiment`**, không phải system service `tool_calibrator`; unit chuẩn báo not-found là đúng với cách cài này.
- Venv `~/tkc-env` bật system-site-packages, dùng Debian OpenCV4.6.0 (`python3-opencv`), không có distribution pip `opencv-python-headless`. OpenCV đạt mốc phiên bản số tối thiểu nhưng chưa xác minh tương đương build/hiệu năng với bản pip. Flask3.0.3, Waitress3.0.2, NumPy1.24.2, requests2.28.1 và urllib3 1.26.12 đều nằm trong dải yêu cầu.
- Chưa include hai bộ macro tiện ích upstream; các alias CALIBRATE_ALL_TOOLS, CALIBRATE_TOOLS_XY, CALIBRATE_TOOL_XY, CALIBRATE_CAMERA, GOTO_CAMERA_TARGET không có trên máy. Các lệnh core vẫn hoạt động.
- Chưa tích hợp ASVC/Update Manager; file station tách riêng, chưa cấu hình áp/lưu offset tool. Chưa nghiệm thu full XYZ.

### Lỗi hướng dẫn được xác minh
1. Ví dụ install guide dùng `default_station`, `lift_z_safe`, `center_x/y`, `matrix_xx/...`, `z_switch_pin` không khớp option mà module hiện tại đọc. Klipper có kiểm tra unused option; không nạp block sai này vào máy thật.
2. Tái hiện offline bằng **ConfigFileReader của Klipper đang cài**: `[include ~/Tool-Klipper-Calibration/macros/tool_calibrator_macros.cfg]` bị ghép thành `/home/voron/printer_data/config/~/Tool-Klipper-Calibration/macros/tool_calibrator_macros.cfg` và báo không tồn tại. Installer cũng in đường dẫn `macros/...` nhưng không copy macro tới config root.
3. SOP gọi AUTO_TEACH_CAMERA với AUTO_CENTER=1 trước CALIBRATE_CAMERA, trong khi b6c3328 chặn centering chưa có matrix. Cần teach waypoint nhìn thấy nozzle với AUTO_CENTER=0, đo scale/matrix, rồi căn tâm. Lần thử mục 7 xóa matrix nhưng giữ waypoint đã đo từ trước; không phải nghiệm thu khởi tạo trống hoàn toàn.
4. Guide ghi health `healthy`, actual là `ok`; installer chỉ dùng curl -s, không kiểm HTTP status/JSON identity, vẫn in hoàn tất khi kiểm tra health cảnh báo. Cần kiểm tra fail-closed và sửa import trước.
5. Macro include/Khởi động Klipper là bước người dùng phải làm tiếp; không coi installer đã tự hoàn tất commissioning. Backup `.bak` cố định cũng không đáp ứng quy tắc không ghi đè backup của kho máy in.

### Sửa báo cáo và phân loại bằng chứng
- Bổ sung ngay đầu REPORT.md/README.md: **đã cài trên máy thật bằng triển khai thủ công có tùy chỉnh; chưa cài nguyên bộ theo hướng dẫn upstream**.
- Thêm INSTALLATION_AUDIT.md: bảng đối chiếu từng thành phần, đường dẫn source đúng SHA và mức xác minh từng lỗi. XY, abort và log runtime là thực tế; Z-sign/session/false-SUCCESS/gate là mô phỏng offline; 91 tests là kiểm tra phần mềm. Không suy rộng lỗi scheduling/CV tới mọi môi trường cài đặt TKC.
- Thêm script audit chỉ đọc và `evidence/installation-audit.json`. `.agents/KNOWN_ISSUES.md` được bổ sung, patch lưu cùng experiment vì thư mục agent nằm ngoài Git.

### Sao lưu và kiểm tra
- [pre-tkc-install-audit-20260906-193105](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-tkc-install-audit-20260906-193105/BACKUP-RECORD.md>) — REPORT.md, README.md, LIVE-README.md và KNOWN_ISSUES.md trước đính chính.
- Dữ liệu đo, số liệu CSV và log mục 7 giữ nguyên. Không sửa `.cfg`, `.conf`, service hay source TKC trên máy.
- Chi tiết: [INSTALLATION_AUDIT.md](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/experiments/tkc-b6c3328-20260906/INSTALLATION_AUDIT.md>).

### Kết quả
Xác nhận cài thật và đo thật, đồng thời đính chính rõ cách cài chưa phải reference installer. Muốn chuẩn hóa cần sửa guide/import, kiểm tra môi trường đúng requirements, tích hợp service/macros/Moonraker, rồi mới nghiệm thu phạm vi tương ứng. Phiên này chỉ audit và cập nhật tài liệu, giữ nguyên bản TKC đang chạy.

## 9. Gỡ sạch TKC cũ và cài lại bản upstream 0.8.19

### Mục tiêu
Gỡ toàn bộ bản TKC thử nghiệm khỏi các đường dẫn đang hoạt động trên máy `192.168.1.43`, xác minh trạng thái sạch, cài lại bản `main` mới nhất, kiểm tra quy trình cài/cập nhật và lập báo cáo mà không vá mã nguồn TKC.

### Sao lưu
- [pre-clean-reinstall-tkc-20260906-195259](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-clean-reinstall-tkc-20260906-195259/README.md>) — `printer.cfg`, `moonraker.conf`, `moonraker.asvc`, cấu hình repo, user service cũ, station data, source patch và trạng thái runtime trước khi gỡ.
- Remote: `/home/voron/printer_data/config_backups/tkc-clean-reinstall-20260906-195259/` — có thêm bằng chứng gỡ sạch, hai lần thử installer chính thức, test venv mới, unit trung gian và trạng thái cuối.

### Gỡ và xác minh sạch
- Dừng/disable/xóa `tool-calibrator-experiment.service`, gỡ đúng include thử nghiệm và các symlink extras đã xác nhận thuộc TKC.
- Chuyển `~/printer_data/tkc-experiment` vào backup; xóa source cũ, `~/tkc-env` và worktree preflight sau khi lưu SHA/patch.
- Restart process Klipper qua Moonraker. Xác minh source/venv/service/config/macro/extras cũ đều vắng mặt, port 8090 đóng, không có process TKC, không còn config reference hay lệnh/object TKC chính xác. Klipper ready; kTAMV vẫn active ở port 8086.

### Bản cài mới và khác biệt với installer
- Chốt upstream `04431dfe575a717833c6966685ecdfac90c6568b`, version 0.8.19. Preflight và venv sạch đều đạt **100/100 tests**; source cuối ở branch main, clean, đúng remote SHA.
- Installer trực tiếp lỗi `Permission denied` vì `install.sh` có mode 100644. Chạy qua `bash` dừng vì coi package hệ thống `python3-pip` là bắt buộc rồi yêu cầu sudo; tài khoản SSH không có sudo không mật khẩu. `python3 -m venv` thực tế hoạt động mà không cần package đó.
- Cài theo layout mới: `~/Tool-Klipper-Calibration/env`, symlink extras và hai macro bundle, cấu hình `[tool_calibrator]`, station-only `tool_offsets.cfg`, Update Manager và service `tool_calibrator.service`.
- Vì thiếu quyền hệ thống, service chạy ở user scope. Bỏ `User=voron`, dùng `default.target`, bind 127.0.0.1:8090 và truyền camera URL/MPP khi khởi động. Upstream source không bị sửa.
- Update Manager dùng `is_system_service: False`, quản lý restart Klipper nhưng không thể tự restart user daemon. No-op update trả ok, SHA không đổi. Sau cập nhật thật phải chạy `systemctl --user restart tool_calibrator.service`.

### Cấu hình và an toàn
- `config/printer.cfg` — thêm include hai macro TKC, `Printer-Setup/tool-calibrator.cfg` và `tool_offsets.cfg`.
- `config/Printer-Setup/tool-calibrator.cfg` — safe Z 40; tốc độ 1800/600/600 mm/min; wiggle tắt; kiểm tra homing/tool active-detected; giữ LED tool tắt khi chụp; chặn cả hai hook Z Cartographer.
- `config/tool_offsets.cfg` — chỉ di chuyển camera station/matrix đã đo từ phiên b6c3328; không có `[tool_offsets]`, không áp offset production.
- `config/moonraker.conf` — thêm updater TKC phù hợp user-service limitation.
- kTAMV giữ nguyên và tiếp tục chạy riêng ở port 8086; TKC chỉ nghe loopback 8090.

### Kiểm tra thực tế
- Klipper và Moonraker nạp cấu hình không lỗi; TKC core commands và macro bundle có mặt.
- Health đúng service/version/commit; pip check không có dependency hỏng; updater current=remote, clean, không detached, behind=0, không warning/anomaly.
- Lần đầu `CALIBRATION_TEST_VISION` sau daemon sạch thất bại vì code không gọi đồng bộ camera, daemon dùng `/webcam2` và nhận HTTP 502. Sau khi đưa camera URL/MPP vào unit, phép thử đứng yên đạt 5/5 frame, UV 639,95/360,05 px, radius 22,30 px, confidence 99,0%, dispersion 0,00 px. Vị trí trước/sau không đổi.
- Sau restart, chạy G28 thông thường theo xác nhận người dùng, đưa Z lên 40. Trạng thái cuối: standby, XYZ homed, T0 active/detected, X175,8 Y168,0 Z40, heater targets bằng 0, TKC IDLE; TKC và kTAMV đều active.

### Lỗi cài/gỡ/cập nhật cần sửa upstream
1. Hai script mode 100644; chmod theo guide làm repo dirty và ảnh hưởng Update Manager.
2. Preflight `python3-pip` thừa tạo yêu cầu sudo không cần thiết; installer không transactional và không rollback khi lỗi muộn.
3. `ln -sf` với legacy `z_backends` symlink có thể tác động ngược vào source; uninstaller xóa cả thư mục/regular files thay vì chỉ tài sản TKC.
4. Health báo ok dù camera mặc định hỏng; `CALIBRATION_TEST_VISION` thiếu `_ensure_vision_sync()` và thất bại sau restart sạch.
5. Guide include `tool_offsets.cfg` nhưng installer không tạo file; comment sample vẫn dùng đường dẫn `~` trái với guide mới.
6. Chỉ hỗ trợ system service; user-service fallback không có đường restart tự động sau update.
7. OpenCV/NumPy không có upper bound; cài mới nhận OpenCV 5.0.0.93 và NumPy 2.4.6, test hiện đạt nhưng khó tái lập lâu dài.
8. Uninstaller vẫn để repo, printer.cfg block/include và offsets file cho người dùng tự xử lý nhưng luôn in thông báo gỡ sạch.

### Kết quả
TKC 0.8.19 đã được cài thật, source sạch và hoạt động ở phạm vi đọc camera/command registration; không chỉ là môi trường test Python. Cài đặt hiện dùng user-service adaptation có giới hạn update đã ghi rõ. Chưa chạy hiệu chuẩn XY mới, chưa chạy Z, chưa áp offset và chưa thử in. Báo cáo đầy đủ: [REPORT.md](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/experiments/tkc-clean-reinstall-20260906/REPORT.md>).

## 10. Gỡ sạch và cài lại TKC `6c721e5`, kiểm tra installer mới trên máy thật

### Mục tiêu và sao lưu
- Gỡ bản `04431df`, xác minh các đường dẫn hoạt động sạch, cài `main` mới nhất `6c721e5798184da1bf92445dbf345141b326ecc2` bằng installer upstream mới và không sửa source TKC.
- Sao lưu local: [pre-tkc-6c721e5-reinstall-20260906-203328](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-tkc-6c721e5-reinstall-20260906-203328/>).
- Sao lưu trên máy: `/home/voron/printer_data/config_backups/tkc-6c721e5-reinstall-20260906-203328/`, gồm config, ASVC, unit, source state, symlink, health, machine state và source cũ không kèm venv.

### Gỡ và xác minh sạch
- Dừng/disable user service; gỡ đúng include, updater và symlink thuộc TKC. Mọi file/symlink `.cfg` được chuyển vào backup, không xóa. Source, env và worktree thử được gỡ sau khi lưu bằng chứng.
- Checkpoint sạch xác nhận source/unit/config active/macro/extras vắng mặt, port 8090 đóng, kTAMV vẫn active port 8086; Klipper nạp config không có object/lệnh TKC và vẫn ready.
- `RESTART` chỉ reload config, không kết thúc Python process. Full restart `klipper.service` ở cuối chuỗi cài đã buộc loại module cũ khỏi cache và nạp mã mới.

### Kết quả installer mới
- `install.sh`/`uninstall.sh` đã có mode 100755. Preflight không còn bắt buộc `python3-pip`; `./scripts/install.sh --user-service` chạy trực tiếp, tạo venv, extras, macro, placeholder offsets, updater và user unit.
- Installer vẫn gọi `sudo systemctl restart moonraker/klipper` trong user mode; cả hai thất bại vì không có sudo không mật khẩu nhưng bị `|| true` che và installer vẫn in thành công. Klipper chưa nạp module mới, Moonraker chưa nạp updater ở thời điểm đó.
- Health trong lúc cài báo `6c721e5-dirty` do `.install_manifest.txt` tạm thời còn trong repo; sau thành công manifest bị xóa và worktree sạch.
- 101/101 tests đạt trong 7,79 giây ở test venv tách biệt. Production venv không cài pytest. `pip check` đạt; phiên bản resolve: Flask 3.0.3, Waitress 3.0.2, OpenCV 5.0.0.93, NumPy 2.4.6, Requests 2.34.2, urllib3 2.7.0.

### Bố trí riêng của máy trong `Printer-Setup`
- Theo yêu cầu người dùng, tất cả đường dẫn `.cfg` TKC riêng của máy được gom vào `config/Printer-Setup/`: `tool-calibrator.cfg`, `tool_offsets.cfg` và `tool_calibrator/` chứa hai macro symlink tới source upstream.
- Sửa include trong `printer.cfg` và `offsets_config_path` cho đúng vị trí mới. Upstream checkout không đổi, branch main sạch và đúng remote SHA.
- Installer vẫn hard-code `config/tool_calibrator/` và root `tool_offsets.cfg`; chạy lại installer sẽ tạo thêm layout root. Đề xuất thêm `--config-subdir`/`--offsets-path`.

### Lỗi runtime mới xác nhận
1. Sync camera ở `klippy:ready` thất bại với `Internal error - reactor pause disabled`; health còn camera mặc định, MPP/matrix rỗng. Cùng hàm sync gọi từ `CALIBRATION_TEST_VISION` sau khi ready thì thành công. Cần lên lịch callback/timer sau ready và integration test với reactor thật.
2. Health chỉ chứng minh process sống, không chứng minh camera/scale/matrix ready. Cần trạng thái readiness riêng và installer kiểm tra object/command/snapshot.
3. Update Manager user mode không quản lý restart user daemon; sau update thật có thể source mới nhưng server process cũ. Cần hook restart hoặc so sánh running commit/source commit.
4. Uninstaller vẫn `rm -rf` thư mục macro, archive offsets trước khi người dùng gỡ include, để machine block/include cho thao tác tay và không nhận layout tùy chỉnh.
5. Rollback manifest chưa ghi đủ venv, service, ASVC, directory, link bị ghi đè/legacy link; manifest lại bị xóa sau success nên uninstall không dùng được.
6. Một phép thử ngoài camera với 1 frame nhận false positive radius 8,60 px, confidence 40%. Burst 5 frame tại cùng scene loại đúng. Cần minimum confidence/radius/ROI và cấm 1 frame cho luồng có thể lưu offset hoặc gây chuyển động.
7. Sau negative vision error, toolchanger quan sát thấy `uninitialized` dù sensor vẫn detected T0; chạy `INITIALIZE_TOOLCHANGER` khôi phục ready mà không chuyển động. Cần test cleanup/error path.

### Đo camera và trạng thái cuối
- G28 thường thành công; T0 active=detected, đi ở Z40 qua approach X171,456 Y43,920 tới target X170,910 Y18,917.
- Năm lượt `CALIBRATION_TEST_VISION SAMPLES=5` đều đạt 5/5 frame. Bốn lượt ổn định confidence 99%, dispersion 0,10–0,20 px; lượt đầu confidence 90,4%, dispersion 2,75 px = 0,0633 mm, vẫn dưới gate 0,08 mm.
- Quay về giữa bàn, burst ngoài camera 5 frame bị từ chối đúng. Không chạy XY calibration, Z calibration, toolchange, gia nhiệt, SAVE_CONFIG hay áp offset.
- No-op Update Manager trả ok; source vẫn sạch, current=remote, behind=0. Cuối phiên: standby, XYZ homed, T0 active/detected, X175,8 Y168,0 Z40; tất cả heater target bằng 0. TKC active loopback 8090 với camera thật, MPP 0,023 và matrix loaded; kTAMV active 8086.

### Kết quả
Đã hoàn tất gỡ/cài lại bản mới trên máy thật, giữ upstream nguyên trạng và tổ chức cấu hình máy trong `Printer-Setup`. Installer mới giải quyết đáng kể lỗi permission/preflight/user-service/placeholder, nhưng chưa thể coi là unattended clean install do restart bị che lỗi, ready-sync sai ngữ cảnh reactor, health chưa kiểm readiness và uninstall/rollback chưa sở hữu đủ trạng thái. Báo cáo và bằng chứng: [REPORT.md](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/experiments/tkc-6c721e5-clean-reinstall-20260906/REPORT.md>).

## 11. Cài sạch TKC `ce4ca303`, thử camera cuối và điều tra lỗi Cartographer Z

### Mục tiêu
- Gỡ hoàn toàn bản TKC trước, xác minh trạng thái sạch rồi cài lại `main` mới nhất.
- Giữ toàn bộ cấu hình riêng của máy dưới `Printer-Setup`.
- Kiểm tra camera lần cuối tại Z=40 và thử đo Z bằng backend Cartographer mà không lưu hay áp offset.
- Lập báo cáo về cài đặt, camera, Z, lỗi và đề xuất cải tiến; không sửa source TKC.

### File đã sửa đổi
- `extras/experiments/tkc-ce4ca30-camera-cartographer-z-20260906/REPORT.md` — báo cáo đầy đủ lần thử.
- `extras/experiments/tkc-ce4ca30-camera-cartographer-z-20260906/*.txt|*.json` — bằng chứng cài/gỡ, camera, Z, trace lỗi và trạng thái cuối.
- `extras/backups/pre-tkc-ce4ca30-camera-z-20260906-212025/` — bản sao cấu hình và trạng thái repo trước thử nghiệm.
- `.agents/KNOWN_ISSUES.md` — ghi lỗi `NameError` làm Klippy shutdown và giới hạn Cartographer cố định trên shuttle.

### Sao lưu
- Local: `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-tkc-ce4ca30-camera-z-20260906-212025/`.
- Máy in: `/home/voron/printer_data/config_backups/tkc-ce4ca30-camera-z-20260906-212025/`.
- Các file live đã lưu: `printer.cfg`, `moonraker.conf`, `Printer-Setup/tool-calibrator.cfg`, `Printer-Setup/tool_offsets.cfg`, macro links, service unit, source state và log daemon.

### Triển khai và kiểm tra
- Upstream `main` chốt tại `ce4ca3030e7d3c8d11c3aa1b54daf9242d997624`; source cuối sạch, current hash bằng remote hash.
- Test tách biệt trên Pi: 107/107 đạt trong 8,43 giây.
- Uninstaller mới chạy với `--config-subdir Printer-Setup`; checkpoint sạch xác nhận source/unit/process/port/symlink/object/command/ref active đều không còn.
- Installer mới chạy bằng `./scripts/install.sh --user-service --config-subdir Printer-Setup`; user service active/enabled và bind loopback `127.0.0.1:8090`.
- Một lần gọi đầu nhận ký tự CR do transport PowerShell và tạo thư mục `Printer-Setup\r`; cấu hình chưa active, đã gỡ sạch ngay. Lần cuối xác minh byte của `Printer-Setup` trước khi cài.
- kTAMV không xung đột: tiếp tục chạy bằng `ktamv-server.service` trên cổng 8086.

### Kết quả camera
- G28 thành công, T0 active khớp detected, Z=40 trước khi di chuyển camera.
- Ở approach X171,456 Y43,920 Z40: 0/5 frame, âm tính đúng, toolchanger vẫn ready.
- Ở target X170,910 Y18,917 Z40: 5 lượt liên tiếp, tổng 25/25 frame.
- Mỗi lượt: UV 639,95 / 355,95 px; radius 22,40 px; confidence 99,0%; dispersion 0,05–0,10 px.
- Không chạy auto-centering và không lưu XY offset.

### Thử nghiệm Cartographer Z và lỗi máy
- Chỉ trong lúc thử, đổi hai hook `_TKC_Z_DISABLED` thành `CARTOGRAPHER_TOUCH_HOME` và `CARTOGRAPHER_TOUCH_PROBE`.
- Lệnh dùng `CALIBRATE_XY=0 CALIBRATE_Z=1 SAVE_CONFIG=0`, máy lạnh, heater target=0, Z40 trước toolchange.
- T0 hoàn thành touch-home tại X174 Y168; Cartographer điều chỉnh gốc Z 0,335 mm và TKC chuẩn hóa reference T0 thành 0.
- T1 được gắn đúng và bắt đầu `CARTOGRAPHER_TOUCH_PROBE`, nhưng chưa trả số đo thì một object-status query kích hoạt lỗi TKC.
- Trace xác nhận `klippy/extras/tool_calibrator.py:get_status()` gọi `time.time()` khi run đang RUNNING nhưng module không `import time`.
- Klippy shutdown với `NameError: name 'time' is not defined` và `Unhandled exception during run`; không phải lỗi CAN, điện hoặc Cartographer.
- `cmd_CALIBRATION_STATUS()` có cùng đường lỗi thiếu import. 107 test upstream không bao phủ trạng thái RUNNING này.
- Dừng khẩn cấp, stop TKC daemon, phục hồi Z-disabled, `FIRMWARE_RESTART`, G28 nhận đúng T1, nâng Z40 rồi đổi an toàn về T0.
- SHA-256 trước/sau của `tool_offsets.cfg` và `printer.cfg` trùng tuyệt đối; không offset nào được ghi hoặc áp.

### Nguyên nhân và giới hạn phương pháp
- Lỗi shutdown gốc là lỗi Python trong TKC `ce4ca303`, tái hiện khi UI/API đọc status trong lúc calibration hoạt động.
- Cartographer máy này cố định trên shuttle và adapter Cartographer mô tả probe là contactless. Kết quả touch theo hình học shuttle–bed, không trực tiếp quan sát chiều dài từng nozzle.
- Không dùng backend này để kết luận Z offset T1–T4. PF2 switch/Axiscope mới là cơ chế nozzle-reference phù hợp để đo tool Z thực.

### Kết quả cuối
- Máy `ready`, `standby`, XYZ homed, T0 active=detected, X175,8 Y168 Z40.
- Toàn bộ hotend và bed target=0.
- TKC `ce4ca303` active/enabled; camera ready, MPP 0,023, matrix loaded, session unlocked.
- Hai hook Z đã trở lại `_TKC_Z_DISABLED`; không chạy lại Z cho tới khi upstream sửa status crash và xác nhận cơ chế đo nozzle.
- Không sửa code upstream TKC.

### Vấn đề còn lại
- P0: sửa import/time và bảo đảm `get_status()` không thể làm Klippy shutdown; thêm integration test subscription khi run đang hoạt động.
- P0: chặn fixed-shuttle Cartographer cho per-tool nozzle Z hoặc yêu cầu khai báo measurement reference.
- P1: `CALIBRATE_TOOL_Z TOOL=n` phải tự đo T0 reference hoặc từ chối; hiện có thể dùng reference rỗng.
- P1: sửa rollback journal, validate `--config-subdir`, bao phủ include `tool-calibrator.cfg`, và chỉ báo cài thành công khi camera/mpp/matrix đã ready.

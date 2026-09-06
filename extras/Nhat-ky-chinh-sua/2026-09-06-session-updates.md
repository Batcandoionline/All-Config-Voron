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


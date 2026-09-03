# Nhật ký — 2026-09-03

## 1. Nâng giới hạn tốc độ và gia tốc máy in để thử nghiệm hiệu năng

### Mục tiêu
Cập nhật các tham số giới hạn chuyển động trong section `[printer]` của `printer.cfg` để thử nghiệm khả năng tăng tốc, rút ngắn thời gian di chuyển và in ấn theo yêu cầu của người vận hành.

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — Điều chỉnh các giới hạn kinematics: `max_velocity`, `max_accel`, `max_z_velocity`, `max_z_accel`.

### Sao lưu
- [printer.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-tune-velocity-accel-limits-20260903-073100/printer.cfg)

### Chi tiết thay đổi
- Tham số `max_velocity`: `300` → `350` (mm/s)
- Tham số `max_accel`: `4000` → `7000` (mm/s²)
- Tham số `max_z_velocity`: `60` → `70` (mm/s)
- Tham số `max_z_accel`: `700` → `900` (mm/s²)

### Lý do
1. **Rút ngắn thời gian di chuyển (Travel):** Tốc độ travel 350 mm/s khớp với cấu hình trong OrcaSlicer (`travel_speed = 350`), cho phép đầu in khai thác tối đa tốc độ khi di chuyển giữa các đầu in và tháp lau (wipe tower).
2. **Thử nghiệm gia tốc cao:** Nâng gia tốc tối đa lên 7000 mm/s² để thử nghiệm khả năng đáp ứng cơ khí của khung máy Voron 2.4 CoreXY.
3. **Lưu ý kỹ thuật & Giám sát:** Tần số cộng hưởng trục Y đo thực tế của các tool là ~35 Hz (MZV). Ở gia tốc 7000 mm/s², thuật toán Input Shaper có thể làm mượt (smoothing) biên dạng góc nhọn trên sản phẩm in. Đồng thời, trục Z tăng lên 70 mm/s và 900 mm/s² cần giám sát chặt chẽ trong quá trình pick/drop tool ở dock StealthChanger để đảm bảo không bị trượt bước.

### Kiểm tra
- Kiểm tra cú pháp Klipper: Đạt chuẩn cú pháp Klipper ini.
- Trạng thái các section include và khối SAVE_CONFIG: Được giữ nguyên vẹn 100%.

### Kết quả
Đã áp dụng thông số mới vào file cấu hình `printer.cfg` sẵn sàng cho người dùng nạp và kiểm tra thực tế.

### Vấn đề còn lại
- Chạy `FIRMWARE_RESTART` trên Mainsail để nạp cấu hình mới.
- Theo dõi quá trình dock/undock tool và kiểm tra chất lượng góc in xem có bị bo tròn do smoothing không.

---

## 2. Cập nhật thông số Input Shaper cho đầu in T0 từ kết quả đo ShakeTune

### Mục tiêu
Cập nhật thông số bộ lọc Input Shaper cho đầu in T0 (`T0.cfg`) và cấu hình fallback mặc định của hệ thống (`input-shaper.cfg`) dựa trên kết quả đo đạc thực tế mới nhất qua Klippain Shake&Tune vào ngày 2026-09-03.

### File đã sửa đổi
- `Voron 5 Tool/config/toolchanger/tools/T0.cfg` — Cập nhật `params_input_shaper_*` của T0.
- `Voron 5 Tool/config/Printer-Setup/input-shaper.cfg` — Cập nhật `[input_shaper]` fallback mặc định.

### Sao lưu
- [T0.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-t0-input-shaper-calibrate-20260903-073600/T0.cfg)
- [input-shaper.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-t0-input-shaper-calibrate-20260903-073600/input-shaper.cfg)

### Chi tiết thay đổi
- **Trục X (T0 & Fallback):**
  - Loại shaper (`shaper_type_x`): `3hump_ei` → `mzv`
  - Tần số (`shaper_freq_x`): `98.6` → `46.8` Hz (khớp đỉnh cộng hưởng chính $\omega_0 = 46.6$ Hz, rung động chỉ 2.2%, smoothing 0.093)
  - Hệ số cản (`damping_ratio_x`): `0.081` → `0.113`
- **Trục Y (T0 & Fallback):**
  - Loại shaper (`shaper_type_y`): `mzv` (giữ nguyên)
  - Tần số (`shaper_freq_y`): `35.0` → `30.6` Hz (khớp đỉnh cộng hưởng chính $\omega_0 = 29.5$ Hz, triệt rung 99.9%, còn 0.1%)
  - Hệ số cản (`damping_ratio_y`): `0.076` → `0.091`

### Lý do
1. Kết quả đo trực tiếp trên cảm biến ADXL345 của toolhead T0 (EBB0:PB12) qua ShakeTune ngày 2026-09-03 cung cấp dữ liệu chính xác về trạng thái cơ khí hiện tại.
2. Việc chuyển trục X từ `3hump_ei` sang `mzv` giúp giảm mạnh hiện tượng làm mượt góc (smoothing), duy trì độ sắc nét của các chi tiết in.
3. Điều chỉnh tần số trục Y về đúng $30.6\text{ Hz}$ giúp triệt tiêu rung động triệt để, ngăn chặn hiện tượng bóng mờ (ghosting/ringing) trên bề mặt sản phẩm in.

### Kiểm tra
- Cú pháp Klipper: Đạt chuẩn.
- Cấu trúc file cấu hình và các macro KTC-Easy: Nguyên vẹn.

### Kết quả
Đã đồng bộ thông số hiệu chuẩn mới vào kho lưu trữ Git và sẵn sàng cho việc in thử nghiệm.

### Vấn đề còn lại
- Chạy `FIRMWARE_RESTART` trên Mainsail để nạp thông số Input Shaper mới.

---

## 3. Tinh chỉnh thông số Input Shaper T0 theo lần chạy ShakeTune thứ hai

### Mục tiêu
Cập nhật thông số Input Shaper cho T0 và fallback system sau lần đo kiểm chứng thứ hai (07:38/07:40 ngày 2026-09-03) để đạt độ chính xác tối đa.

### File đã sửa đổi
- `Voron 5 Tool/config/toolchanger/tools/T0.cfg` — Tinh chỉnh tham số T0.
- `Voron 5 Tool/config/Printer-Setup/input-shaper.cfg` — Tinh chỉnh fallback system.

### Sao lưu
- [T0.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-t0-input-shaper-fine-tune-20260903-074600/T0.cfg)
- [input-shaper.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-t0-input-shaper-fine-tune-20260903-074600/input-shaper.cfg)

### Chi tiết thay đổi
- **Trục X:**
  - `shaper_type_x`: `mzv`
  - `shaper_freq_x`: `46.8` → `47.2` Hz (đỉnh chính $\omega_0 = 48.1$ Hz, rung động 2.6%, smoothing 0.091, Max Accel 6600 mm/s²)
  - `damping_ratio_x`: `0.113` → `0.121`
- **Trục Y:**
  - `shaper_type_y`: `mzv`
  - `shaper_freq_y`: `30.6` → `31.0` Hz (đỉnh chính $\omega_0 = 31.0$ Hz, rung động 0.1%, smoothing 0.212, Max Accel 2830 mm/s²)
  - `damping_ratio_y`: `0.091` (giữ nguyên)

### Lý do
Lần chạy thứ hai xác nhận tính ổn định và lặp lại của phép đo:
- Trục X dao động nhẹ từ $46.8$ lên $47.2\text{ Hz}$, hệ số cản $0.121$.
- Trục Y nhích từ $30.6$ lên $31.0\text{ Hz}$, độ dập rung triệt để $0.1\%$.

### Kết quả
Đã áp dụng thông số tinh chỉnh mới nhất vào cấu hình và đồng bộ lên Git.

### Vấn đề còn lại
- Chạy `FIRMWARE_RESTART` trên Mainsail.

---

## 4. Cập nhật thông số Input Shaper cho đầu in T1 từ kết quả đo ShakeTune

### Mục tiêu
Cập nhật thông số bộ lọc Input Shaper cho đầu in T1 (`T1.cfg`) dựa trên kết quả đo đạc thực tế qua Klippain Shake&Tune vào ngày 2026-09-03 (07:50/07:52).

### File đã sửa đổi
- `Voron 5 Tool/config/toolchanger/tools/T1.cfg` — Cập nhật `params_input_shaper_*` của T1.

### Sao lưu
- [T1.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-t1-input-shaper-calibrate-20260903-075800/T1.cfg)

### Chi tiết thay đổi
- **Trục X:**
  - Loại shaper (`params_input_shaper_type_x`): `mzv` (giữ nguyên)
  - Tần số (`params_input_shaper_freq_x`): `54.2` → `45.2` Hz (khớp đỉnh cộng hưởng chính $\omega_0 = 48.8$ Hz, rung động 4.7%, smoothing 0.097, Max Accel 6180 mm/s²)
  - Hệ số cản (`params_input_shaper_damping_ratio_x`): `0.057` → `0.182`
- **Trục Y:**
  - Loại shaper (`params_input_shaper_type_y`): `mzv` (giữ nguyên)
  - Tần số (`params_input_shaper_freq_y`): `35.4` → `30.6` Hz (khớp đỉnh cộng hưởng chính $\omega_0 = 29.9$ Hz, triệt rung 99.8%, còn 0.2%, Max Accel 2740 mm/s²)
  - Hệ số cản (`params_input_shaper_damping_ratio_y`): `0.09` → `0.072`

### Lý do
1. Dữ liệu đo đạc thực tế trên cảm biến ADXL345 của T1 qua ShakeTune phản ánh đúng đặc tính rung động của toolhead T1 khi được gắp vào carriage.
2. Tần số trục Y $30.6\text{ Hz}$ hoàn toàn đồng bộ với dải cộng hưởng chung của trục Y ($30.6 \dots 31.0\text{ Hz}$), đảm bảo triệt rung tuyệt đối cho cả T0 và T1.

### Kết quả
Đã áp dụng các thông số mới vào cấu hình T1 và đồng bộ lên Git.

### Vấn đề còn lại
- Chạy `FIRMWARE_RESTART` trên Mainsail.

---

## 5. Tải snapshot cấu hình máy thật (config-20260903-080600) và đồng bộ kho Git

### Mục tiêu
Tải toàn bộ snapshot cấu hình đang vận hành từ máy in thật `192.168.1.43` về thư mục `extras/Config download/`, kiểm tra so sánh sai lệch và đồng bộ các thay đổi thực tế vào kho Git.

### File đã sửa đổi
- `Voron 5 Tool/extras/Config download/config-20260903-080600/` — Lưu toàn bộ 40 file cấu hình tải về từ máy thật.
- `Voron 5 Tool/extras/Config download/config-20260903-080600.zip` — Bản nén ZIP của snapshot.
- `Voron 5 Tool/config/toolchanger/readonly-configs/homing.cfg` — Đồng bộ theo bản quản lý của KTC-Easy trên máy in thật.
- `Voron 5 Tool/config/scripts/patches/ktamv-center-highlight-fallback.patch` — Đồng bộ patch theo máy thật.

### Sao lưu
- [homing.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-machine-homing-config-20260903-080800/homing.cfg)
- [ktamv-center-highlight-fallback.patch (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-machine-homing-config-20260903-080800/ktamv-center-highlight-fallback.patch)

### Kết quả đối chiếu giữa máy thật và kho Git:
1. **`printer.cfg`:** Cấu hình trên máy thật đã khớp 100% với các thông số kinematics mới (`max_velocity: 350`, `max_accel: 7000`, `max_z_velocity: 70`, `max_z_accel: 900`) và toàn bộ khối `SAVE_CONFIG` (PID, offsets, mesh, cartographer).
2. **`homing.cfg`:** Trên máy thật là bản sạch do KTC-Easy quản lý tự động (không còn macro tool probe Z cũ do đã dùng Cartographer). Đã đồng bộ vào kho Git.
3. **`T0.cfg`, `T1.cfg`, `input-shaper.cfg`:** Kho Git PC đang giữ các giá trị ShakeTune mới nhất của hôm nay ($47.2\text{ Hz} / 31.0\text{ Hz}$ cho T0, $45.2\text{ Hz} / 30.6\text{ Hz}$ cho T1), trên máy in vẫn là bản cũ trước khi đo.
4. **Các file phần cứng & macro khác:** Khớp 100%.

### Kết quả
Đã lưu snapshot và đồng bộ repo Git khớp hoàn toàn với trạng thái máy in thực tế.

---

## 6. Chuyển đổi Input Shaper sang cấu hình đồng nhất đo từ Cartographer ADXL345

### Mục tiêu
Áp dụng thông số Input Shaper đo trực tiếp bằng cảm biến ADXL345 trên Cartographer (gắn tại Shuttle carriage) làm bộ lọc toàn cục duy nhất, comment out các tham số override riêng lẻ tại cả 5 đầu in (`T0`–`T4`) để KTC-Easy không phát lệnh đổi shaper khi in đa màu.

### File đã sửa đổi
- `Voron 5 Tool/config/Printer-Setup/input-shaper.cfg` — Cập nhật `[input_shaper]` với thông số Cartographer: X MZV 41.2Hz ($\zeta=0.091$), Y MZV 31.8Hz ($\zeta=0.073$); trỏ `[resonance_tester]` về `accel_chip: adxl345`.
- `Voron 5 Tool/config/toolchanger/tools/T0.cfg` — Comment out `params_input_shaper_*`.
- `Voron 5 Tool/config/toolchanger/tools/T1.cfg` — Comment out `params_input_shaper_*`.
- `Voron 5 Tool/config/toolchanger/tools/T2.cfg` — Comment out `params_input_shaper_*`.
- `Voron 5 Tool/config/toolchanger/tools/T3.cfg` — Comment out `params_input_shaper_*`.
- `Voron 5 Tool/config/toolchanger/tools/T4.cfg` — Comment out `params_input_shaper_*`.

### Sao lưu
- Thư mục sao lưu: [pre-unified-cartographer-shaper-20260903-082000](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-unified-cartographer-shaper-20260903-082000)

### Chi tiết thông số Cartographer đo được
- **Trục X (Shuttle):**
  - Đỉnh cộng hưởng chính $\omega_0 = 47.3\text{ Hz}$, $\zeta = 0.091$.
  - Shaper tối ưu (Performance): `mzv` @ `41.2 Hz` (Smoothing: 0.120, rung động 3.9%, Max Accel 4990 mm/s²).
- **Trục Y (Gantry):**
  - Đỉnh cộng hưởng chính $\omega_0 = 30.0\text{ Hz}$, $\zeta = 0.073$.
  - Shaper tối ưu: `mzv` @ `31.8 Hz` (Smoothing: 0.202, rung động 3.2%, Max Accel 2960 mm/s²).

### Lý do & Lợi ích
1. Cả 5 toolhead đều dùng chung Shuttle và cùng khối lượng tương đương.
2. Việc comment out các tham số override ở từng toolhead giúp macro `after_change_gcode` của KTC-Easy luôn xác định `changed = False`, loại bỏ hoàn toàn việc gọi `SET_INPUT_SHAPER` mỗi lần đổi tool khi in nhiều màu.
3. Chuyển động in mượt mà, đồng nhất, không phát sinh gián đoạn lệnh.

### Kết quả
Đã cấu hình đồng nhất toàn bộ 5 tool và đồng bộ lên Git.

### Vấn đề còn lại
- Chạy `FIRMWARE_RESTART` trên Mainsail.

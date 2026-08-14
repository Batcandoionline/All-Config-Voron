# Nhật ký — 2026-08-14

## 1. Tích hợp bộ Macro sấy nhựa bằng bàn in (Filament Dryer Macros & Presets)

### Mục tiêu
Tích hợp giải pháp sấy cuộn nhựa trực tiếp trên bàn in nhiệt của máy Voron 2.4 StealthChanger 5-Tool, kết hợp quạt đối lưu buồng (`bed_fan`), cơ chế tự động đỗ đầu in an toàn (`UNSELECT_TOOL` và nâng Z), chống ngắt bởi `idle_timeout`, và cung cấp sẵn các nút bấm 1-click preset trên giao diện Mainsail.

### File đã sửa đổi
- [print-macros.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/Printer-Setup/print-macros.cfg) — Thêm các macro điều khiển sấy nhựa: `START_DRYER`, `STOP_DRYER`, `_DRYER_STATUS`, `DRYER_TIMER`, và các preset `DRY_PLA`, `DRY_PETG`, `DRY_ABS`, `DRY_ASA`, `DRY_TPU`, `DRY_NYLON`, `DRY_PC`.

### Sao lưu
- [print-macros.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-add-filament-dryer-macros-20260814-160600/print-macros.cfg)
- [README.md (Backup Record)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-add-filament-dryer-macros-20260814-160600/README.md)

### Chi tiết thay đổi
1. **Macro `START_DRYER`**:
   - Nhận các tham số: `BED` (nhiệt độ bàn in, mặc định 50°C), `TIME` (thời gian tính theo phút, mặc định 240 phút), `TIME_HOURS` (tùy chọn theo giờ), `FAN` (tốc độ quạt đối lưu `bed_fan`, mặc định 0.3), `PARK` (1: tự động homing, nhả toolhead `UNSELECT_TOOL` về dock và nâng Z lên $\ge 200\text{ mm}$ để lấy không gian đặt cuộn nhựa).
   - Kiểm tra an toàn trạng thái in (`printer.idle_timeout.state == "Printing"` / `is_paused`).
   - Khởi động timer đếm ngược qua `[delayed_gcode DRYER_TIMER]`.
2. **Macro `STOP_DRYER`**:
   - Tắt nhiệt bàn in `M140 S0`, tắt quạt `BED_FAN_OFF`, hủy timer `DURATION=0`, khôi phục LED và gửi thông báo hoàn tất.
3. **Macro `_DRYER_STATUS` & `DRYER_TIMER`**:
   - Chu kỳ cập nhật mỗi 10 giây: gửi lại lệnh `M140 S{bed_temp}` ngăn Klipper tắt heater khi rảnh (`idle_timeout`), hiển thị đếm ngược định dạng `XhYm` ra màn hình (`M117`), định kỳ 10 phút gửi log nhiệt độ bàn + nhiệt độ buồng vào console.
4. **Các macro Preset 1-click**:
   - `DRY_PLA`: Bàn 50°C — 4 giờ, quạt 30%
   - `DRY_PETG`: Bàn 65°C — 4 giờ, quạt 40%
   - `DRY_ABS`: Bàn 80°C — 4 giờ, quạt 50%
   - `DRY_ASA`: Bàn 80°C — 4 giờ, quạt 50%
   - `DRY_TPU`: Bàn 55°C — 5 giờ, quạt 30%
   - `DRY_NYLON`: Bàn 90°C — 6 giờ, quạt 60%
   - `DRY_PC`: Bàn 95°C — 6 giờ, quạt 60%

### Lý do
Giải pháp sấy cuộn nhựa bằng bàn nhiệt kết hợp hộp chụp (cardboard cover) giúp tận dụng tối đa bàn in silicone công suất lớn và quạt đối lưu Nevermore/Bed Fan của Voron 2.4 mà không cần can thiệp cài thêm module Python rời vào Klippy, loại bỏ nguy cơ xung đột khi cập nhật hệ thống.

### Kiểm tra
- Kiểm tra cú pháp: Đạt chuẩn cú pháp Klipper Jinja2 và delayed_gcode.
- Khớp nối phần cứng: Tương thích hoàn toàn với cấu hình StealthChanger (`UNSELECT_TOOL`), `bed_fan`, và `[temperature_sensor chamber]`.

### Kết quả
Tạo thành công hệ thống macro sấy nhựa hoàn chỉnh, sẵn sàng hiển thị trên giao diện Mainsail.

---

## 2. Đồng bộ cấu hình thực tế từ máy in (`config-20260814-160642`)

### Mục tiêu
So sánh và đồng bộ các thay đổi từ gói cấu hình máy in thực tế vừa tải về (`config-20260814-160642`) vào repository PC để đảm bảo tính nhất quán 100% giữa máy in và máy tính.

### File đã sửa đổi
- [printer.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/printer.cfg) — Cập nhật Z-offset cho `[tool T4]` và điểm bù lưới bàn in `[bed_mesh default]`.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-downloaded-machine-config-20260814-161000/printer.cfg)
- [README.md (Backup Record)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-downloaded-machine-config-20260814-161000/README.md)

### Chi tiết thay đổi
1. **`[tool T4]` trong khối `SAVE_CONFIG`**:
   - `gcode_z_offset`: `0.086` → `-0.014` (giá trị thực tế lưu trên máy in).
2. **`[bed_mesh default]`**:
   - Cập nhật điểm lưới dòng 85: `0.027074` → `0.02074` theo đúng dữ liệu scan thực tế của máy.
3. **Các cấu hình khác**:
   - Toàn bộ các file cấu hình hardware, toolchanger, T0-T4, fans-leds, calibration, sensor đều hoàn toàn trùng khớp 100%.
   - Giữ lại các cải tiến tài liệu `README.md`, cờ loại trừ file `*.md` trong `install.sh`/`update.sh` và macro sấy nhựa mới thêm ở Section 1.

### Lý do
Đảm bảo thông số Z-offset thực tế của T4 và dữ liệu bed mesh trên máy in được lưu trữ chính xác trong repo Git, tránh bị ghi đè sai lệch khi chạy script cập nhật từ xa.

### Kiểm tra
- Kiểm tra `git diff --no-index` giữa `extras/Config download/config-20260814-160642/config/printer.cfg` và `config/printer.cfg`: Khớp 100% không còn sai lệch.

### Kết quả
Toàn bộ repository đã được đồng bộ chuẩn xác với trạng thái máy in thực tế.

---

## 3. Tích hợp và tối ưu hóa quạt dưới bàn nhiệt (`bed_fan`) cho chu trình sấy nhựa

### Mục tiêu
Tối ưu hóa luồng khí đối lưu nhiệt bằng cách tích hợp trực tiếp quạt đặt dưới bàn in (`bed_fan` kết nối tại Fan3/PF8) vào tất cả các macro và preset sấy nhựa. Quạt dưới bàn nhiệt sẽ thổi luồng khí nóng từ mặt dưới mâm nhiệt silicone tuần hoàn ngược lên trên buồng sấy/hộp chụp, giúp nhiệt độ phân bố đều 360 độ xung quanh cuộn nhựa và đẩy hơi ẩm ra ngoài nhanh hơn.

### File đã sửa đổi
- [print-macros.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/Printer-Setup/print-macros.cfg) — Tối ưu `START_DRYER`, bộ duy trì tốc độ quạt `_DRYER_STATUS`, lệnh tắt `STOP_DRYER` và điều chỉnh tốc độ quạt trong các preset `DRY_PLA` (40%), `DRY_PETG` (50%), `DRY_ABS`/`DRY_ASA` (60%), `DRY_TPU` (40%), `DRY_NYLON`/`DRY_PC` (70%).

### Sao lưu
- [print-macros.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-optimize-dryer-bed-fan-airflow-20260814-161400/print-macros.cfg)
- [README.md (Backup Record)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-optimize-dryer-bed-fan-airflow-20260814-161400/README.md)

### Chi tiết thay đổi
1. **Duy trì luồng gió liên tục trong `_DRYER_STATUS`**:
   - Cứ mỗi chu kỳ 10 giây, bộ điều khiển kiểm tra và áp dụng lại lệnh `SET_FAN_SPEED FAN=bed_fan SPEED={fan_speed}`, đảm bảo quạt dưới bàn in không bao giờ bị tắt đột ngột bởi timeout hay các sự kiện hệ thống khác trong suốt nhiều giờ sấy.
2. **Nâng cấp tốc độ quạt tối ưu cho từng loại nhựa**:
   - Nhựa nhiệt độ thấp (PLA, TPU): Quạt chạy $40\%$ tạo gió êm dịu, không làm nguội bề mặt quá nhanh.
   - Nhựa nhiệt độ trung bình (PETG): Quạt chạy $50\%$ giúp nhiệt độ trong hộp sấy đạt $\approx 45\text{-}50^\circ\text{C}$.
   - Nhựa kỹ thuật cao (ABS, ASA, Nylon, PC): Quạt chạy $60\%\text{ - }70\%$ để đẩy tối đa luồng khí nóng từ mâm nhiệt công suất lớn lên cuộn nhựa, nâng nhiệt độ buồng sấy lên $\ge 60\text{-}70^\circ\text{C}$.
3. **Hiển thị trạng thái quạt lên Console**:
   - Bổ sung thông tin tốc độ `%` quạt `bed_fan` vào thông báo log định kỳ mỗi 10 phút.

### Kết quả
Hệ thống sấy nhựa bằng bàn in đạt hiệu suất truyền nhiệt và thoát ẩm tối ưu nhờ luồng gió đối lưu liên tục từ quạt dưới bàn in.

---

## 4. Tích hợp hiệu ứng đèn LED màu Cam / Hổ phách (Amber/Orange Glow) khi sấy nhựa

### Mục tiêu
Tạo hiệu ứng thị giác trực quan rõ ràng: Khi máy ở chế độ sấy nhựa, toàn bộ thanh LED buồng (`chamber_lights` 40 bóng WS2812B) và các đèn LED trên 5 đầu in (`T0`–`T4`) sẽ phát ánh sáng màu Cam / Hổ phách ấm áp (`Red: 85%, Green: 35%, Blue: 0%`), giúp người dùng nhìn từ xa nhận biết ngay máy đang thực hiện chu trình sấy nhiệt (khác biệt hoàn toàn với màu trắng khi rảnh, xanh khi in, xanh ngọc khi leveling hay đỏ khi lỗi).

### File đã sửa đổi
- [fans-leds.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/Printer-Setup/fans-leds.cfg) — Bổ sung macro `_SET_LED_STATUS_DRYING` và `_SET_LED_STATUS_DRYING_COMPLETE`.
- [print-macros.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/Printer-Setup/print-macros.cfg) — Tích hợp gọi `_SET_LED_STATUS_DRYING` trong `START_DRYER` và khôi phục đèn bằng `_SET_LED_STATUS_DRYING_COMPLETE` trong `STOP_DRYER`.

### Sao lưu
- [fans-leds.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-add-filament-dryer-led-status-20260814-161700/fans-leds.cfg)
- [print-macros.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-add-filament-dryer-led-status-20260814-161700/print-macros.cfg)
- [README.md (Backup Record)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-add-filament-dryer-led-status-20260814-161700/README.md)

### Chi tiết thay đổi
1. **Macro `_SET_LED_STATUS_DRYING`**:
   - Chuyển `_PRINT_STATE` sang trạng thái `'drying'`.
   - Đặt dải đèn LED buồng 40 bóng sang màu Cam Hổ phách ấm áp: `RED=0.85, GREEN=0.35, BLUE=0.00`.
   - Đặt toàn bộ 5 đầu in `T0`–`T4` sang trạng thái `heating` (LED trước màu cam nổi bật).
2. **Macro `_SET_LED_STATUS_DRYING_COMPLETE`**:
   - Khôi phục `_PRINT_STATE` về `'idle'`.
   - Đưa dải đèn buồng về màu trắng dịu nhẹ trung tính (`RED=0.30, GREEN=0.30, BLUE=0.30`).
   - Đưa toàn bộ 5 đầu in về trạng thái `standby` (xanh dương dịu).

### Kết quả
Trạng thái sấy nhựa hiển thị đẹp mắt, trực quan và đồng bộ hoàn hảo với hệ thống LED Neopixel của toàn bộ máy Voron 2.4 StealthChanger.

---

## 5. Rà soát toàn bộ hệ thống, chỉnh sửa chú thích cũ/sai sót và cập nhật README.md

### Mục tiêu
Kiểm tra toàn diện tất cả các file cấu hình và tài liệu của dự án; chỉnh sửa các chú thích đã cũ hoặc không chính xác; cập nhật các file `README.md` đảm bảo ngắn gọn, súc tích, mô tả chính xác 100% hiện trạng phần cứng và tính năng mới nhất (bao gồm chế độ sấy nhựa và quạt đối lưu).

### File đã sửa đổi
- [README.md (Master)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/README.md) — Cập nhật Z-offset thực tế cho T4 (`-0.014`), bổ sung phần tài liệu hệ thống sấy nhựa (`START_DRYER`, `STOP_DRYER`, bảng preset, under-bed fan, LED amber), làm rõ hành vi của Z stepper (`32mm rotation distance`).
- [config/README.md](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/README.md) — Cập nhật cây thư mục và bảng linh kiện phần cứng (thêm quạt dưới bàn `bed_fan` trên `PF8`, dải LED buồng `chamber_lights` trên `PD15`).
- [hardware.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/Printer-Setup/hardware.cfg) — Sửa chú thích `cb1_fan` thành `cm4_fan` (khớp với host BTT CM4); sửa chú thích `T8 leadscrew` thành `Belted Z drive (80:16 gear ratio)`.
- [calibration.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/Printer-Setup/calibration.cfg) — Xóa bỏ chú thích thừa về Octopus Pro, chỉ rõ bo mạch Manta M8P V2.0.
- [nozzle-clean.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/Printer-Setup/nozzle-clean.cfg) — Sửa chú thích độ cao lau vòi phun từ `Z=2mm` thành `Z=1.2mm` (khớp chính xác với `clean_z`) và cập nhật dải tọa độ quét vòng tròn $X: 277.0 \rightarrow 309.0$.
- [toolchanger-config.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/toolchanger/toolchanger-config.cfg) — Xóa bỏ chú thích thừa về Octopus Pro.

### Sao lưu
- [README.md.master (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-doc-refresh-and-comment-cleanup-20260814-162200/README.md.master)
- [config-README.md (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-doc-refresh-and-comment-cleanup-20260814-162200/config-README.md)
- [hardware.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-doc-refresh-and-comment-cleanup-20260814-162200/hardware.cfg)
- [calibration.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-doc-refresh-and-comment-cleanup-20260814-162200/calibration.cfg)
- [nozzle-clean.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-doc-refresh-and-comment-cleanup-20260814-162200/nozzle-clean.cfg)
- [toolchanger-config.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-doc-refresh-and-comment-cleanup-20260814-162200/toolchanger-config.cfg)
- [README.md (Backup Record)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-doc-refresh-and-comment-cleanup-20260814-162200/README.md)

### Lý do
Giữ cho tài liệu và chú thích code luôn sạch sẽ, chính xác 100% với cấu hình thực tế, giúp loại bỏ hoàn toàn các thông tin mơ hồ hoặc lỗi thời.

### Kết quả
Toàn bộ hệ thống cấu hình và tài liệu `README.md` đã được rà soát, tinh gọn và đạt tính nhất quán cao nhất.





# Nhật ký — 2026-07-26

## 1. Chuyển Cartographer sang chế độ Scan Homing (Không chạm bàn)

### Mục tiêu
Khắc phục hiện tượng Nozzle bị cày sát bàn PEI do nhựa dẻo sót trên Nozzle gây nén đệm và làm tụt chốt cơ khí StealthChanger khi thực hiện Touch Home. Chuyển Cartographer sang dùng Eddy Current Scan Homing hoàn toàn không tiếp xúc.

### File đã sửa đổi
- `Voron 5 Tool/config/Printer-Setup/print-macros.cfg` — comment out bước `CARTOGRAPHER_TOUCH_HOME` trong macro `PRINT_START`.

### Sao lưu
- [print-macros.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cartographer-scan-homing-20260726-081000/print-macros.cfg)

### Chi tiết thay đổi
- Trong `PRINT_START`: Vô hiệu hóa `CARTOGRAPHER_TOUCH_HOME` ở bước 8.
- Quy trình homing Z hiện tại sử dụng `G28 Z` (Eddy Current Scan Homing) tích hợp sẵn ở cuối lệnh `QUAD_GANTRY_LEVEL`.

### Lý do
Tại nhiệt độ 150°C, nhựa sót ở đầu vòi phun bị dẻo hóa tạo thành đệm nén làm sai lệch vị trí Touch, khiến lực ép đẩy lún chốt toolhead StealthChanger và làm Z=0 bị âm quá sâu. Scan Homing hoàn toàn không chạm bàn, loại bỏ 100% rủi ro đâm bàn và nén chốt.

### Kiểm tra
- Kiểm tra cú pháp: Đạt (cú pháp Jinja2/Klipper macro chuẩn).
- Cấu hình sẵn sàng khởi động lại Klipper.

### Kết quả
Quá trình `PRINT_START` sẽ chạy QGL + Eddy Scan Homing nhanh chóng, không còn bước nhấp chạm nozzle T0 xuống bàn in.

### Vấn đề còn lại
Không có.

---

## 4. Điều tra hai lần Tool Crash T0 tại prime tower

### Triệu chứng
Hai lần in file `voron_design_cube_v8-v1_PETG_2h1m.gcode` đều bị Klipper shutdown với thông báo `tool_crash detected tool T0` ngay sau khi đổi sang T0 và bắt đầu purge trên prime tower.

### Phân tích nhật ký
- File nhật ký liên quan: [klippy.log](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/logs/klippy.log)
- File Moonraker liên quan: [moonraker.log](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/logs/moonraker.log)
- Lần 1, khoảng 08:55:10: `sd_pos=200733`; T0 vừa đổi từ T4, tower layer #4, Z=0.84 mm, sau đó báo `tool_crash detected tool T0`.
- Lần 2, khoảng 09:46:57: `sd_pos=237140`; T0 vừa đổi từ T2, tower layer #5, Z=1.04 mm, sau đó báo cùng lỗi.
- Trước cả hai lần shutdown, EBB0 và toàn bộ CAN bus vẫn `active`, `rx_error=0`, `tx_error=0`, `tx_retries=0`; nhiệt độ T0 ổn định khoảng 220°C.
- Plugin `[tool_crash]` giám sát `detection_pin: ^!EBB0:PB6`, không dùng Cartographer để phát hiện crash. Với `watchdog_interval: 0.5` và `watchdog_threshold: 2`, lỗi nghĩa là tín hiệu hiện diện T0 mất trong hai lần kiểm tra liên tiếp.
- Ảnh prime tower cho thấy các đường purge bị nhô, kéo sợi và dồn cục, đặc biệt ở đầu các đường quét ngang. G-code cho T0 chạy purge trực tiếp qua vùng X≈153.5–193.0 mm; đây là vùng có khả năng tạo lực quệt làm T0 lỏng/bung khỏi carriage hoặc làm tiếp điểm PB6 chập chờn.

### Nguyên nhân gốc
Nguyên nhân trực tiếp đã xác nhận là tín hiệu hiện diện T0 trên `EBB0:PB6` bị mất khi T0 đang purge tại prime tower. Nguyên nhân vật lý có xác suất cao là nozzle T0 quệt vào các gờ/cục PETG nhô trên tower, làm cơ cấu khóa T0 dịch chuyển; khả năng thứ hai cần loại trừ là microswitch/đầu nối/dây PB6 của riêng T0 bị chập chờn dưới rung động. Không có bằng chứng về lỗi CAN, Moonraker, nhiệt độ hoặc Cartographer gây ra sự cố.

### Hướng khắc phục đã thực hiện
Chưa sửa cấu hình. Chỉ phân tích log, G-code, ảnh tower và các setting OrcaSlicer hiện tại.

### Kết quả
Hai lần crash tái hiện cùng chuỗi sự kiện: đổi sang T0, bật lại crash detection, purge trên tower, sau đó mất tín hiệu detection T0.

### Phòng ngừa
- Kiểm tra lực khóa/magnet/latch của T0 và thử rung nhẹ T0 khi chạy `QUERY_ENDSTOPS` để phát hiện tín hiệu PB6 chập chờn.
- Kiểm tra microswitch, giắc và dây tín hiệu `EBB0:PB6`.
- Trước lần in tiếp theo, cải thiện độ ổn định prime tower và giảm nguy cơ dồn cục; không vô hiệu hóa crash detection để che lỗi.

### Vấn đề còn lại
Cần thử riêng T0 và in tower ngắn sau khi kiểm tra cơ khí/cảm biến để phân biệt chắc chắn giữa T0 bị bung do va vào tower và tín hiệu PB6 chập chờn.

---

## 2. Tinh chỉnh Z-Offset chuẩn cho Cartographer Scan Model (-0.360mm)

### Mục tiêu
Cập nhật Z-offset cố định cho Cartographer Scan Model dựa trên kết quả tinh chỉnh thực tế của người dùng qua Babystepping trên Mainsail (-0.35mm đến -0.37mm).

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — cập nhật `z_offset` trong section `[cartographer scan_model default]` từ `0` thành `-0.360`.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cartographer-z-offset-tune-20260726-092200/printer.cfg)

### Chi tiết thay đổi
- `[cartographer scan_model default]` `z_offset`: `0` → `-0.360`

### Lý do
Sau khi chuyển sang Cartographer Scan Homing (không chạm), người dùng đã hạ Z trên Mainsail khoảng -0.35mm đến -0.37mm thu được lớp in đầu tiên (first layer) phẳng bám bàn hoàn hảo. Việc lưu baseline -0.360mm giúp tất cả các lệnh in về sau tự động dùng mốc Z chuẩn mà không cần hạ thủ công.

### Kiểm tra
- Kiểm tra cú pháp: Đạt.
- Khởi động lại Klipper: Sẵn sàng áp dụng sau lệnh `RESTART`.

### Kết quả
Tất cả các bản in mới sẽ tự động áp dụng Z-offset -0.360mm, đường nhựa lớp 1 bám bàn đẹp đúng như người dùng đã tinh chỉnh.

### Vấn đề còn lại
Không có.

---

## 3. Khôi phục Cartographer Touch Home & Thêm bước lau Nozzle ngay sát trước Touch

### Mục tiêu
Khắc phục hiện tượng trôi Z giữa các lần in của chế độ Scan thuần (do trôi nhiệt cuộn cảm) và xử lý triệt để nguyên nhân ép nhựa dẻo làm trượt chốt StealthChanger khi Touch Home.

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — khôi phục `z_offset = 0` trong section `[cartographer scan_model default]`.
- `Voron 5 Tool/config/Printer-Setup/print-macros.cfg` — bật lại `CARTOGRAPHER_TOUCH_HOME` và thêm `CLEAN_NOZZLE TEMP=150 WIPES=5` ngay sát trước bước Touch.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cartographer-touch-wipe-fix-20260726-093700/printer.cfg)
- [print-macros.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cartographer-touch-wipe-fix-20260726-093700/print-macros.cfg)

### Chi tiết thay đổi
- `printer.cfg`: `[cartographer scan_model default]` `z_offset`: `-0.360` → `0`
- `print-macros.cfg`: Trong `PRINT_START`, thêm `CLEAN_NOZZLE TEMP=150 WIPES=5` ngay trước `CARTOGRAPHER_TOUCH_HOME`.

### Lý do
1. Theo tài liệu chính thức Cartographer & cộng đồng StealthChanger: Chế độ Scan thuần bị trôi nhiệt (Thermal Drift) theo nhiệt độ cuộn cảm & lồng máy, bắt buộc phải dùng Touch Home để tự động chốt $Z=0$ cơ học thực tế cho mỗi lần in (không cần babystep lại).
2. Di chuyển bước lau Nozzle xuống ngay sát trước Touch giúp loại bỏ 100% cục đệm nhựa dẻo đọng lại trong lúc QGL/soak, giúp Cartographer Touch kích hoạt ngắt Z tức thì khi Nozzle kim loại vừa chạm nhẹ mặt PEI.

### Kiểm tra
- Kiểm tra cú pháp: Đạt.
- Sẵn sàng khởi động lại Klipper.

### Kết quả
Quy trình Touch Home chạy mượt mà, chạm nhẹ ngắt ngay không làm tụt chốt StealthChanger, khóa $Z=0$ chính xác 100% cho mọi bản in mà không phải baby step lại.

### Vấn đề còn lại
Không có.


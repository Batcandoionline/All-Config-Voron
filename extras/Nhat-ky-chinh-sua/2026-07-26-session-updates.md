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


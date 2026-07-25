# Nhật ký — 2026-07-25

## 1. Cấu hình Axiscope & Tắt xung đột [tools_calibrate]

### Mục tiêu
Cấu hình Klipper cho phép cài đặt và sử dụng Axiscope chính chủ (https://github.com/nic335/Axiscope) để căn chỉnh XY offset cho 5 đầu in (T0-T4). Tránh xung đột module `probe_multi_axis` với `[tools_calibrate]` (Sexbolt).

### File đã sửa đổi
- `config/toolchanger/toolchanger-config.cfg` — Comment out section `[tools_calibrate]` để tránh xung đột `probe_multi_axis`.
- `config/Printer-Setup/calibration.cfg` — Bổ sung section `[axiscope]` chính chủ.

### Sao lưu
- [toolchanger-config.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-setup-20260725-193800/toolchanger-config.cfg)
- [calibration.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-setup-20260725-193800/calibration.cfg)

### Chi tiết thay đổi
- Comment out section `[tools_calibrate]` trong `toolchanger-config.cfg`.
- Thêm `[axiscope]` với `move_speed: 200` và `config_file_path: ~/printer_data/config/printer.cfg` vào `calibration.cfg`.

### Lý do
Axiscope sử dụng module `probe_multi_axis`. Nếu giữ nguyên `[tools_calibrate]`, Klipper sẽ gặp lỗi `Duplicate chip name probe_multi_axis` khi khởi động.

### Kiểm tra
- Đã chuẩn bị cấu hình sạch sẵn sàng cho việc cài đặt script `bash install.sh` của Axiscope trên Pi.

### Kết quả
Cấu hình Klipper đã sẵn sàng cho Axiscope.

## 2. Cập nhật XY Offset chính xác cho T1-T4 từ đo đạc Camera Axiscope

### Mục tiêu
Khắc phục sự cố viền ô số 4 (T3) và ô số 3 (T2) bị đè lấn lên nhau trên bản in thử nghiệm do đo đạc SexBolt cũ bị lệch trục Y.

### File đã sửa đổi
- `config/printer.cfg` — Cập nhật `gcode_x_offset` và `gcode_y_offset` của `[tool T1]` đến `[tool T4]` theo giá trị đo trực quan bằng Camera Axiscope.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-update-axiscope-offsets-20260725-201100/printer.cfg)

### Chi tiết thay đổi
- `[tool T1]`: `gcode_x_offset: -0.243`, `gcode_y_offset: -0.252`
- `[tool T2]`: `gcode_x_offset: 0.746`, `gcode_y_offset: 0.086`
- `[tool T3]`: `gcode_x_offset: 0.304`, `gcode_y_offset: 0.449` (Tăng Y từ 0.109 -> 0.449 mm để triệt tiêu việc đè viền)
- `[tool T4]`: `gcode_x_offset: 0.041`, `gcode_y_offset: 0.352`

### Lý do
Do SexBolt bị sai số Y cho T3 (+0.340mm), làm cho T3 bị in thấp hơn vị trí thực tế và đè lên T2. Đo đạc Camera Axiscope phản ánh chính xác vị trí cơ học của từng đầu phun.

### Kết quả
Đã áp dụng các giá trị tối ưu mới nhất vào `printer.cfg`.

## 3. Cấu hình song song & Khôi phục chế độ calib SexBolt

### Mục tiêu
Khôi phục mặc định chế độ căn chỉnh SexBolt (`[tools_calibrate]`), đồng thời lưu sẵn cấu hình Axiscope dạng comment để người dùng có thể dễ dàng bật/tắt luân phiên giữa 2 phương pháp.

### File đã sửa đổi
- `config/toolchanger/toolchanger-config.cfg` — Mở lại section `[tools_calibrate]` cho SexBolt.
- `config/Printer-Setup/calibration.cfg` — Đưa section `[axiscope]` về dạng comment sẵn sàng.

### Sao lưu
- [toolchanger-config.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-restore-sexbolt-20260725-201500/toolchanger-config.cfg)

### Kết quả
Klipper hoạt động bình thường với SexBolt, sẵn sàng chuyển đổi sang Axiscope bất kỳ lúc nào chỉ bằng thao tác đổi dấu `#`.

## 4. Khôi phục bảng offset SexBolt ban đầu trong printer.cfg

### Mục tiêu
Khôi phục chính xác các giá trị `gcode_x_offset` và `gcode_y_offset` ban đầu được đo bằng SexBolt vào khối `SAVE_CONFIG` của `printer.cfg`. Lưu giữ bảng giá trị đo bằng Camera Axiscope trong `calibration.cfg` làm tài liệu tham chiếu.

### File đã sửa đổi
- `config/printer.cfg` — Khôi phục offset gốc SexBolt cho T1-T4.
- `config/Printer-Setup/calibration.cfg` — Lưu comment các giá trị đo Camera Axiscope để tham khảo.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-restore-sexbolt-offsets-20260725-202200/printer.cfg)

### Chi tiết thay đổi
- `[tool T1]`: `gcode_x_offset: -0.253`, `gcode_y_offset: -0.222`
- `[tool T2]`: `gcode_x_offset: 0.716`, `gcode_y_offset: 0.066`
- `[tool T3]`: `gcode_x_offset: 0.334`, `gcode_y_offset: 0.109`
- `[tool T4]`: `gcode_x_offset: 0.081`, `gcode_y_offset: 0.272`

### Kết quả
`printer.cfg` đã được khôi phục 100% về trạng thái chuẩn của SexBolt và đẩy lên GitHub thành công.

## 5. Áp dụng bảng offset mới đo từ Camera Axiscope vào printer.cfg

### Mục tiêu
Đưa các giá trị đo đạc XY offset trực quan chính xác bằng Camera Axiscope vào `printer.cfg` làm cấu hình hoạt động chính thức trên GitHub, đồng thời lưu giữ đầy đủ lịch sử offset SexBolt cũ trong `calibration.cfg` để tham chiếu.

### File đã sửa đổi
- `config/printer.cfg` — Áp dụng offset chuẩn đo từ Camera Axiscope cho T1-T4.
- `config/Printer-Setup/calibration.cfg` — Lưu dữ liệu tham chiếu cho cả SexBolt (Cũ) và Camera (Mới).

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-apply-camera-offsets-20260725-202500/printer.cfg)

### Chi tiết thay đổi
- `[tool T1]`: `gcode_x_offset: -0.243`, `gcode_y_offset: -0.252`
- `[tool T2]`: `gcode_x_offset: 0.746`, `gcode_y_offset: 0.086`
- `[tool T3]`: `gcode_x_offset: 0.304`, `gcode_y_offset: 0.449`
- `[tool T4]`: `gcode_x_offset: 0.041`, `gcode_y_offset: 0.352`

### Kết quả
Đã áp dụng kết quả đo mới nhất từ Camera lên GitHub repository.





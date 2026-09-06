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

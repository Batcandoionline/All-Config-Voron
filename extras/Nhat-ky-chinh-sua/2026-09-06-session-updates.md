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


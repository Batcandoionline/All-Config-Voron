# Nhật ký — 2026-08-01

## 1. Cập nhật vị trí dock StealthChanger theo snapshot tải về

### Mục tiêu
Đồng bộ cấu hình production với vị trí vật lý mới của dock các tool, sử dụng snapshot `extras/Config download/config-20260801-181843`.

### File đã sửa đổi
- `config/toolchanger/tools/T0.cfg` — cập nhật `params_park_x` và `params_park_y`.
- `config/toolchanger/tools/T1.cfg` — cập nhật `params_park_x` và `params_park_y`.
- `config/toolchanger/tools/T2.cfg` — cập nhật `params_park_y`.
- `config/toolchanger/tools/T3.cfg` — cập nhật `params_park_y`.
- `config/toolchanger/tools/T4.cfg` — cập nhật `params_park_x` và `params_park_y`.

### Sao lưu
- [Backup trước cập nhật](file:///C:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-dock-position-update-20260801-182244/)

### Chi tiết thay đổi
- T0: X `30.70 → 30.20`, Y `1.8 → 1.3`.
- T1: X `103.5 → 104`, Y `1.5 → 1.1`.
- T2: Y `2.1 → 1.6`.
- T3: Y `2.3 → 2.5`.
- T4: X `321 → 321.5`, Y `3.1 → 2.6`.
- Giữ nguyên `params_park_z: 343`, các section khác và toàn bộ comment không liên quan.

### Lý do
Các giá trị mới là dữ liệu vị trí vật lý đã tải về từ máy in; comment giữ lại giá trị cũ để truy vết và rollback.

### Kiểm tra
- So sánh SHA-256 với snapshot `config-20260801-181843`: đạt, toàn bộ file trong snapshot khớp sau cập nhật.
- Kiểm tra cú pháp tĩnh: đạt; các section `[tool T0]`–`[tool T4]` giữ nguyên, giá trị dock là số hợp lệ, `git diff --check` không phát hiện lỗi whitespace.
- Khởi động lại Klipper / thử đổi tool: chưa thực hiện trong môi trường này.

### Kết quả
Cấu hình production đã đồng bộ chính xác với snapshot tải về, chỉ gồm 5 file vị trí dock.

### Vấn đề còn lại
Cần xác nhận thực tế bằng thao tác đổi tool an toàn trên máy in sau khi triển khai.

# Nhật ký — 2026-09-04

## 1. Cấu hình CANCEL_PRINT cất tool về dock thay vì đưa cụm ra sau bàn

### Mục tiêu
Khắc phục hiện tượng khi bấm cancel bản in máy không cất tool về dock mà lại nhấc/giữ T0 và đưa cả cụm toolhead ra sát vách sau bàn in. Đưa quy trình cancel về đúng chuẩn an toàn: tự động nhả tool active về dock của nó (`UNSELECT_TOOL`) và đỗ shuttle rỗng tại vị trí an toàn phía sau bàn (`Y = max - 20 mm`).

### File đã sửa đổi
- `config/Printer-Setup/fans-leds.cfg` — Cập nhật macro hook `_CUSTOM_CANCEL_CLEANUP` thay thế logic chọn `T0` bằng `UNSELECT_TOOL`, và đổi tọa độ đỗ shuttle rỗng từ `Y{th.axis_maximum.y - 2}` thành `Y{th.axis_maximum.y - 20}`.

### Sao lưu
- [fans-leds.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cancel-dock-tool-20260904-065500/fans-leds.cfg)
- [README.md (Backup Record)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cancel-dock-tool-20260904-065500/README.md)

### Chi tiết thay đổi
- Trong macro `[gcode_macro _CUSTOM_CANCEL_CLEANUP]`:
  - Thay thế đoạn mã kiểm tra `active_tool > 0 -> T0`:
    ```jinja2
    {% set active_tool = printer.toolchanger.tool_number|default(-1)|int %}
    {% if active_tool > 0 %}
        T0
    {% elif active_tool < 0 %}
        RESPOND TYPE=echo MSG="[CANCEL] Toolchanger has no active tool - skipping T0 pickup"
    {% endif %}
    ```
    thành:
    ```jinja2
    # Drop active tool to dock (leave shuttle empty).
    {% set active_tool = printer.toolchanger.tool_number|default(-1)|int %}
    {% if active_tool >= 0 %}
        UNSELECT_TOOL
    {% else %}
        RESPOND TYPE=echo MSG="[CANCEL] Toolchanger has no active tool to dock"
    {% endif %}
    ```
  - Thay đổi tọa độ đỗ shuttle rỗng:
    `G0 X{th.axis_maximum.x // 2} Y{th.axis_maximum.y - 2} F9000`
    thành:
    `G0 X{th.axis_maximum.x // 2} Y{th.axis_maximum.y - 20} F9000`
  - Đồng bộ comment mô tả quy trình cleanup của macro.

### Lý do
- Trước đây, khi hủy lệnh in (`CANCEL_PRINT`), hook `_CUSTOM_CANCEL_CLEANUP` kiểm tra nếu đang ở tool T1..T4 thì nhả tool và gọi `T0` (nhặt T0 lên), còn nếu đang ở T0 thì không làm gì. Sau đó macro đưa toàn bộ toolhead đang gắn tool ra đỗ ở tọa độ `Y = max - 2` (rất sát phía sau bàn in, nguy cơ chạm vào dock hoặc chốt).
- Việc gọi `UNSELECT_TOOL` đảm bảo bất kỳ tool nào đang active (T0–T4) đều được trả về dock riêng của nó. Carriage/shuttle lúc này hoàn toàn rỗng, di chuyển lùi về đỗ tại `Y = max - 20` (giống như logic chuẩn trong `PRINT_END`), đảm bảo khoảng cách an toàn 20 mm cho các chu trình homing hoặc thao tác tiếp theo.

### Kiểm tra
- Kiểm tra cú pháp Jinja2: Đạt (30/30 gcode macro trong file parse thành công).
- Kiểm tra logic: Khớp 100% với cơ chế `STEP 4` và `STEP 5` trong `PRINT_END` của `print-macros.cfg`.

### Kết quả
- Macro `CANCEL_PRINT` (thông qua `_CUSTOM_CANCEL_CLEANUP`) giờ đây sẽ tự động cất tool đang sử dụng vào dock và đỗ shuttle rỗng phía sau bàn in.

### Vấn đề còn lại
- Nạp cấu hình lên máy in thực tế và khởi động lại Klipper (`FIRMWARE_RESTART` hoặc restart dịch vụ) để áp dụng macro mới.

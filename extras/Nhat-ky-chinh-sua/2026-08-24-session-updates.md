# Nhật ký chỉnh sửa — 2026-08-24

## 1. Chuyển cấu hình ToolVision vào Printer-Setup

### Yêu cầu và sao lưu

- Người vận hành yêu cầu bản cài riêng của máy đặt cấu hình ToolVision trong
  `config/Printer-Setup/` và giữ mọi JSON được sinh ra dưới
  `config/Generated-Data/ToolVision/`.
- Trước khi sửa, đã sao lưu chính xác `printer.cfg`, `tool_vision.cfg` và
  `install.sh` vào
  `extras/backups/pre-move-toolvision-to-printer-setup-20260823-220605/`.
- Hai mục `extras/Config download/config-20260821-172111*` không liên quan tiếp
  tục được giữ nguyên, không stage hoặc sửa.

### Thay đổi local

- Chuyển `config/tool_vision.cfg` thành
  `config/Printer-Setup/tool-vision.cfg` và sửa include trong `printer.cfg`.
- Giữ nguyên hai đường dẫn runtime:
  - `~/printer_data/config/Generated-Data/ToolVision/state.json`.
  - `~/printer_data/config/Generated-Data/ToolVision/results.json`.
- Cập nhật preflight trong `config/scripts/install.sh` để nhận include mới.
  `rsync --delete` vẫn exclude toàn bộ `Generated-Data/`, vì vậy deploy không
  xóa state hoặc kết quả ToolVision hiện có.
- Cập nhật cây thư mục và mô tả quyền sở hữu dữ liệu trong `README.md` và
  `config/README.md`.

### Kiểm tra trước commit

- Cả 11 include trực tiếp từ `printer.cfg` đều có target local hợp lệ.
- File ToolVision mới có 12 section, vẫn giữ đúng section `[tool_vision]` và
  toàn bộ macro panel cũ.
- Kiểm tra chính xác state/result path và `Generated-Data/` rsync exclude: đạt.
- `git diff --check`: đạt; chỉ có cảnh báo chuyển LF/CRLF của Git trên Windows.
- PC không cài Bash/WSL. Kiểm tra `bash -n` qua CM4 chưa thực hiện được vì SSH
  `192.168.1.43:22` timeout; chưa deploy hoặc restart dịch vụ nào.

### Commit và trạng thái deploy

- Commit `e45c738` (`config: move ToolVision into Printer-Setup`) đã được push
  lên `origin/main`; chỉ stage các file của tác vụ và snapshot bắt buộc.
- Kiểm tra mạng lần hai xác nhận `ping=false`, SSH port 22 và Moonraker port
  7125 đều không truy cập được. Vì vậy chưa chạy `update.sh`, chưa restart
  Moonraker/Klipper và cấu trúc file live trên CM4 chưa thay đổi.
- Dữ liệu JSON live đã nằm đúng `Generated-Data/ToolVision/` từ cấu hình trước;
  phần deploy còn lại chỉ chuyển file cấu hình vào `Printer-Setup/` và nạp lại
  include khi CM4 online.

## 2. Hướng dẫn tích hợp ToolVision song ngữ

- Sau khi máy được bật lại, kiểm tra trước deploy xác nhận SSH hoạt động; Klipper,
  Moonraker và ToolVision service đều active; printer `ready`/`standby`, không
  pause, ToolVision `busy=false`, no last error và mọi heater target bằng 0.
- Tạo hai tài liệu đồng bộ:
  - `extras/docs/toolvision-integration-guide.en.md` — English.
  - `extras/docs/toolvision-integration-guide.vi.md` — Tiếng Việt.
- Hai bản cùng mô tả ownership của runtime/config/generated data, include mới,
  preflight installer, quy trình update/restart, smoke test không chuyển động,
  Z-method semantics, backup/rollback và troubleshooting.
- Cập nhật `README.md` và `config/README.md` để liên kết trực tiếp tới cả hai
  ngôn ngữ. Tài liệu ghi rõ mọi JSON ToolVision phải ở
  `Generated-Data/ToolVision/` và không được tạo JSON rỗng thủ công.

## 3. Deploy bố cục ToolVision mới lên CM4

### Preflight và deploy

- Trước deploy: Klipper `ready`, printer `standby`, không pause, ToolVision
  `busy=false`, no last error; bed và T0-T4 đều target `0`.
- Xác nhận live còn `config/tool_vision.cfg`, chưa có file mới trong
  `Printer-Setup/`, và ghi SHA-256 của hai JSON trước khi thay đổi.
- Chạy đúng một lần `bash ~/printer_data/config/scripts/update.sh`. Installer
  kiểm tra KTC-Easy symlink và tool_crash patch thành công, xóa file root cũ,
  tạo `Printer-Setup/tool-vision.cfg` và tạo rollback snapshot:
  `/home/voron/printer_data/config_backups/config-install-20260824-153138/`.
- `bash -n` trên `scripts/install.sh` live đạt. Include mới, state/result path và
  exclude `Generated-Data/` đều khớp cấu hình đã push.

### Bảo toàn dữ liệu và restart

- SHA-256 của JSON không đổi trước/sau deploy và restart:
  - `state.json`: `506273e699fbc9a8d9d539afb7141a1fad643a40d9a94e18660bbdc602d1fdca`.
  - `results.json`: `6f91a57179071ecb8d70d58f8af35701d162df1c4b9bce536b430b7712680466`.
- Restart Moonraker qua API chính thức; service active lại lúc
  `2026-08-24 15:32:35 +07`. Sau đó gọi `FIRMWARE_RESTART` đúng một lần và chờ
  Klipper trở lại `ready`.

### Smoke test không chuyển động

- Klipper, Moonraker và `tool-vision.service` đều active; Moonraker không có
  warning hoặc failed component; 300 dòng cuối `klippy.log` không có mẫu lỗi
  startup/config được kiểm tra.
- Object `tool_vision` và macro `TOOL_VISION` đều được nạp. Status báo service
  online `3.4.0-rc1`, method `cartographer_touch`, Z ready, switch ready,
  Cartographer Touch ready và no last error.
- `QUERY_ENDSTOPS`: `ToolVision switch:open`; X/Y/Z endstop đều open.
- Sau cùng printer vẫn `standby`, không pause, ToolVision `busy=false`, mọi
  heater target `0`. Không home, probe, toolchange, setup hoặc calibration.
- CM4 hiện có bốn rollback snapshot nhỏ sau khi installer tạo bản mới; không
  xóa thêm backup trong tác vụ này.

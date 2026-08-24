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

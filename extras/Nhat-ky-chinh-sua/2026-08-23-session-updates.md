# Nhật ký — 2026-08-23

## 1. Giao quyền quản lý KTC readonly và đồng bộ trạng thái production

### Mục tiêu

- Ghi nhận xác nhận của người vận hành: Cartographer đã hết lỗi, cảm biến T4 đã
  hết lỗi và Input Shaper T0–T4 đã hiệu chỉnh.
- Loại bỏ hướng dẫn kTAMV cũ và sửa các thông số tài liệu không còn khớp máy.
- Giao toàn quyền quản lý `toolchanger/readonly-configs/` cho KTC-Easy.
- Không can thiệp máy khi bản in còn chạy; chỉ triển khai sau khi người dùng xác
  nhận máy đã ở chế độ chờ.

### File đã sửa đổi

- `config/scripts/install.sh` — yêu cầu đủ sáu symlink KTC hợp lệ trước mọi thay
  đổi và luôn loại trừ toàn bộ `toolchanger/readonly-configs/` khỏi `rsync`.
- `config/Printer-Setup/input-shaper.cfg` — ghi rõ fallback T0 đã hiệu chỉnh và
  được xác nhận ngày 2026-08-23.
- `config/toolchanger/tools/T0.cfg` đến `T4.cfg` — sửa comment profile để khớp
  chính xác loại shaper, tần số và damping đang dùng; không đổi giá trị runtime.
- `README.md`, `config/README.md` — bổ sung quyền sở hữu KTC, preflight và quy
  tắc chỉ chạy installer khi máy idle.
- `extras/docs/huong-dan-he-thong-stealthchanger.md` — bỏ workflow kTAMV đã gỡ,
  cập nhật Axiscope PF2 production, trạng thái lỗi, Input Shaper và sửa nhầm
  `gcode_x_offset T2 = 0.746` thành Z-offset.
- `.gitmodules` — bổ sung metadata còn thiếu cho `extras/Axiscope-reference`.
- `.agents/KNOWN_ISSUES.md`, `.agents/TODO.md`, `.agents/CHANGELOG.md` và
  `.agents/DECISIONS.md` — cập nhật trạng thái và quyết định kỹ thuật ở workspace.

### Sao lưu

- [Backup local trước sửa](<file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-ktc-ownership-and-doc-sync-20260823-083206/>)
- Backup toàn bộ config máy trước đổi symlink:
  `/home/voron/printer_data/config_backups/pre-ktc-ownership-20260823-083950/`
  (35 file, 388 KiB, có `SHA256SUMS` và `KTC_COMMIT`).
- Backup tự động ngay trước deploy:
  `/home/voron/printer_data/config_backups/config-install-20260823-084215/`.

### Chi tiết thay đổi

- Đối chiếu installer chính thức KTC-Easy và checkout đang cài ở commit
  `e881fe40949a3999b0d63f59c22df589474eae9b`.
- Sáu file readonly cũ đều là file thường. Năm file khớp byte với KTC source;
  riêng `homing.cfg` là bản cũ. Bản KTC hiện tại bỏ logic tool-probe legacy;
  cấu hình người dùng đã có override `TOOL_BED_MESH_CALIBRATE` cho Cartographer
  gắn cố định trên shuttle.
- Do `sudo -n` không được cấp và installer KTC chính thức sẽ dừng ở bước restart,
  áp dụng chính xác sáu lệnh symlink của option 2 (shuttle-mounted
  Cartographer), rồi restart Klipper qua Moonraker:
  - `calibrate-offsets.cfg`
  - `crash-detection.cfg`
  - `homing.cfg`
  - `toolchanger-include.cfg` → `toolchanger-include_scanner.cfg`
  - `toolchanger-macros.cfg`
  - `toolchanger.cfg`
- Commit cấu hình `3f7547b` (`fix: enforce KTC readonly ownership`) được push lên
  `origin/main`, sau đó máy chạy `bash scripts/update.sh` từ GitHub đúng một lần.
- Klipper được reload đúng một lần bằng Moonraker API. Sau reload chạy
  `INITIALIZE_TOOLCHANGER` không chuyển động để khôi phục trạng thái active tool.

### Kiểm tra

- `bash -n config/scripts/install.sh`: đạt.
- `bash -n config/scripts/update.sh`: đạt.
- `git diff --check`: đạt.
- Quét section của 22 file CFG: đạt.
- `.gitmodules` có đủ `tool_crash` và `Axiscope-reference`: đạt.
- Máy trước deploy: job `cancelled`, không pause, mọi heater target `0`.
- Klipper và Moonraker sau reload: `active`; printer state `ready`/`standby`.
- Sáu readonly path: đều là symlink hợp lệ tới checkout KTC-Easy.
- 7/7 Git blob (`install.sh`, `input-shaper.cfg`, T0–T4) khớp byte với file máy.
- Object production: `axiscope`, `cartographer`, `toolchanger` đều được nạp.
- G-code có `CALIBRATE_ALL_Z_OFFSETS`, `CALIBRATION_STATUS`,
  `CARTOGRAPHER_TOUCH`, `SET_INPUT_SHAPER` và `INITIALIZE_TOOLCHANGER`.
- KTC sau initialize: status `ready`, active `tool T0`, detected `tool T0`.
- Input Shaper active T0: X `3hump_ei @ 98.6 Hz`, damping `0.081`; Y
  `mzv @ 35.0 Hz`, damping `0.076`.
- Không chạy homing, toolchange, calibration hoặc chuyển động kiểm thử.

### Kết quả

KTC-Easy hiện là chủ sở hữu thật của toàn bộ readonly config trên máy và các lần
deploy All-Config sau sẽ dừng an toàn nếu symlink thiếu/hỏng. Tài liệu khớp lại
trạng thái production: Axiscope PF2 active, ToolVision inactive, kTAMV đã gỡ,
Cartographer/T4 không còn lỗi mở và Input Shaper T0–T4 đã hiệu chỉnh.

### Vấn đề còn lại

- Pressure Advance theo từng tool/material vẫn là hạng mục tối ưu.
- Tối ưu quạt từng tool vẫn là hạng mục cải tiến.
- Giám sát nhiệt độ Cartographer là tùy chọn phòng ngừa, không phải lỗi đang mở.
- Chưa chạy thử chuyển động pickup/dropoff trong phiên này; không cần thiết vì
  chỉ đổi quyền sở hữu readonly và nội dung KTC được lấy từ checkout đang cài.

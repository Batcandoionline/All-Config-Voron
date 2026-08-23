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

## 2. Đánh giá mã nguồn và chuẩn bị canary ToolVision PF2

### Mục tiêu

- Đọc trực tiếp mã nguồn ToolVision, không chỉ tài liệu Markdown, trước khi cho
  phép nạp vào Klipper production.
- Chuẩn bị canary đo Z-offset bằng microswitch PF2 theo chế độ report-only;
  không tự ghi đè offset đang dùng.
- Chỉ cho phép chuyển sang bước homing/toolchange/probe sau khi runtime, dịch vụ
  và cấu hình đều vượt kiểm tra không chuyển động.

### Đánh giá mã nguồn

- Đã kiểm tra installer/uninstaller, năm module Klipper, state/config layout,
  server camera/API, detection/transform và toàn bộ test liên quan.
- Điểm an toàn đạt: kết quả chỉ được báo cáo; không gọi `SAVE_CONFIG` hoặc
  `SAVE_TOOL_PARAMETER`; chuyển động đi lên safe-Z trước; switch phải ở trạng
  thái open; mỗi tool lấy năm mẫu, dùng median, tolerance 0.05 mm và tối đa hai
  lần retry; file state được ghi atomic; API mặc định chỉ bind loopback.
- Rủi ro chưa đóng của upstream: HTTP đồng bộ trong Klipper reactor; chưa
  preflight envelope của mọi tool trước khi bắt đầu; nhánh lỗi probe chưa luôn
  retract; khôi phục tool/G-code state và tắt heater vẫn là best-effort; adapter
  offset có đường fallback về 0 khi lookup thất bại.
- T0 production đang có XYZ offset bằng 0 nên thỏa giả định reference tool của
  mã nguồn. Tọa độ station đã lưu cộng offset T0-T4 đều nằm trong giới hạn máy;
  đây mới là kiểm tra số học, chưa thay thế quan sát trực tiếp khi chạy.
- Checkout upstream được khóa ở commit
  `2b3bf2c6a0e2cad3f579fe755cefca65c69c3dc3`. Mã tự nhận
  `3.4.0-rc1` nhưng chưa có tag tương ứng; `git describe` là
  `v3.3.0-rc1-11-g2b3bf2c6`, vì vậy chỉ được xem là development canary.

### Sao lưu

- Backup local trước khi chuẩn bị config:
  `extras/backups/pre-toolvision-z-canary-20260823-211530/`.
- Backup máy đã kiểm tra bundle và toàn bộ SHA-256:
  `/home/voron/printer_data/config_backups/pre-toolvision-z-canary-20260823-211716/`.
- Lần thử backup trước đó tại
  `/home/voron/printer_data/config_backups/pre-toolvision-z-canary-20260823-211658/`
  không hoàn tất bước verify Git bundle và được giữ nguyên để truy vết; không sử
  dụng làm điểm phục hồi chính.

### Chuẩn bị local và runtime máy

- `config/printer.cfg`: chuẩn bị include `tool_vision.cfg`.
- `config/tool_vision.cfg`: thêm section PF2 và panel Mainsail; giữ nguyên nguyên
  tắc report-only.
- `config/Printer-Setup/calibration-probe.cfg`: chuẩn bị tắt section Axiscope
  nhưng giữ nguyên nội dung comment để rollback.
- `config/moonraker.conf`: chuẩn bị updater ToolVision theo nhánh `main`.
- `config/scripts/install.sh`: thêm preflight checkout, venv, systemd unit và đủ
  năm symlink module Klipper trước khi cho deploy.
- Runtime `/home/voron/Tool-Vision` đã cập nhật tới commit khóa; venv giữ độc
  lập và đủ năm symlink module trỏ chính xác vào checkout.

### Kiểm tra đã đạt

- Máy phát triển: 104/104 test đạt, `compileall` đạt và `pip check` đạt.
- Máy in: 104/104 test đạt, `compileall`, `pip check`, parse shell installer và
  `git diff --check` đều đạt.
- Checkout máy sạch sau cập nhật; không sửa source upstream.
- Máy trước canary ở trạng thái standby, chưa home, toolchanger chưa initialize,
  mọi heater target đã được đưa về 0; chưa chạy homing/toolchange/probe.
- Config local đạt `git diff --check`; chưa commit, push hoặc deploy.

### Kích hoạt dịch vụ và điểm dừng trước deploy

- Người vận hành đã tự chạy
  `sudo systemctl enable --now tool-vision.service`; không chia sẻ hoặc lưu mật
  khẩu sudo. Unit sau đó ở trạng thái `enabled`, `active/running`, PID `2210`,
  exit status `0`.
- Health API loopback trả `ok: true`, version `3.4.0-rc1`, chưa configured,
  không có camera/job/transform đang chạy; đây là trạng thái đúng trước khi
  Klipper nạp config canary.
- Máy vẫn standby, không pause, chưa home, toolchanger uninitialized, mọi heater
  target bằng 0; T0-T3 khoảng 27-30 °C, T4 khoảng 34 °C và bed khoảng 25 °C.
- Moonraker đang chạy chưa liệt kê `tool-vision` trong `available_services`;
  updater config mới sẽ được nạp ở lần restart có kiểm soát sau deploy.
- Tiếp tục dừng trước mọi chuyển động cho tới khi commit/push, installer và
  smoke test không chuyển động đều đạt.

### Commit, deploy và smoke test production

- Commit `3b8d2cb` (`config: enable ToolVision PF2 Z-offset canary`) được push
  lên `origin/main`. Hai mục `extras/Config download/config-20260821-172111*`
  không liên quan không được stage hoặc sửa.
- Máy chạy `bash ~/printer_data/config/scripts/update.sh` đúng một lần. Preflight
  ToolVision/KTC/tool_crash đạt và tạo backup tự động:
  `/home/voron/printer_data/config_backups/config-install-20260823-212901/`.
- Năm Git blob production (`printer.cfg`, `moonraker.conf`,
  `calibration-probe.cfg`, `install.sh`, `tool_vision.cfg`) khớp chính xác commit
  đã push.
- Moonraker được restart trước: không warning/failed component, kết nối lại
  Klipper ở trạng thái ready, nhận `tool-vision` trong `available_services` và
  báo service `active/running`.
- Klipper được restart đúng một lần: state `ready`, không warning/failed
  component. Object `tool_vision` được nạp; object `axiscope` không còn được
  nạp; mọi heater target tiếp tục bằng 0.
- Smoke test không chuyển động đạt:
  - `QUERY_ENDSTOPS`: `ToolVision switch:open`.
  - `TOOL_VISION_STATUS`: host online `3.4.0-rc1`, Z method `switch`, Z setup
    ready, camera chưa setup, không last error.
  - Moonraker updater: branch `main`, local/remote cùng
    `v3.3.0-rc1-11-g2b3bf2c6`, checkout sạch và không detached.
- `INITIALIZE_TOOLCHANGER` không tạo chuyển động và đưa KTC về `ready`, nhưng
  cả `tool` lẫn `detected_tool` đều là `null`. Dừng trước homing để người vận
  hành xác nhận carriage thực sự rỗng, T0-T4 ở đúng dock và nút dừng khẩn cấp
  sẵn sàng. Chưa chạy home, pickup, toolchange hoặc probe Z.

## 3. Dọn backup cũ trên CM4

### Phạm vi và kiểm kê

- Người vận hành yêu cầu chỉ giữ vài backup mới nhất trên CM4. Không thay đổi
  backup Git-tracked trong `extras/backups/` của workspace.
- Trước khi xóa đã kiểm kê theo đường dẫn, loại file và dung lượng. Phần backup
  chỉ khoảng 9 MiB; phần lớn 3.3 GiB trong `printer_data` là G-code và không nằm
  trong phạm vi dọn.
- Dry-run xác nhận từng target là thư mục thật, không phải symlink, có realpath
  nằm dưới `/home/voron/printer_data/` và không trùng config production.

### Đã giữ lại

- `/home/voron/printer_data/config_backups/config-install-20260823-212901/`
- `/home/voron/printer_data/config_backups/pre-toolvision-z-canary-20260823-211716/`
- `/home/voron/printer_data/config_backups/config-install-20260823-084215/`

Ba điểm phục hồi còn lại có tổng dung lượng 1.4 MiB. Bản pre-ToolVision được
giữ là bản đã kiểm tra Git bundle và SHA-256; bản `...211658` không hoàn tất
verify không được giữ.

### Đã xóa vĩnh viễn

- 16 thư mục `config.update-backup-*`/`config.backup-*` từ 2026-05 đến
  2026-06 nằm trực tiếp dưới `printer_data`.
- `tool-vision.pre-v3.2.0-20260821-215201/`.
- `config_backups/pre-toolvision-z-canary-20260823-211658/`.
- `config_backups/pre-ktc-ownership-20260823-083950/`.
- `config_backups/config-install-20260822-211338/`.

Tổng cộng xóa đúng 20 thư mục, thu hồi 7,942,144 byte. Không xóa G-code, log,
runtime, config đang chạy hoặc ba backup được giữ. Sau dọn, Moonraker, Klipper
và ToolVision service đều `active`; filesystem còn khoảng 14 GiB trống.

## 4. Phép đo ToolVision Z 150 °C đầu tiên

- Trong lúc kiểm tra sau dọn backup, người vận hành tự home máy và bấm chạy Z
  calibration từ panel ToolVision. Lần gọi trước khi initialize toolchanger đã
  báo lỗi chọn tool; lần chạy sau có KTC `ready`, T0 active/detected và bắt đầu
  gia nhiệt đủ T0-T4 lên 150 °C.
- Theo dõi toàn bộ toolchange/probe trực tiếp: mỗi pickup đều được detection pin
  xác nhận; PF2 đi từ open sang trigger/retract; không pause hoặc last error;
  nhiệt độ giữ quanh 150 °C.
- Kết quả report-only được ghi vào
  `Generated-Data/ToolVision/results.json`:
  - T0 `+0.000 mm`, trigger Z `1.629311 mm`.
  - T1 `+0.098 mm`, trigger Z `1.727311 mm`.
  - T2 `-0.384 mm`, trigger Z `1.245311 mm`.
  - T3 `-0.154 mm`, trigger Z `1.475311 mm`.
  - T4 `+0.078 mm`, trigger Z `1.707311 mm`.
  - T0 return trigger Z `1.657311 mm`; reference drift `+0.028 mm`.
- Sau hoàn tất: ToolVision `busy=false`, no last error, PF2 `open`, KTC
  `ready`, active/detected T0, printer standby tại `[67.5, -8.0, 2.0]`, mọi
  heater target bằng 0. Không áp dụng hoặc sửa production XYZ offsets.
- Đây mới là một phép đo ở 150 °C. Cần chạy lặp lại cùng điều kiện trước khi
  đánh giá độ lặp, đặc biệt vì T3 lệch `-0.100 mm` so với dữ liệu ToolVision cũ
  (`-0.054 mm`).

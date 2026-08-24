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

## 4. Viết lại tài liệu hiện hành theo cặp Anh–Việt

### Phạm vi và nguyên tắc

- Người vận hành yêu cầu cập nhật các file Markdown song ngữ và viết sát tiến
  độ thật sau khi đọc code, không tự suy diễn.
- Đã kiểm kê 64 file Markdown được Git theo dõi trước thay đổi: tài liệu hiện
  hành, journal lịch sử, snapshot backup, snapshot tải từ máy, file retired và
  tài liệu fork Axiscope không còn active.
- Không sửa nội dung journal cũ, snapshot backup hoặc snapshot tải từ máy vì đó
  là bằng chứng bất biến. Ba snapshot rollback Git gần nhất chỉ được dẫn link
  trong chỉ mục mới. Đây là thay đổi chỉ `.md`, không sửa `.cfg`, `.conf` hoặc
  `.sh`, nên không tạo thêm snapshot cấu hình.
- Hai mục untracked `extras/Config download/config-20260821-172111*` tiếp tục
  không được sửa hoặc stage.

## 6. Cài ToolVision RC2 canary và preflight Cartographer Touch

### Mục tiêu

- Đọc lại quy tắc, tài liệu hiện hành của All-Config và handbook bắt buộc của
  repository ToolVision trước khi thay đổi máy.
- Xác định bản mới nhất phù hợp để HIL Cartographer, đối chiếu phép tính Z với
  Cartographer3D đang chạy thật và cài canary mà không áp offset production.

### Baseline và đối chiếu source

- ToolVision production trước update: `main` tại `500dbad`, runtime
  `3.4.0-rc1`; semantic tag gần nhất vẫn là `v3.3.0-rc1`.
- Canary mới nhất đã xác minh trực tiếp trên remote:
  `codex/correctness-safety-evidence` tại `6059149`, runtime `3.4.0-rc2`.
- Cartographer production: package `cartographer3d-plugin 1.9.0`, Touch model
  `default`, firmware Cartographer V3 `6.1.0`.
- Cartographer lấy median của tập touch hợp lệ rồi trả
  `trigger_position - model.z_offset` qua public status
  `cartographer.touch.last_z_result`. ToolVision đọc đúng public command/status
  và tính `raw_contact_z(tool) - raw_contact_z(T0)`. Vì toàn run khóa cùng một
  Touch model và sensor cố định trên shuttle, `model.z_offset` triệt tiêu trong
  phép trừ tương đối.
- RC2 tiếp tục dùng T0 đầu run làm mốc offset, đo lại T0 cuối run chỉ để báo
  signed drift. Nó không cộng correction, không gọi `SAVE_CONFIG` và không sửa
  `gcode_z_offset` production.

### Kiểm tra local trước deploy

- `158/158` unit/component/fake-Klipper test: đạt.
- Python compile, Ruff safety subset và `git diff --check`: đạt.
- Không phát hiện lỗi contract, dấu hoặc phép tính đủ để chặn canary. Các gate
  simulator/HIL còn thiếu vẫn được giữ đúng là rủi ro mở.

### Sao lưu

- Backup trên CM4 đã tạo và xác minh toàn bộ SHA-256:
  [manual-rc2-cartographer-hil-20260824-211500](file:///home/voron/printer_data/config_backups/tool-vision/manual-rc2-cartographer-hil-20260824-211500/).
- Backup chứa `printer.cfg`, `moonraker.conf`, `tool-vision.cfg`,
  `moonraker.asvc`, state/result/migration backup, commit/status runtime và Git
  bundle đã qua `git bundle verify`.
- Bản off-device đã copy và kiểm tra lại từng checksum tại
  [printer-rc2-cartographer-hil-20260824-211500](file:///D:/Desktop/Tool-Vision/.local-backups/printer-rc2-cartographer-hil-20260824-211500/).

### Cài đặt canary qua Moonraker

- Live `moonraker.conf` tạm đổi riêng
  `primary_branch: main` thành
  `primary_branch: codex/correctness-safety-evidence`; source All-Config chưa
  đổi vì đây là canary đang chờ HIL và rollback decision.
- Tạo local canary branch tại chính baseline `500dbad`, đặt upstream remote rồi
  để Moonraker Update Manager fast-forward đúng hai commit lên `6059149`.
- Chỉ gọi upgrade `tool-vision`; không update Klipper, Moonraker, OS hoặc
  component khác. Update Manager restart đúng `tool-vision` và `klipper`.

### Smoke test không chuyển động

- Repository runtime clean, đúng branch/hash `6059149`; host health và Klipper
  object cùng báo `3.4.0-rc2`.
- Klipper, Moonraker và `tool-vision.service` active; Klipper trở lại `ready`,
  printer `standby`, ToolVision `busy=false`, mọi heater target bằng `0`.
- State/result giữ nguyên checksum trước canary:
  - `state.json`: `506273e699fbc9a8d9d539afb7141a1fad643a40d9a94e18660bbdc602d1fdca`.
  - `results.json`: `6f91a57179071ecb8d70d58f8af35701d162df1c4b9bce536b430b7712680466`.
- RC2 báo `z_ready=false`, `switch_ready=false` theo thiết kế vì station schema
  3 cũ không có `reference_offset`. Runtime fail-closed và yêu cầu teach lại,
  không tự đoán snapshot bằng zero.
- Chạy `CALIBRATION_STATUS`, `CHECK_OFFSETS`, `QUERY_ENDSTOPS` và
  `TOOL_VISION_STATUS`; không có home, heat, probe, toolchange hoặc ghi JSON.

### Kết quả và bước còn lại

- Cài đặt canary và smoke test đạt; chưa có bằng chứng lỗi mã cần chuyển sang
  dự án ToolVision.
- HIL đang dừng an toàn trước chuyển động. Sau restart, toolchanger đang
  `uninitialized`; cần người vận hành hiện diện, bàn/đường dock trống và
  emergency stop sẵn sàng trước khi home, chọn T0, teach lại Cartographer và
  chạy Z report-only ở cùng `150 C` để so với baseline ngày 2026-08-23.

### Source đã đọc và sự thật được khóa

- Đọc lại `printer.cfg`, toàn bộ `Printer-Setup/*.cfg`,
  `toolchanger-config.cfg`, T0–T4, `install.sh`, `update.sh`,
  `cleanup-voron.sh`, `moonraker.conf`, `crowsnest.conf` và script đồng bộ
  OrcaSlicer.
- Xác nhận lại include order, quyền sở hữu readonly của KTC-Easy, CAN UUID,
  dock, offset production, giới hạn trục, Cartographer mesh/Touch, trình tự
  `PRINT_START`/`PRINT_END`, prime line, dryer preset, ToolVision PF2 và đường
  dẫn `Generated-Data/ToolVision/`.
- Đọc source, test và tài liệu chuẩn của repository ToolVision độc lập. Nhánh
  `codex/z-calibration-ux` tại `2d936f3` đã cài đặt method Z tường minh,
  `VERBOSITY=QUIET`, metadata `NOT APPLIED` và history 20 record, nhưng tài liệu
  test của chính dự án ghi chưa deploy/HIL production. Runtime máy được ghi
  nhận vẫn là `2b3bf2c6`, vì vậy tài liệu phân biệt rõ hai trạng thái.

### Tài liệu đã cập nhật

- Tạo cặp `README.md` / `README.vi.md` ở root.
- Tạo cặp `config/README.md` / `config/README.vi.md`.
- Tạo cặp `Orca Config/README.md` / `Orca Config/README.vi.md` theo hành vi thật
  của `Sync-OrcaProfiles.ps1` và `.cmd`.
- Viết lại hướng dẫn StealthChanger tiếng Việt và thêm bản tiếng Anh.
- Viết lại cặp hướng dẫn tích hợp ToolVision; phân biệt runtime production và
  feature branch chưa deploy.
- Chuyển đề xuất UX ToolVision thành báo cáo evidence/trạng thái implementation
  và thêm bản tiếng Việt.
- Thêm chỉ mục tài liệu `extras/docs/README.md` / `README.vi.md` để liên kết các
  cặp hiện hành, nội dung retired và ba snapshot gần nhất mà không sửa backup.
- `FORK_INFO.md` Axiscope và README retired được bổ sung song ngữ. README dài
  của fork Axiscope chỉ được thêm banner Anh–Việt báo rõ inactive/rollback,
  không viết lại nội dung upstream lịch sử.

### Kiểm tra

- Bảy cặp tài liệu hiện hành đều tồn tại và liên kết chéo đúng.
- Link local trong toàn bộ tài liệu hiện hành đã sửa đều resolve.
- Quét các tuyên bố cũ không còn thấy “camera XY disabled/inactive”, Axiscope là
  backend active, `PRINT_END` quay về T0 hoặc chỉ giữ đúng một backup.
- Đối chiếu lại các giá trị số với code và sửa range Z thành `-5..347`, prime
  amount thành `13.33 mm` cho mỗi pass đủ 52 mm.
- `git diff --check` đạt. Cảnh báo LF/CRLF của Git trên Windows không phải lỗi
  whitespace.

### English summary

- Rewrote the current owned documentation as seven English/Vietnamese pairs
  after checking the active configuration, scripts and independent ToolVision
  source/tests.
- Preserved historical journals, backup READMEs and downloaded snapshots as
  immutable evidence; the new bilingual index links three recent rollback
  snapshots without editing them.
- Clearly separated the deployed ToolVision canary (`2b3bf2c6`) from the
  implemented but not production-deployed UX branch (`2d936f3`).
- Local-link validation and `git diff --check` passed; no printer motion,
  service restart, deployment or generated-data mutation was required.

## 5. Mở rộng README thành tài liệu tham khảo đầy đủ

### Mục tiêu

- Người vận hành yêu cầu viết lại `README.md` chi tiết để người mới, operator và
  maintainer có thể tra cứu mà không phải tự ghép thông tin từ nhiều file.
- Giữ nguyên chính sách tài liệu song ngữ nên cập nhật đồng thời `README.md` và
  `README.vi.md`.
- Thay đổi chỉ liên quan Markdown; không sửa `.cfg`, `.conf` hoặc `.sh`, vì vậy
  không tạo snapshot cấu hình mới và không có thao tác trên máy in.

### Source đã đối chiếu

- Đọc lại rule project, known issues, decisions và TODO hiện hành.
- Đối chiếu trực tiếp `hardware.cfg`, `fans-leds.cfg`,
  `calibration-probe.cfg`, `input-shaper.cfg`, `nozzle-clean.cfg`,
  `prime-lines.cfg`, `print-macros.cfg`, `tool-crash.cfg`,
  `toolchanger-config.cfg`, T0–T4, `printer.cfg`, `moonraker.conf`,
  `crowsnest.conf`, `install.sh`, `update.sh`, `cleanup-voron.sh` và ba machine
  profile OrcaSlicer.
- Không lấy giá trị từ README cũ làm nguồn nếu có thể đọc trực tiếp từ config
  hoặc code.

### Nội dung mới

- Thêm bảng “Start here” theo nhu cầu người dùng và quy ước Active/Observed/
  Development/Retired.
- Ghi rõ ranh giới ownership KTC-Easy, ToolVision, Cartographer và generated
  data.
- Bổ sung pinout Manta/EBB, CAN UUID, dock, rotation distance, offset production
  và Input Shaper từng tool.
- Bổ sung giới hạn chuyển động, điểm QGL, Cartographer Touch/mesh và include
  order.
- Mô tả đầy đủ hợp đồng Orca `PRINT_START`, thứ tự `PRINT_START`/`PRINT_END`,
  runout/crash recovery và bảng macro có phân loại chuyển động/nhiệt.
- Ghi geometry/parameter cho nozzle cleaning, prime line và toàn bộ preset/
  override dryer.
- Phân biệt ToolVision runtime đang deploy với UX feature branch chưa HIL; giữ
  bảng kết quả Z thực và semantics report-only.
- Thêm quy trình install/update, post-update smoke test không chuyển động,
  backup/rollback/cleanup, troubleshooting, limitation/TODO và documentation
  map.

### Kiểm tra

- `README.md` và `README.vi.md` có cấu trúc tương ứng, lần lượt khoảng 780 và
  760 dòng.
- Mọi link Markdown local trong hai README đều resolve.
- Các giá trị pin, CAN, dock, offset, shaper, QGL, mesh, nhiệt, dryer và macro
  đã được đối chiếu lại với source.
- `git diff --check` đạt; chỉ có cảnh báo line-ending LF/CRLF thông thường trên
  Windows.
- Hai mục untracked `extras/Config download/config-20260821-172111*` tiếp tục
  không được sửa hoặc stage.

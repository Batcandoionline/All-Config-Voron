# Nhật ký — 2026-08-31

## 1. Thay ToolVision bằng kTAMV để đối chiếu phương pháp sử dụng

### Mục tiêu

- Đọc toàn bộ tài liệu Markdown và hệ thống quy tắc `AGENTS.md`/`.agents/`
  trước khi thao tác.
- Gỡ tích hợp ToolVision đang hoạt động, cài kTAMV từ upstream đã review và lập
  tài liệu đối chiếu workflow.
- Giữ nguyên vị trí vật lý của tool đang ở trên camera; không chạy bất kỳ lệnh
  chuyển động nào trong phiên.

### File đã sửa đổi

- `config/printer.cfg` — thay include ToolVision bằng `Printer-Setup/ktamv.cfg`.
- `config/Printer-Setup/ktamv.cfg` — thêm backend kTAMV X/Y có giám sát, camera
  local, server cổng `8086`, cloud tắt và hai macro setup/status không chuyển động.
- `config/Printer-Setup/calibration-probe.cfg` — chuyển trạng thái calibration
  sang kTAMV X/Y; ghi rõ không có backend tool-offset Z active.
- `config/moonraker.conf` — bỏ updater ToolVision; kTAMV pin/thủ công vì có patch
  local đã review.
- `config/scripts/install.sh` — thay preflight ToolVision bằng kiểm tra commit,
  venv, user service, hai symlink và detector patch kTAMV.
- `config/scripts/ktamv/ktamv-server.service` — thêm user unit cổng `8086`.
- `config/scripts/patches/ktamv-multi-object-selection.patch` — sửa đường code
  nhiều keypoint và method binding trong detector upstream.
- `config/toolchanger/toolchanger-config.cfg` — cập nhật ranh giới sở hữu backend.
- `config/Printer-Setup/tool-vision.cfg` — chuyển nguyên byte sang
  `extras/retired-configs/2026-08-31-toolvision-removal/tool-vision.cfg`; không
  còn nằm trong payload active.
- README Anh/Việt, chỉ mục tài liệu và hướng dẫn StealthChanger — đồng bộ trạng
  thái kTAMV hiện hành, giữ tài liệu ToolVision cũ dưới dạng evidence retired.
- `extras/docs/ktamv-usage-comparison.en.md` và `.vi.md` — hướng dẫn sử dụng,
  phân loại lệnh có/không chuyển động và bảng đối chiếu hai phương pháp.
- `.agents/DIRECTORY.md`, `.agents/DECISIONS.md`, `.agents/KNOWN_ISSUES.md` và
  `.agents/CHANGELOG.md` — cập nhật cấu trúc, quyết định và giới hạn đã biết.

### Sao lưu

- [Snapshot repository](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-replace-toolvision-with-ktamv-20260831-113047/)
  — 22 file nguồn trước thay đổi và bản sao quy tắc dự án.
- Snapshot máy thật:
  `/home/voron/printer_data/config_backups/pre-replace-toolvision-with-ktamv-20260831-113047/`
  — config, source tar/Git bundle, generated data, log, system unit, symlink,
  dependency và trạng thái máy; 67 checksum SHA-256 đã đạt.
- Backup tự động lúc deploy:
  `/home/voron/printer_data/config_backups/config-install-20260831-114445/`.

### Nghiên cứu upstream

- Đã đọc đầy đủ checkout [TypQxQ/kTAMV](https://github.com/TypQxQ/kTAMV) tại
  commit `72421f2d54da0de8701c4f84449c6e6b7d060301`; `main`/HEAD upstream vẫn là
  commit ngày 2024-04-02.
- Không chạy installer upstream vì nó đổi giờ hệ thống qua API ngoài, chạy
  `apt` toàn máy, ghi header Moonraker thừa `]`, sửa config active, restart
  Klipper/Moonraker và không idempotent.
- Source xác nhận kTAMV chỉ đo X/Y; camera transform và origin chỉ ở RAM;
  `KTAMV_GET_OFFSET` chỉ báo `raw current - raw origin`; không tự lưu offset.
- `KTAMV_CALIB_CAMERA` di chuyển mười điểm nhỏ và có thể dịch cuối tới tâm;
  `KTAMV_FIND_NOZZLE_CENTER` jog X/Y và có thể wiggle 0,1–0,2 mm. Hai lệnh này
  không được chạy trong phiên.
- Lần thử máy ngày 2026-08-22 chỉ đạt 6/10 sample: vùng phản xạ bị nhận nhầm,
  scale `0.028` lệch cụm `0.041–0.044`, camera 1280×720 bị kéo thành 640×480.
  Đây là giới hạn quang học cần xử lý trước test motion mới.

### Cài đặt và gỡ runtime trên máy thật

- kTAMV được clone thủ công vào `/home/voron/kTAMV`, pin commit `72421f2`, áp
  detector patch và `py_compile` toàn bộ module thành công.
- Tạo `/home/voron/ktamv-env` dùng package OpenCV hệ thống; cài Flask `3.1.3`,
  Waitress `3.0.2`, Jinja2 `3.1.6` và dependency cần thiết.
- Cài đúng hai symlink `ktamv.py`/`ktamv_utl.py`; user service
  `ktamv-server.service` active/enabled nhờ linger, chỉ cổng `8086` lắng nghe.
- Dừng ToolVision qua Moonraker, bỏ `tool-vision` khỏi `moonraker.asvc`, sau khi
  xác minh backup đã xóa chính xác runtime `~/Tool-Vision`, venv
  `~/tool-vision-env`, năm symlink/bytecode Klipper, symlink
  `~/printer_data/tool-vision`, generated data và log active. Port `8085` đóng.
- Sau khi người dùng cho phép sudo SSH, disable/xóa unit root
  `/etc/systemd/system/tool-vision.service`, chạy `systemctl daemon-reload` và
  xác nhận systemd trả `No such file or directory` cho unit cũ.
- Chuyển file sao lưu cũ `moonraker.asvc.pre-tool-vision-20260821-215307` khỏi
  root `printer_data` vào snapshot dated, bổ sung checksum và xác minh lại.
- Không sửa/xóa backup ToolVision lịch sử.

### Kiểm tra

- Đã đọc 97/97 file Markdown, không có read failure.
- `bash -n` đạt cho `config/scripts/install.sh` và `update.sh` trên staging CM4.
- Hash SHA-256 của `printer.cfg`, `ktamv.cfg`, `moonraker.conf` và `install.sh`
  khớp giữa PC, staging và config live.
- Installer chạy thành công, Klipper restart hai lần và Moonraker restart một
  lần bằng service API; không gửi G-code.
- Sau cutover: Klipper ready, `print_stats.state=standby`, không pause, bed
  target `0`, `homed_axes=""`; object `ktamv` đã nạp với
  `is_calibrated=false`, `mm_per_pixels=null`, origin `null`.
- `ktamv-server.service=active`; cổng `8086` mở; ToolVision `inactive`; cổng
  `8085` đóng. Mười một đường dẫn active ToolVision kiểm tra đều không tồn tại.
- Tool trước restart ở tọa độ báo cáo X `170.2`, Y `20`, Z `40`; sau restart
  Klipper xóa trạng thái home nhưng tool vật lý không chuyển khỏi camera.
- Không chạy `KTAMV_SETUP`, preview, detector, home, toolchange, heater,
  calibration hoặc bất kỳ G-code nào.

### Kết quả

kTAMV đã thay ToolVision trong config production và đang chạy như backend đối
chiếu X/Y có người giám sát. Tài liệu mới giải thích rõ cách dùng, sự khác nhau
về trục, persistence, detector, recovery và phạm vi an toàn. Chưa thực hiện phép
đo vì người dùng yêu cầu giữ nguyên vị trí máy và cảnh camera cũ còn mơ hồ.

### Vấn đề còn lại

- Chỉ sau khi sửa ánh sáng/focus/cảnh phản xạ và có người đứng máy mới cân nhắc
  test `KTAMV_CALIB_CAMERA`/`KTAMV_FIND_NOZZLE_CENTER`.

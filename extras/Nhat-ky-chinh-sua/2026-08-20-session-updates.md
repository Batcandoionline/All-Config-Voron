# Nhật ký — 2026-08-20

## 1. Rebuild Tool Vision 2 thành hệ thống đo XYZ độc lập phần cứng

### Mục tiêu
Xóa implementation Tool Vision cũ và xây dựng lại hệ thống đo offset X/Y bằng
camera hướng lên, đo Z bằng microswitch, kế thừa đúng chiều offset và quy trình
từ kTAMV/Axiscope nhưng không cố định độ phân giải hay đường dẫn phần cứng.

### File đã sửa đổi
- `.gitattributes` — ép LF cho source, cấu hình và shell script của Tool Vision.
- `extras/Tool-Vision/.gitignore` — loại cache/test artifact khỏi Git.
- `extras/Tool-Vision/README.md` — viết lại kiến trúc, commissioning và quy tắc an toàn.
- `extras/Tool-Vision/tool_vision.cfg` — cấu hình portable cho camera, detector,
  trạm đo, tốc độ, calibration, probe và workflow hook.
- `extras/Tool-Vision/klippy/extras/tool_vision.py` — viết lại Klipper extension
  điều phối camera, chuyển động an toàn, probe Z và báo cáo XYZ.
- `extras/Tool-Vision/server/` — thay server cũ bằng API versioned, camera I/O
  native-resolution, detector ổn định nhiều frame và affine/quadratic transform.
- `extras/Tool-Vision/install.sh` — viết lại installer tự nhận user/home/path.
- `extras/Tool-Vision/uninstall.sh` — thêm gỡ cài đặt có guard cho virtualenv.
- `extras/Tool-Vision/tests/` — thêm test deterministic cho API, camera/detector,
  transform, dấu offset và thứ tự chuyển động.
- Xóa `server/vision_io.py`, `server/vision_dm.py`, `server/vision_server.py` và
  `server/tool_vision.service` của implementation cũ.

### Sao lưu
- [Tool Vision trước rebuild](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-tool-vision-rebuild-20260820-154154/)

### Chi tiết thay đổi
- Loại bỏ toàn bộ hằng số/resize `640x480`; detector đọc kích thước thật từ
  `frame.shape`, còn target, ROI và blob area được cấu hình bằng tỉ lệ.
- Hỗ trợ HTTP JPEG/MJPEG, RTSP/OpenCV, `/dev/video*` và camera index; width,
  height, FPS bằng `0` để camera tự chọn native/default mode.
- Fit phép biến đổi `machine_delta = transform(pixel_delta)` và buộc recalibrate
  khi độ phân giải camera thay đổi.
- Giữ chiều XY `raw_current - raw_reference` của kTAMV và chiều Z
  `trigger_current - trigger_reference` của Axiscope.
- Luôn nâng Z tới safe height trước khi chạy XY sang camera hoặc microswitch.
- Từ chối safe Z thấp hơn measurement/approach Z và từ chối danh sách tool
  rỗng, âm hoặc trùng lặp ngay khi Klipper đọc cấu hình.
- Chặn chạy khi máy đang print/paused, chặn nhiều job camera đồng thời và chặn
  đổi cấu hình camera giữa lúc một job detection đang chạy.
- Chỉ ghi kết quả atomically vào `tool_vision_results.json`; không tự sửa
  production offset, không gọi `SAVE_CONFIG` hoặc `SAVE_TOOL_PARAMETER`.
- Tọa độ camera mẫu được để comment vì chưa có số đo phần cứng thật. Production
  `[axiscope]` và các file config đang chạy không bị sửa hoặc include Tool Vision.

### Lý do
Implementation cũ chứa giả định 640x480, đường dẫn service/user cố định, quy
trình station chưa đủ an toàn và khả năng ghi trực tiếp offset. Thiết kế mới cần
dùng được trên các máy khác chỉ bằng thay đổi `.cfg`, đồng thời giữ kết quả đo ở
chế độ report-only cho đến khi được kiểm chứng bằng phần cứng và first-layer test.

### Kiểm tra
- Xác minh 7/7 file implementation cũ trong backup khớp Git blob trước rebuild: đạt.
- Python unit/integration tests: `22/22` đạt.
- Native-resolution detector: đạt với `1280x720`, `800x600` và rotation 90 độ.
- Kiểm tra dấu XY/Z theo kTAMV/Axiscope: đạt.
- Kiểm tra safe-Z-before-XY và guard thiếu tọa độ camera: đạt.
- Parse `tool_vision.cfg` strict, một section và không trùng option: đạt.
- Python compile và Ruff `E,F`: đạt.
- Shell parse cho `install.sh` và `uninstall.sh`: đạt.
- Render service template với project/log path chứa khoảng trắng: đạt.
- `git diff --check`: đạt.
- Khởi động lại Klipper/thử phần cứng/thử in: chưa thực hiện vì Tool Vision chưa
  được deploy/include và tọa độ camera thật chưa được cung cấp.

### Kết quả
Hoàn thành codebase Tool Vision 2 độc lập phần cứng ở mức host-side, có cấu hình
camera native-resolution, đo XYZ report-only, tài liệu commissioning và bộ test
logic. Cấu hình production hiện hành được giữ nguyên an toàn.

### Vấn đề còn lại
- Đo và điền `camera_x_pos`, `camera_y_pos`, `camera_z_pos`, `camera_safe_z` thật.
- Cài service trên Klipper host, xác nhận stream camera và switch pin thực tế.
- Chỉ disable `[axiscope]` rồi include `[tool_vision]` khi bắt đầu commissioning.
- Chạy tuần tự T0, một tool phụ, sau đó mới chạy toàn bộ tool và đối chiếu với
  first-layer print trước khi áp dụng bất kỳ offset nào.

## 2. Clone tool_crash của cekim-git làm nguồn tham khảo

### Mục tiêu
Đưa nguyên bản dự án crash detection của cekim-git vào `extras/` để có thể đọc,
đối chiếu thiết kế sensor/watchdog với hệ thống toolchanger hiện tại.

### File đã sửa đổi
- `.gitmodules` — khai báo URL để Git có thể tái tạo nguồn tham khảo.
- `extras/tool_crash/` — clone nguyên repository upstream dưới dạng Git
  submodule; không sửa source của tác giả.

### Sao lưu
- Không cần sao lưu vì đây là thư mục mới, không ghi đè file hiện có.

### Chi tiết thay đổi
- Nguồn: `https://github.com/cekim-git/tool_crash.git`.
- Nhánh: `main`.
- Upstream commit được ghim: `5cb00ad9e0216db97b8139a627b41407c86c88a9`.
- Nội dung chính gồm `tool_crash.py`, `README.md` và `LICENSE`.
- Không copy extension vào Klipper, không thêm `[tool_crash]` vào production và
  không chạy bất kỳ mã upstream nào.

### Lý do
Dự án triển khai crash detection cho `klipper-toolchanger` bằng cạnh tín hiệu
probe/detection pin kết hợp watchdog kiểm tra trạng thái active tool. Đây là
nguồn tham khảo phù hợp cho phần an toàn toolchanger, nhưng upstream tự đánh dấu
là alpha nên chưa được phép dùng trực tiếp trên máy.

### Kiểm tra
- Xác nhận remote origin, nhánh và commit upstream: đạt.
- `git fsck --no-reflogs` trong repository clone: đạt.
- Working tree upstream sạch: đạt.
- Parse AST `tool_crash.py`: đạt.
- Klipper runtime/hardware test: không thực hiện vì chỉ clone làm tham khảo.

### Kết quả
Repository upstream đã có tại `extras/tool_crash` dưới dạng submodule, giữ
nguyên lịch sử Git để đọc, so sánh hoặc cập nhật độc lập khi cần.

### Vấn đề còn lại
- Cần review chi tiết tính tương thích với phiên bản `klipper-toolchanger` đang
  dùng trước khi kế thừa bất kỳ logic nào.
- Không enable `[tool_crash]` trên production khi chưa audit và thử nghiệm an toàn.

## 3. Chuyển tool_crash từ Klipper shutdown sang pause an toàn

### Mục tiêu
Audit cấu hình `tool_crash` đang chạy trên Voron 5 Tool và máy thật
`192.168.1.43`; nếu crash đang gây emergency/shutdown thì đổi sang trạng thái
pause có thể sửa tool, cứu bản in hoặc cancel.

### File đã sửa đổi
- `config/Printer-Setup/tool_crash_cartographer.cfg` — bật custom crash handler,
  thêm macro pause không park XYZ và sửa giải thích `ignore_events`.
- `config/Printer-Setup/crash_detection_override.cfg` — sửa hướng dẫn vô hiệu
  detection; upstream `ignore_events: all` không vô hiệu mọi sự kiện.
- `extras/backups/pre-tool-crash-safe-pause-20260820-170905/` — bản sao hai file
  cấu hình trước thay đổi và hướng dẫn restore.

### Sao lưu
- Local: `extras/backups/pre-tool-crash-safe-pause-20260820-170905/`.
- Máy in: `config/.codex-backups/pre-tool-crash-safe-pause-20260820-170905/`.
- SHA256 bản gốc `tool_crash_cartographer.cfg`:
  `9492AC393D3F176CD0F5E954A3FA762A3AA70C526C5ADC6D84A91BECC3B69344`.
- SHA256 bản gốc `crash_detection_override.cfg`:
  `7E59E00AE0F72EE189C33CE1CBC973F8D7A0B48D064FF5EFF0213899E51D3E66`.

### Audit logic
- Cấu hình cũ không khai báo `crash_gcode`. Source upstream gọi
  `printer.invoke_shutdown(msg)`, vì vậy Klipper vào shutdown, không thể Resume
  và cần `FIRMWARE_RESTART` sau khi xử lý nguyên nhân.
- Năm tool T0-T4 đều có detection pin đúng dạng `^!EBBn:PB6`.
- `PRINT_START` dừng detection trước G28/QGL/mesh/prime và bật lại sau prime.
- `dropoff_gcode` dừng detection trước đường docking; `after_change_gcode` chỉ
  bật lại khi `_PRINT_STATE == "printing"`.
- `PRINT_END` và cancel cleanup dừng detection trước các chuyển động dọn dẹp.
- Wrapper START/STOP ưu tiên plugin mới và giữ fallback cũ khi `[tool_crash]`
  không tồn tại.
- Upstream tự đánh dấu alpha và cảnh báo custom crash gcode có thể chờ sau motion
  đã nằm trong hàng đợi. Pause không nhanh bằng hard shutdown trong mọi tình huống.

### Thay đổi hành vi
- `crash_gcode` gọi `_TOOL_CRASH_SAFE_PAUSE`; `crash_mintime` giảm từ mặc định
  0.5 giây xuống 0.1 giây để giảm fixed callback latency.
- Khi đang in virtual SD: lưu target nhiệt cho RESUME, gọi `PAUSE_BASE`, đổi LED
  sang pause, retract E theo Mainsail và hiện cảnh báo.
- Không gọi macro PAUSE thông thường vì macro đó tự nâng Z và park XY; tool đã
  rơi/lệch có thể khiến chuyển động phục hồi làm hỏng thêm đầu in hoặc bàn.
- Crash handler không phát lệnh X/Y/Z, không tắt heater và không shutdown.
- Khi đã pause hoặc không có bản in active: chỉ cảnh báo, không tạo thêm chuyển
  động hay shutdown.

### Deploy và kiểm tra máy thật
- Trước sửa: Klipper `ready`, máy `standby`, `is_paused=False`, active tool `-1`.
- Xác nhận live plugin có các lệnh `START_TOOL_CRASH_DETECTION` và
  `STOP_TOOL_CRASH_DETECTION`; `[tool_crash]` được parse với watchdog 0.5 giây,
  threshold 2 và `ignore_events: probing`.
- Upload hai file qua Moonraker với SHA256 checksum khớp local.
- Chỉ gọi Klipper `RESTART` khi máy standby; restart hoàn tất với trạng thái
  `ready` và thông báo `Printer is ready`.
- Xác nhận live `_TOOL_CRASH_SAFE_PAUSE` đã được nạp, `crash_gcode` trỏ đúng
  macro, `crash_mintime=0.1`, năm pin T0-T4 đúng và START/STOP wrapper đúng.
- Không có `Config error`, parse error, unknown command hoặc `crash gcode failed`
  trong log sau restart.
- Không cố ý tháo tool/kích detection pin để tạo crash thật vì thử nghiệm đó có
  nguy cơ cơ khí; cần xác nhận lần đầu bằng test có giám sát và khoảng trống an toàn.

### Kết quả
Production không còn dùng hard shutdown mặc định của tool_crash. Khi crash được
phát hiện trong lúc in, hệ thống chuyển sang pause có thể Resume/Cancel và tránh
mọi chuyển động park XYZ tự động sau sự cố.

### Vấn đề còn lại
- Custom pause chỉ được thực thi khi đến lượt trong hàng đợi G-code; motion đã
  buffer trước đó có thể vẫn hoàn tất. Đây là giới hạn upstream, không phải cam
  kết dừng tức thì như `invoke_shutdown`/M112.
- Trước khi RESUME, người vận hành phải xác nhận tool được gắn chắc, dây/canbus
  còn nguyên, vị trí cơ khí đúng và nozzle không mắc vào chi tiết in.
- Nên chạy một test giám sát ở tốc độ thấp, toolhead cách xa bàn/chi tiết, rồi
  kiểm tra trạng thái `paused` và quy trình RESUME/CANCEL trước khi tin cậy hoàn toàn.

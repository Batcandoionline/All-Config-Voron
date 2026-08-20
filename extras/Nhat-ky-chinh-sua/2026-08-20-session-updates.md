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

## 4. Audit tương thích và cập nhật software máy in

### Mục tiêu
Đối chiếu các phiên bản được Mainsail Update Manager đề xuất với cấu hình Voron
5 Tool, xử lý trước breaking change có thể ảnh hưởng startup rồi cập nhật máy
thật `192.168.1.43` trong trạng thái an toàn.

### Audit trước cập nhật
- Máy `standby`, không pause, không có active tool và toàn bộ heater target bằng 0.
- Klipper từ `v0.13.0-700` lên `v0.13.0-740`; 40 commit mới không đổi chữ ký
  `reactor.register_callback`, `register_timer` hoặc `unregister_timer` mà
  `tool_crash.py` đang sử dụng.
- KTC-Easy từ `v0.0.0-252` lên `v0.0.0-258`; thay đổi Python chủ yếu cập nhật
  `tool_probe` theo probe API mới và cải thiện output `tools_calibrate`.
- KTC-Easy v258 xóa `_ADJUST_Z_HOME_FOR_TOOL_OFFSET` và
  `TOOL_BED_MESH_CALIBRATE` khỏi readonly `homing.cfg` vì logic offset cũ bị áp
  hai lần. Máy này dùng Cartographer cố định và không khai báo
  `[tool_probe_endstop]`, nên không cần phép hiệu chỉnh đó.
- Cấu hình user trước đây chỉ khai báo `description` cho
  `TOOL_BED_MESH_CALIBRATE` và phụ thuộc vào phần `gcode` readonly. Nếu readonly
  mới được áp dụng nguyên trạng, macro user có thể thiếu option `gcode`.
- Mainsail `v2.18.1`/`v2.18.2` chỉ có các bugfix giao diện, file download,
  webcam, console sanitization và frontend loader; không thay `mainsail.cfg`.
- KlipperScreen update là các sửa lỗi UI/network/mesh/reconnect, dependency và
  localization; không thay Klipper config hoặc toolchanger API.

### File đã sửa đổi
- `config/toolchanger/toolchanger-config.cfg` — biến
  `TOOL_BED_MESH_CALIBRATE` thành wrapper độc lập gọi
  `BED_MESH_CALIBRATE {rawparams}` cho Cartographer cố định.
- `extras/backups/pre-software-update-20260820-172054/` — snapshot cấu hình user,
  readonly KTC và tool_crash trước cập nhật.

### Sao lưu
- Local: `extras/backups/pre-software-update-20260820-172054/`.
- Máy in:
  `config/.codex-backups/pre-software-update-20260820-172054/`.
- Wrapper tương thích được upload với SHA256
  `614EFE1FDD8CE023E209BB454D3619A21DACF3C1AD3C8238190ED19F6CE36AA2`.
- Đã RESTART và xác nhận wrapper cùng safe tool-crash load được trên Klipper cũ
  trước khi bắt đầu software update.

### Cách cập nhật
- Dùng Moonraker full-upgrade thay vì update Klipper/KTC riêng lẻ. Trong full
  update, service restart do KTC yêu cầu được hoãn; KTC được update trước,
  Klipper update sau và service Klipper chỉ restart khi cả hai repo đã đổi xong.
- Refresh phát hiện thêm 78 OS packages gồm kernel, Python 3.11, nginx, curl,
  Mesa và security/runtime packages. Package manager được để chạy hoàn tất,
  không ngắt giữa chừng.
- Sau update, package count về 0. Host được reboot khi máy standby, active tool
  `-1` và sáu heater target đều bằng 0 để kích hoạt kernel mới.

### Phiên bản sau cập nhật
- Klipper: `v0.13.0-740`, commit
  `60fc7aa67a8da9abb43a2bad825d4992294ebf3f`.
- klipper-toolchanger-easy: `v0.0.0-258`, commit
  `e881fe40949a3999b0d63f59c22df589474eae9b`.
- KlipperScreen: `v0.4.7-157`.
- Mainsail: `v2.18.2`.
- Linux kernel: `6.12.87+rpt-rpi-v8` -> `6.12.96+rpt-rpi-v8` sau reboot.

### Kiểm tra sau reboot
- Klipper, Moonraker, KlipperScreen và Axiscope: `active/running`.
- Klipper: `ready`; print: `standby`; pause: `False`; active tool: `-1`.
- CAN interface: 1,000,000 bit/s, tx queue 128.
- Đủ object main MCU, EBB0, EBB1, EBB2, EBB3, EBB4 và Cartographer MCU.
- Cartographer, toolchanger và Axiscope object đều load.
- Các lệnh `INITIALIZE_TOOLCHANGER`, `CARTOGRAPHER_TOUCH`, `MOVE_TO_ZSWITCH`,
  `PROBE_ZSWITCH`, `CALIBRATE_ALL_Z_OFFSETS`, START/STOP tool_crash,
  `_TOOL_CRASH_SAFE_PAUSE` và `TOOL_BED_MESH_CALIBRATE` đều tồn tại.
- Live `[tool_crash]` vẫn trỏ tới `_TOOL_CRASH_SAFE_PAUSE`,
  `crash_mintime=0.1`; wrapper bed mesh parse thành
  `BED_MESH_CALIBRATE {rawparams}`.
- Không có config warning, không có SAVE_CONFIG pending, system package count 0.
- Không tìm thấy traceback, config error, MCU communication error, unknown
  command hoặc update error trong log của phiên boot mới.
- Không chạy G28, toolchange, probe hoặc bed mesh tự động trong lượt kiểm tra này
  để tránh tạo chuyển động cơ khí ngoài yêu cầu.

### Trạng thái readonly KTC
- Repo KTC đã cập nhật; Klipper tiếp tục nạp các Python extension KTC từ
  `klippy/extras` và không báo import/config error.
- Live `toolchanger/readonly-configs/homing.cfg` vẫn có SHA256
  `BDC3351AF750F3A9CE99A9D2DCBEFB518D4963D5E6B1401497D3FC9E403E3C6B`, là
  snapshot cũ và không khớp file v258
  `4DEB257CF25ED85CAB1F39E08048E039B5F1707A5BCC94167F77946A2B01201E`.
- Không sửa trực tiếp vùng readonly theo quy tắc dự án. Snapshot cũ hiện không
  ảnh hưởng startup/homing vì `[tool_probe_endstop]` không tồn tại; wrapper user
  mới cũng override an toàn macro bed mesh cũ.

### Kết quả
Software và OS đã được cập nhật hoàn tất, breaking change duy nhất liên quan
cấu hình đã được tách khỏi readonly bằng wrapper Cartographer. Máy trở lại trạng
thái `ready/standby`, các extension tùy chỉnh và toàn bộ CAN MCU vẫn hoạt động.

### Vấn đề còn lại
- Các file readonly trên máy không tự đổi theo repo KTC. Khi có SSH hợp lệ, nên
  audit lại link do `install.sh` tạo và tái lập symlink bằng installer chính thức
  trong một phiên bảo trì riêng; không copy/chỉnh tay readonly production.
- Klipper Update Manager tiếp tục báo anomaly về các untracked custom extension
  (`axiscope.py`, `tool_crash.py`, KTC files, v.v.). Đây không phải dirty tracked
  changes và update vẫn bảo toàn chúng, nhưng cần giữ backup trước mỗi lần update.
- Cần test cơ khí có giám sát: G28, lấy/trả một tool, Cartographer touch và một
  bed mesh nhỏ trước bản in sản xuất tiếp theo.

## 5. Tách Tool Vision thành repository độc lập

### Mục tiêu
Di chuyển implementation Tool Vision 2 ra khỏi repository cấu hình Voron, đặt
repository phát triển độc lập trên PC, giữ Axiscope và kTAMV chỉ làm nguồn tham
khảo, đồng thời chuẩn bị luồng cài đặt không cần clone Git trên Raspberry Pi.

### Repository độc lập
- Local PC: `D:\Desktop\Tool-Vision`.
- GitHub: `https://github.com/IDcrazy123/Tool-Vision`.
- Commit khởi tạo: `edee31e` (`Initial independent Tool Vision release`).
- Commit installer no-clone: `634e8ae` (`Persist printer runtime without cloning`).
- Axiscope là submodule tham khảo, ghim tại
  `9a1a9efe3cfa6dc1e816acaaea87f8ac513282f6`.
- kTAMV là submodule tham khảo, ghim tại
  `72421f2d54da0de8701c4f84449c6e6b7d060301`.
- Hai submodule chỉ tồn tại trên PC/GitHub và không thuộc runtime máy in.

### Luồng cài đặt trên Pi
- `install.sh` không gọi `git clone`.
- Khi chạy standalone, script tải source archive tạm thời từ GitHub, kiểm tra đủ
  file bắt buộc, rồi lưu runtime tối thiểu vào
  `~/printer_data/tool-vision`.
- Runtime chỉ gồm Klipper extension, host service, requirements, installer,
  uninstaller và mẫu cấu hình; không copy test, tài liệu, Axiscope, kTAMV hoặc
  metadata Git.
- Klipper symlink và systemd service trỏ tới runtime đã lưu trên Pi, không phụ
  thuộc thư mục tải tạm.
- Cấu hình hiện có được bảo toàn; installer không tự sửa `printer.cfg`.

### Máy thật `192.168.1.43`
- Mainsail Config chỉ còn
  `config/Tool-Vision/tool_vision.cfg` (5,722 bytes).
- Đã xóa snapshot Axiscope, kTAMV, `.gitmodules`, source backend, test và tài
  liệu khỏi thư mục hiển thị trên máy in.
- Chưa chạy installer, chưa tạo service/symlink, chưa include `[tool_vision]` và
  không restart Klipper vì tọa độ camera/switch chưa được commissioning.
- Không có config đang hoạt động tham chiếu `Tool-Vision`; máy vẫn `ready` sau
  khi thu gọn thư mục.

### Tách khỏi dự án Voron gốc
- Đã xóa implementation được track tại `extras/Tool-Vision/` sau khi xác nhận
  cả bản PC và GitHub độc lập tồn tại.
- Đã xóa `.gitattributes` cũ vì file chỉ áp dụng cho đường dẫn Tool Vision đã
  di chuyển.
- Bổ sung ignore chung cho `__pycache__/` và `*.py[cod]`.
- Các snapshot trong `extras/backups/` được giữ lại theo chính sách backup và
  chỉ có giá trị lịch sử, không phải source đang hoạt động.

### Kiểm tra
- Unit tests repository mới: 23/23 đạt.
- Python compileall, Bash syntax và `git diff --check`: đạt.
- GitHub raw installer khớp SHA256 với local; archive có đủ runtime bắt buộc và
  không chứa entry Axiscope/kTAMV.
- GitHub `main` trỏ đúng commit `634e8ae`.
- Không có thao tác G-code, chuyển động, heater, toolchange hoặc probing trong
  quá trình tách repository.

### Sao lưu
Không ghi đè target cũ: repository GitHub ban đầu trống, thư mục Desktop mới và
thư mục `config/Tool-Vision` trên máy in đều chưa tồn tại. Trước khi xóa bản
trùng trong dự án gốc, source đã tồn tại ở cả PC độc lập và GitHub; lịch sử Git
của dự án gốc cùng các snapshot backup vẫn cho phép phục hồi.

### Kết quả
Tool Vision hiện có một nguồn chính thức độc lập trên PC/GitHub. Máy in chỉ hiển
thị file cấu hình cần chỉnh; runtime sau này sẽ được installer tự lưu trực tiếp
trên Pi mà không cần clone repository.

## 6. Đồng bộ All-Config-Voron với máy thật

### Mục tiêu
Đối chiếu payload `config/` trên PC với `~/printer_data/config` tại máy
`192.168.1.43`, đồng bộ mọi khác biệt production và bảo đảm quá trình update sau
này không xóa dữ liệu chỉ thuộc máy in.

### Audit ban đầu
- Repository PC sạch tại commit `51e9689`.
- Local `config/`: 33 file; trong đó `README.md` là tài liệu và được deployment
  scripts loại khỏi payload.
- Máy thật: 44 file trước backup mới; 32 file managed, 10 file trong
  `.codex-backups/`, một `.moonraker.conf.bkp` do Moonraker sinh và một
  `Tool-Vision/tool_vision.cfg` thuộc dự án độc lập.
- 32/32 file managed khớp SHA256 tuyệt đối giữa PC và máy thật; không có khác
  biệt nội dung hoặc line ending.

### Vấn đề phát hiện
`config/scripts/install.sh` và `config/scripts/update.sh` dùng đồng thời
`rsync --delete --delete-excluded`. Nếu chạy lại, cơ chế này có thể xóa các vùng
máy-local không có trong payload All-Config, bao gồm backup và Tool Vision.

### Sao lưu
- Local:
  `extras/backups/pre-config-sync-20260820-181021/`.
- Máy thật:
  `config/.codex-backups/pre-config-sync-20260820-181021/config/scripts/`.
- SHA256 bản cũ `install.sh`:
  `ECDB2F955CCB2643AFACEC887B91858AAB3DE5205C5E1C339C50A48D5AD01269`.
- SHA256 bản cũ `update.sh`:
  `C13E9F8BF0D152A2B16FD771F957427A7B5445F70BD85C6E39E7DCBAB86355D4`.

### Thay đổi
- Bỏ `--delete-excluded` nhưng giữ `--delete` để stale managed files vẫn được
  loại bỏ.
- Thêm exclude được bảo vệ cho `.codex-backups/`, `.moonraker.conf.bkp` và
  `Tool-Vision/`.
- Giữ nguyên exclude tài liệu `README.md`, `*.md` và
  `Nhat-ky-chinh-sua/`.
- Upload đúng hai script đã sửa lên `config/scripts/`; không sửa config Klipper
  đang parse và không restart service.
- SHA256 mới `install.sh`:
  `A44A06EEB4394BABD436DBC5719BC977E8B49FCB542B664E97F183487AA9954A`.
- SHA256 mới `update.sh`:
  `7C4D46690DBDF5696215314E45C76150C09153DFAFCD460F95CF9DCAADCDE29E`.

### Kiểm tra
- Bash syntax của cả hai script: đạt.
- Contract check: không còn `--delete-excluded`, đủ ba exclude máy-local.
- Sau upload, 32/32 file managed khớp SHA256; mismatch = 0.
- Backup mới, `.moonraker.conf.bkp` và Tool Vision đều còn tồn tại.
- Klipper `ready`, print `standby`, pause `False`, `SAVE_CONFIG` pending `False`.
- Không chạy G-code, không restart, không tạo chuyển động hoặc gia nhiệt.

### Kết quả
Payload All-Config-Voron trên PC và máy thật hiện thống nhất hoàn toàn. Các file
generated, backup và Tool Vision được phân loại là dữ liệu máy-local có chủ đích
và đã được deployment scripts bảo vệ cho các lần đồng bộ sau.

## 7. Tái cấu trúc cấu hình 5 tool và chuẩn bị tích hợp Tool Vision

### Mục tiêu
Đọc lại toàn bộ tài liệu dự án, đối chiếu cấu hình máy thật và nguồn chính thức,
rút gọn các lớp cấu hình user-owned, giữ nguyên tuyệt đối dữ liệu phần cứng, và
lập luồng thay Axiscope bằng Tool Vision phù hợp camera tháo lắp bằng gá nam châm.

### Sao lưu trước thay đổi
- Local:
  `extras/backups/pre-five-tool-rewrite-20260820-181903/`.
- Bản local gồm cấu hình PC, cấu hình live tải từ Moonraker và source Tool Vision.
- Máy thật:
  `config/.codex-backups/pre-five-tool-rewrite-20260820-181903/config/`.
- Đã xác minh 34/34 file live trong backup máy thật khớp SHA256 với bản tải về.
- Root `.gitattributes` lưu `extras/backups/**` byte-for-byte, không normalize
  line ending hoặc báo lỗi whitespace của snapshot lịch sử.
- Tổng cộng 127 file Markdown trong workspace đã được đọc trước khi tái cấu trúc.

### Đối chiếu nguồn chính thức
- Klipper Config Reference: xác nhận bed mesh dùng tọa độ probe tương đối và
  Klipper không có `sensor_type: DHT22` native.
- KTC-Easy: máy đang dùng đúng commit mới nhất
  `e881fe40949a3999b0d63f59c22df589474eae9b` (v0.0.0-258).
- Cartographer: cấu trúc Touch/Scan hiện tại phù hợp probe cố định trên shuttle.
- crowsnest: MF-500 đang stream 1280x720/30 MJPEG đúng mode camera hỗ trợ.
- Axiscope/kTAMV: giữ đúng chiều delta XYZ và ràng buộc chỉ một backend dùng
  `probe_multi_axis`.
- tool_crash: xác nhận cần `crash_gcode` tùy chỉnh để tránh shutdown mặc định.

### Vấn đề quan trọng phát hiện
Repo KTC trên Pi đã cập nhật nhưng `toolchanger/readonly-configs` vẫn là file
copy cũ, không phải symlink mới do installer quản lý. Script All-Config trước đây
có thể tiếp tục ghi đè vùng này. `homing.cfg` cũ gọi
`_ADJUST_Z_HOME_FOR_TOOL_OFFSET` và truy cập `tool_probe_endstop` không tồn tại
khi homing Z với tool đang active.

### Thay đổi cấu hình
- `install.sh` và `update.sh` loại trừ toàn bộ
  `toolchanger/readonly-configs/` và cảnh báo nếu file KTC không phải symlink.
- Thêm no-op user-owned `_ADJUST_Z_HOME_FOR_TOOL_OFFSET` cho tới khi chạy lại
  official KTC installer; không sửa trực tiếp readonly.
- Rút gọn `calibration.cfg`, giữ Axiscope active, chặn ba macro SexBolt cũ truy
  cập object không tồn tại, và thêm `CALIBRATION_STATUS`/`CHECK_OFFSETS` đủ XYZ.
- Loại các section extruder rỗng trùng lặp và ví dụ DHT22 không được Klipper hỗ
  trợ khỏi `hardware.cfg`; giữ nguyên mọi pin, MCU và thông số nhiệt.
- Làm rõ `crash_detection_override.cfg` vẫn cần để route macro KTC sang
  `tool_crash`; file detector tiếp tục pause an toàn, không XYZ park/shutdown.
- Thêm Tool Vision include ở trạng thái comment; chưa chuyển backend production.
- Viết lại README/config guide ngắn gọn, thêm hardware preservation contract và
  kế hoạch tích hợp/rollback Tool Vision theo từng pha.
- Bỏ hai gitlink hỏng `extras/Axiscope-reference` và `extras/kTAMV` khỏi
  All-Config sau khi xác minh bản ghim tương ứng đã có trong repository Tool
  Vision độc lập; thư mục legacy trên ổ đĩa được giữ nguyên và ignore. Submodule
  `extras/tool_crash` vẫn hợp lệ.

### Camera và tọa độ station
- Chỉ có một MF-500. Bình thường camera soi buồng in.
- Khi cần hiệu chuẩn, người dùng đặt camera lên gá nam châm có định vị trên bàn,
  kiểm tra không rung/lắc và ảnh hướng lên.
- Người dùng tự jog T0, xác định camera X/Y/Z/safe-Z và nhập vào `.cfg`.
- Vị trí switch/pin cũng được người dùng đo thủ công và nhập `.cfg`; máy hiện tại
  giữ nguyên `^PF2`, X=68, Y=-10, Z=7.
- Không suy đoán tọa độ từ ảnh, không copy tọa độ giữa các máy.

### Tool Vision độc lập
- Nâng lên phiên bản 2.2.0, commit GitHub
  `16ff1b26033468d3b27963fa13e3d9dbaff62e48`.
- Camera/switch example station đều để comment, buộc người dùng đo trên phần cứng.
- Thêm `TV_PREFLIGHT`, `TV_ARM`, `TV_DISARM` và `require_manual_arm: true`.
- Mỗi lần arm camera tháo lắp sẽ xóa transform cũ, buộc chạy lại
  `TV_CALIBRATE_CAMERA`; lệnh station move bị khóa nếu chưa arm.
- Detector tự thu nhỏ adaptive threshold block cho ROI nhỏ và tiếp tục dùng frame
  native, không có `cv2.resize`/hằng số 640x480.
- Installer hỗ trợ `--no-restart` để stage runtime trước cutover.
- Unit/integration tests: 28/28 đạt; Python compile, Bash parse và diff check đạt.

### Đồng bộ và kiểm tra máy thật
- Trước deploy: Klipper `ready`, print `standby`, pause `false`, active tool `-1`,
  bed và 5 hotend target đều 0.
- Upload 15 file user-owned qua Moonraker; 15/15 SHA256 khớp bản PC.
- Chỉ gọi Klipper RESTART để parse; không home, heat, toolchange hoặc probe.
- Sau restart: `ready`, đủ T0-T4, Axiscope active, Tool Vision và tools_calibrate
  không active, không có `tool_probe_endstop`.
- Xác nhận lệnh START/STOP tool_crash, safe-pause, Axiscope Z và hai macro status
  đều tồn tại; `crash_gcode=_TOOL_CRASH_SAFE_PAUSE`, `crash_mintime=0.1`.
- Chạy hai macro chỉ đọc. `CHECK_OFFSETS` trả đúng:
  T0 `0/0/0`, T1 `-0.243/-0.252/+0.228`,
  T2 `+0.746/+0.086/-0.295`, T3 `+0.304/+0.449/-0.268`,
  T4 `+0.041/+0.352/-0.014`.

### Việc còn lại cần giám sát vật lý
- Chạy lại `bash ~/klipper-toolchanger-easy/install.sh` khi có SSH hợp lệ để
  khôi phục readonly symlink; user compatibility guard đang bảo vệ tạm thời.
- Chưa chạy G28, pickup/dropoff, Cartographer Touch/QGL hoặc test in cơ khí trong
  lượt này.
- Chưa cài/enable Tool Vision service vì camera đang ở vị trí soi buồng và chưa
  có tọa độ camera station do người dùng đo.
- Khi commissioning: đo station, stage installer `--no-restart`, chuyển đúng một
  backend, chạy T0 lặp lại, một tool phụ, đủ 5 tool, sau đó first-layer validation.

## 8. Viết lại toàn bộ cấu hình production và đồng bộ máy thật

### Phạm vi
- Rà soát toàn bộ 33 file trong `config/`, bao gồm đồ thị include và các file
  KTC readonly.
- Viết lại 24 file được triển khai lên Pi và tài liệu quản trị; không sửa 6 file
  KTC installer-owned trong `toolchanger/readonly-configs/`.
- Giữ nguyên dữ liệu phần cứng, tọa độ, PID, Cartographer model và XYZ offset.

### Sao lưu trước thay đổi
- Backup kép:
  `extras/backups/pre-full-config-rewrite-20260820-191536/`.
- Bản backup gồm `pc-config/` 33 file, `live-config/` 34 file và README mô tả;
  tổng 68 file. Hash PC 33/33 và live 34/34 đã được xác minh trước khi sửa.
- Máy thật giữ thêm:
  `config/.codex-backups/pre-full-config-rewrite-20260820-191536/`.
- Snapshot zip của cấu hình live:
  `extras/Config download/config-20260820-194101.zip`, SHA256
  `ACA930B70E3EF80A941032C346230AB537531208F159031D96E2BBB654674483`.

### Nguồn đối chiếu
- Klipper đúng commit máy thật `60fc7aa67a8da9abb43a2bad825d4992294ebf3f`.
- Moonraker, Mainsail client config, crowsnest 4.2, KlipperScreen,
  Cartographer, KTC-Easy v258 và `cekim-git/tool_crash` từ repository/tài liệu
  chính thức.
- Không áp dụng schema crowsnest v5 cho máy đang chạy v4.2.
- `mainsail.cfg` đồng bộ logic với `mainsail-config/client.cfg` chính thức.

### Thay đổi cấu hình
- Viết lại `hardware.cfg`, toolchanger user config và T0-T4 theo từng khối rõ
  ràng; xóa giá trị thử nghiệm cũ trong inline comment nhưng giữ nguyên giá trị
  production hiện hành.
- Giữ nguyên tuyệt đối 6/6 file readonly KTC và toàn bộ block SAVE_CONFIG.
- Loại `_THERMAL_CALIBRATION_PARAMS` và `_SET_CALIBRATION_MATERIAL` không còn
  consumer; giữ Axiscope active và ba guard chặn SexBolt cũ.
- Rút gọn macro nhưng giữ chú thích bảo trì cạnh từng khối: mục đích, số đo,
  điều kiện an toàn và điểm được phép tinh chỉnh. Không giữ nhật ký `BUG/FIX`
  hoặc giá trị thử nghiệm bên cạnh số production.
- `CANCEL_PRINT` nay dock tool đang active bằng `UNSELECT_TOOL` thay vì lấy T0.
- Sửa moisture-flush dryer dùng `min` để giới hạn 70%, đồng thời clamp tham số
  bed/chamber/humidity/time/fan vào khoảng an toàn.
- Clamp tham số cleaning, bỏ `M82` tạm thời và để SAVE/RESTORE quản lý extrusion
  mode của caller.
- Giữ tool_crash ở chế độ pause an toàn, retract E, không XYZ park và không
  emergency shutdown.
- `KlipperScreen.conf` chuyển block generated thành `[main]` rõ ràng với đúng
  bốn giá trị runtime cũ.
- `update.sh` tải archive GitHub vào `mktemp`, gọi installer backup-first rồi
  xóa source tạm; không để clone repository trên Pi.
- `install.sh` bảo vệ Tool Vision, KTC readonly, backup và dữ liệu local.
- `cleanup-voron.sh` mặc định dry-run và kiểm tra realpath trước khi xóa.

### Kiểm tra tĩnh
- 92/92 template Jinja user-owned parse thành công bằng delimiter của Klipper.
- 112/112 khai báo pin là duy nhất; không phát hiện pin trùng.
- Không còn duplicate section trong phạm vi user-owned. Các duplicate với
  readonly/Mainsail đều là override có chủ đích và đúng include order.
- Block SAVE_CONFIG giống backup từng byte.
- 6/6 file KTC readonly có SHA256 không đổi.
- `git diff --check` đạt sau khi xử lý whitespace; tất cả file cấu hình/script
  dùng LF.

### Đồng bộ và xác minh máy thật
- Trước deploy: Klipper ready, print standby, pause false, active tool -1, bed
  và năm hotend target 0.
- Upload 24 file production user-owned qua Moonraker; 24/24 SHA256 khớp PC.
- Chỉ chạy Klipper `RESTART`; không home, heat, probe, QGL hoặc toolchange.
- Sau restart: Klipper ready, warning 0, failed component 0.
- Axiscope và tool_crash load; Tool Vision và tools_calibrate không load.
- Runtime xác nhận safe_y 120, fast speed 15000, path speed 900; năm dock và
  năm bộ XYZ offset đúng dữ liệu production.
- Runtime xác nhận dryer dùng giới hạn 70% và cancel cleanup chứa
  `UNSELECT_TOOL`.
- Chạy `CALIBRATION_STATUS` và `CHECK_OFFSETS` không chuyển động; kết quả đủ
  T0-T4 và đúng offset.
- Camera proxy trả HTTP 200, `image/jpeg`, 309145 byte.
- Trạng thái cuối: standby, pause false, active tool -1, sáu heater target 0.

### Giới hạn kiểm tra cơ khí
- Không tự động chạy G28, Cartographer Touch, QGL, pickup/dropoff hoặc test in.
- Các đường dock/tọa độ được bảo toàn từ máy thật; cần người đứng máy cho lần
  kiểm thử chuyển động tiếp theo.
- Chưa enable Tool Vision; camera vẫn phục vụ soi buồng cho tới khi người dùng
  đặt lên gá nam châm và đo station thủ công.

### Git
- Commit cấu hình và backup: `8b5a170` —
  `Rewrite production configuration and deployment flow`.
- Đã push thành công nhánh `main` lên
  `git@github.com:IDcrazy123/All-Config-Voron.git`.

## 9. Hoàn nguyên về đúng mốc trước yêu cầu lúc 18:13

### Mục tiêu
- Đưa All-Config, Tool Vision độc lập và cấu hình live trên Pi về trạng thái
  ngay trước tin nhắn “viết lại dự án để 5tool hoạt động...” lúc 18:13.
- Giữ toàn bộ backup và lịch sử Git để mọi bước rollback vẫn có thể đảo ngược.

### Xác định đúng mốc từ lịch sử chat và Git
- Commit cuối trước yêu cầu là `2f04bfa`, thời gian
  `2026-08-20 18:12:28 +07:00`.
- `e39b26f` có thời gian `18:57:47` và là kết quả của chính yêu cầu trong ảnh;
  `8b5a170` và `9fa38a8` là hai lượt tiếp theo.
- Backup `pre-five-tool-rewrite-20260820-181903` ghi rõ baseline `2f04bfa`.
- 33/33 file `pc-config/` khớp Git blob của `2f04bfa`; 21/21 file Tool Vision
  trong backup khớp commit `634e8ae` lúc 17:58:46.

### Sao lưu trước rollback
- Backup hiện trạng sau các lượt tái cấu trúc:
  `extras/backups/pre-rollback-full-config-rewrite-20260820-195913/`.
- Nội dung gồm 33 file config PC, 34 file live, các tài liệu repo bị ảnh hưởng
  và source Tool Vision tại commit `16ff1b2`.
- Máy in giữ thêm 34/34 file tại
  `config/.codex-backups/pre-rollback-full-config-rewrite-20260820-195913/`.
- `.venv` và hai checkout Axiscope/kTAMV trong snapshot Tool Vision chỉ được
  giữ local; Git backup lưu source và commit ghim, không đẩy 230 MB môi trường
  dựng lại được lên GitHub.

### Khôi phục All-Config
- Toàn bộ 33 file trong `config/` khớp byte với cây Git `2f04bfa`.
- Khôi phục root README, `.gitignore` và hướng dẫn StealthChanger về bản 18:12.
- Loại hai tài liệu được tạo sau yêu cầu: `hardware-invariants.md` và
  `toolvision-integration-plan.md`.
- Khôi phục hai gitlink tham khảo về đúng commit:
  Axiscope `9a1a9ef`, kTAMV `72421f2`.
- Giữ `.gitattributes` chỉ để các backup timestamped không bị `core.autocrlf`
  thay đổi byte; giữ toàn bộ backup, snapshot zip và nhật ký đã có.

### Khôi phục Tool Vision độc lập
- Khôi phục 9 file thay đổi bởi commit `16ff1b2` về commit `634e8ae`.
- So sánh toàn bộ tracked tree: khớp `634e8ae`.
- Python compile đạt; `unittest discover` đạt 23/23 test.
- Commit rollback mới `cad935b` đã push lên `IDcrazy123/Tool-Vision`.

### Khôi phục và kiểm tra máy in
- Khôi phục bản live `pre-five-tool-rewrite-20260820-181903/live-config/`.
- Lượt đầu đưa 24 file về `e39b26f`; sau khi đối chiếu timestamp phát hiện mốc
  đó vẫn nằm sau yêu cầu, tiếp tục khôi phục 15 file của lớp `2f04bfa`.
- Kiểm tra cuối 34/34 file live khớp SHA-256 với backup mục tiêu; không sửa 6
  file KTC readonly vì chúng vốn không thay đổi.
- Chạy `FIRMWARE_RESTART`; không home, probe, QGL, pickup/dropoff, gia nhiệt
  hoặc chuyển động.
- Gọi `INITIALIZE_TOOLCHANGER` không có `RECOVER` để đồng bộ cảm biến T0; mã KTC
  xác nhận đường lệnh này không thực hiện chuyển động.
- Trạng thái cuối: Klipper `ready`, Moonraker 0 warning/0 failed component,
  print `standby`, pause `false`, active T0 = detected T0 và 6 heater target 0.

### Kết quả
- Production trên PC và Pi đã trở về đúng mốc trước 18:13. Tool Vision độc lập
  cũng trở về bản trước yêu cầu; các backup và lịch sử sau mốc được bảo toàn để
  truy vết hoặc phục hồi lại nếu cần.

## 10. Gộp cấu hình, rà soát logic và stage Tool Vision

### Mục tiêu
- Gộp hai lớp cấu hình crash thành một file dễ hiểu.
- Gộp calibration và Cartographer/mesh thành một file theo đúng bối cảnh.
- Stage cấu hình Tool Vision trên PC và Pi, chưa chạy hiệu chuẩn cơ khí.
- Đọc lại comment/logic, sửa lỗi có thể chứng minh mà không thay đổi dữ liệu
  phần cứng.

### Backup trước thay đổi
- Local:
  `extras/backups/pre-config-merge-toolvision-20260820-201907/`.
- Backup gồm cấu hình PC, 34 file cấu hình live và source Tool Vision tại commit
  `cad935b377e6f1d6f6750e84f4dfb322d16a5f02`.
- Pi:
  `config/.codex-backups/pre-config-merge-toolvision-20260820-201907/config/`.
- Đã upload và xác minh đủ 34/34 file trong backup trên Pi.

### Đối chiếu nguồn
- `cekim-git/tool_crash` commit
  `5cb00ad9e0216db97b8139a627b41407c86c88a9`: plugin tự tắt detector/watchdog
  trước khi gọi `crash_gcode`; thiếu `crash_gcode` mới gọi
  `printer.invoke_shutdown()`.
- KTC-Easy commit
  `e881fe40949a3999b0d63f59c22df589474eae9b`: readonly hiện tại trên máy là
  bản copy cũ, chưa phải symlink do installer mới quản lý.
- Klipper Config Reference: mesh giữ tọa độ probe hiện tại; Klipper native
  không có `sensor_type: DHT22`.
- Tool Vision độc lập: 23/23 test đạt, không resize/fix cứng 640x480, station
  camera vẫn để trống để buộc người dùng đo thủ công.

### Thay đổi cấu hình
- Tạo `Printer-Setup/tool-crash.cfg`, gộp:
  - `[tool_crash]`;
  - adapter KTC `START_CRASH_DETECTION`/`STOP_CRASH_DETECTION`;
  - `_TOOL_CRASH_SAFE_PAUSE`.
- Tạo `Printer-Setup/calibration-probe.cfg`, gộp:
  - Cartographer, bed mesh, ADXL345, axis twist;
  - Axiscope PF2 đang active;
  - trạng thái backend và báo cáo XYZ offset;
  - guard cho macro SexBolt/tools_calibrate cũ.
- Bốn file cũ được giữ tại
  `extras/retired-configs/2026-08-20-config-merge/` và trên Pi tại
  `config/.codex-backups/retired-configs/2026-08-20-config-merge/`.
- Thêm `config/Tool-Vision/tool_vision.cfg` ở trạng thái stage. Include vẫn
  comment, Axiscope vẫn active, camera X/Y/Z/safe-Z vẫn để trống.
- Sửa comment sai về PF4/X257/Y327, DHT22 native, vai trò Cartographer trong
  tool crash, hành vi shutdown/pause và thứ tự override.
- `update.sh` dùng archive tạm, không giữ clone Git trên Pi. `install.sh` quản
  lý riêng một file `.cfg` của Tool Vision nhưng bảo vệ runtime/result cục bộ và
  KTC readonly. `cleanup-voron.sh` kiểm tra realpath trước khi xóa.

### Lỗi logic đã sửa
- `PRINT_START` sai tool/nhiệt nay dùng `action_raise_error`; không còn gọi
  `CANCEL_PRINT` rồi vô tình chạy cleanup/toolchange.
- `PRIME_LINES` đếm đúng initial tool dùng `TOOL_TEMP` khi đồng thời có Tn_TEMP.
- Runout của tool active chỉ pause khi `print_stats.state == printing`.
- `PRINT_END` sau `UNSELECT_TOOL` nay đặt LED complete cho toàn bộ tool thay vì
  tìm active tool không còn tồn tại.
- Moisture flush đổi `max` thành `min`, giới hạn 70%, đúng cửa sổ 30 giây; fan
  luôn nhận cả target 0 để không giữ tốc độ cũ.

### Kiểm tra tĩnh
- 22 file active, 189 section; 119/119 template Jinja parse thành công.
- 112 khai báo pin, không có pin trùng trong đồ thị active.
- `SAVE_CONFIG` giống backup từng byte.
- Hardware option, T0-T4, Cartographer/mesh, PF2 Axiscope và tham số tool_crash
  giữ nguyên.
- 22/22 Orca JSON parse thành công.
- Bash syntax của ba script đạt; `git diff --check` đạt.
- Tool Vision độc lập: Python compile đạt, unit test 23/23.

### Đồng bộ và trạng thái máy thật
- Trước deploy: Klipper ready, print standby, pause false, T0 active/detected,
  sáu heater target đều 0.
- Upload 14 file thay đổi; hash 14/14 khớp. Kiểm tra toàn payload sau đó:
  31/31 file triển khai khớp SHA-256 giữa PC và Pi.
- Chỉ gọi Klipper `RESTART` để parse; không G28, probe, QGL, toolchange, heat
  hoặc calibration.
- Sau restart: Klipper ready, warning 0, failed component 0, print standby,
  pause false, T0 được cảm biến phát hiện, sáu heater target 0.
- Runtime xác nhận `tool_crash` dùng safe pause, `crash_mintime=0.1`, Axiscope
  vẫn ở PF2/X68/Y-10/Z7; `tool_vision` chưa load đúng trạng thái stage.
- Sau khi chuẩn hóa EOF, upload lại ba file gộp/stage; SHA-256 PC/Pi khớp
  3/3. Lần `RESTART` cuối trở lại `ready`, `standby`, không pause, detected T0,
  active tool -1 do KTC chưa initialize lại và sáu heater target đều 0.
- Commit cấu hình `8e5b34d` đã push lên `origin/main`.

### Vấn đề còn lại sau audit
- Chưa thể cài runtime/service Tool Vision vì SSH tới `voron@192.168.1.43`
  trả `Permission denied (publickey,password)` và Moonraker không cung cấp API
  cài arbitrary systemd/Klipper extra. Không dùng đường thực thi tạm thiếu an
  toàn để lách quyền này.
- Tool Vision hiện tại chưa có khóa arm thủ công dành riêng cho camera tháo lắp;
  station trống và include comment đang chặn chuyển động. Phải thêm/kiểm tra lớp
  khóa này trước cutover production.
- KTC readonly trên Pi là copy cũ, không phải symlink của installer v258. Script
  deploy mới ngừng ghi đè nhưng cần chạy lại installer KTC khi có SSH.
- Hai gitlink legacy `extras/Axiscope-reference` và `extras/kTAMV` không có entry
  tương ứng trong `.gitmodules`; source tham khảo đúng hiện nằm trong repo Tool
  Vision độc lập. Chưa xóa trong lượt này để tránh lặp lại thay đổi rollback.
- Dryer vẫn chưa clamp toàn bộ tham số nhập và chưa chặn gọi START_DRYER lần hai.
- Nozzle-clean chưa clamp tham số và lệnh wipe thủ công có thể chạy khi nozzle
  cao hơn nhiệt độ làm sạch mặc định.
- Cancel cleanup để T0 active, trong khi PRINT_END để shuttle rỗng; cần chọn một
  policy thống nhất rồi kiểm nghiệm cơ khí có người giám sát.
- Chưa kiểm nghiệm home, dock/pickup, Cartographer, camera, switch hoặc first
  layer theo yêu cầu không chạy thực tế trong lượt này.

## 11. Sửa URL camera Tool Vision bị từ chối truy cập

### Triệu chứng
- Mở `127.0.0.1:8080` từ PC trả connection refused.

### Phân tích nhật ký
- Crowsnest live log:
  [crowsnest.log](http://192.168.1.43/server/files/logs/crowsnest.log).
- Crowsnest đang chạy `camera-streamer`, camera MF-500 tại 1280x720/30 fps,
  `port: 8080` và `no_proxy: false`.
- Raw LAN URL `192.168.1.43:8080` không nhận kết nối, đúng với việc không mở
  raw camera port ra LAN.
- Moonraker webcam database công bố `/webcam/stream`; snapshot reverse proxy
  trả HTTP 200 JPEG và stream reverse proxy trả HTTP 200 multipart MJPEG.

### Nguyên nhân gốc
- `127.0.0.1` trong trình duyệt trên PC là loopback của PC, không phải CM4 của
  máy in. Cấu hình cũ cũng dùng raw port 8080 thay vì route reverse proxy đã
  được xác minh từ mạng thực tế.

### Hướng khắc phục đã thực hiện
- Backup PC và Pi tại
  [pre-fix-toolvision-camera-url-20260820-205334](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-fix-toolvision-camera-url-20260820-205334/).
- Đổi `camera_source` trong `config/Tool-Vision/tool_vision.cfg`:
  - Cũ: `http://127.0.0.1:8080/?action=stream`
  - Mới: `http://192.168.1.43/webcam/stream`
- Giữ `server_url: http://127.0.0.1:8085`; đây là API Tool Vision dự kiến chạy
  trên cùng Pi, không phải URL camera dành cho trình duyệt.

### Kiểm tra
- Strict INI parse: đạt, chỉ có một section `[tool_vision]`.
- URL mới: HTTP 200, `multipart/x-mixed-replace`.
- Upload Pi và xác minh SHA-256 PC/Pi: khớp.
- Không restart Klipper vì Tool Vision vẫn đang stage và include chưa bật.

### Kết quả
- URL xem/thử camera từ PC là `http://192.168.1.43/webcam/stream`.
- Không mở cổng raw 8080 ra LAN và không thay đổi cấu hình Crowsnest production.

## 12. Kiểm tra điều kiện cutover Axiscope sang Tool Vision

### Mục tiêu
- Bật include Tool Vision và gỡ Axiscope nếu hai backend xung đột.

### Kiểm tra thực tế
- Klipper objects: `axiscope=true`, `tool_vision=false`,
  `tools_calibrate=false`.
- Moonraker `available_services` có `axiscope` nhưng không có
  `tool-vision`.
- LAN `192.168.1.43:8085/health` không nhận kết nối. Dịch vụ thiết kế để bind
  loopback nên phép thử này chỉ bổ trợ; danh sách service và Klipper object mới
  là bằng chứng runtime chưa được cài/load.
- SSH `voron@192.168.1.43` tiếp tục trả
  `Permission denied (publickey,password)`.
- Sau khi người dùng báo đã cấp key, thử lại với `IdentitiesOnly=yes` và ép
  chính xác `C:\Users\batca\.ssh\id_ed25519`; client đã offer fingerprint
  `SHA256:yxE9VagQtOgNe24Q66f8HeGO9vKt30Uwn2aUt6eg29o` nhưng server không accept.
  Các tài khoản `voron`, `pi`, `mks`, `biqu`, `root` đều bị từ chối.
- Source Tool Vision chủ động báo config error nếu `[axiscope]` hoặc
  `[tools_calibrate]` cùng tồn tại vì các backend cùng tạo
  `probe_multi_axis`.

### Kết luận an toàn
- Chưa sửa `printer.cfg` hoặc `calibration-probe.cfg`. Tắt Axiscope và bật
  include khi `tool_vision.py` chưa nằm trong Klipper extras sẽ đưa Klipper về
  `not ready` với section `[tool_vision]` không xác định.
- Cutover bắt buộc theo thứ tự: cấp SSH, chạy installer Tool Vision, kiểm tra
  `tool-vision.service` và loopback API 8085, backup, tắt `[axiscope]`, bật
  include, rồi chỉ chạy `RESTART` để parse. Không chạy chuyển động/calibration
  trong bước cutover cấu hình.

### Trạng thái máy
- Không có cấu hình production nào bị thay đổi trong lượt kiểm tra này.
- Axiscope tiếp tục active để không làm mất backend hiệu chuẩn đang hoạt động.

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

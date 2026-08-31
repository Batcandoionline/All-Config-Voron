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

## 2. Chẩn đoán camera calibration kTAMV lỗi `stdev`

### Triệu chứng

- Operator đã home, đưa T0 tới X `170`, Y `20`, Z `40` và chạy
  `KTAMV_CALIB_CAMERA` có giám sát.
- Mười bước trả `0.042, 0.063, 0.064, 0.067, failed, 0.003, 0.004, 0.004,
  0.064, 0.060`; sample về tâm là `0.0600`.
- Lệnh kết thúc bằng
  `_calibrate_px_mm failed _get_average_mpp_from_lists failed stdev requires at least two data points`.

### Phân tích nhật ký

- [klippy.log](file:///home/voron/printer_data/logs/klippy.log) — evidence tại
  các dòng 15340–15490.
- Source upstream gọi `statistics.stdev()` sau mỗi vòng lọc mà không kiểm tra
  danh sách còn tối thiểu hai phần tử.
- Mô phỏng đúng thuật toán với các sample trên: mean ban đầu `0.043`, stdev
  `0.028045`; trước bộ lọc ±25% còn bảy giá trị với mean `0.042`; sau bộ lọc chỉ
  còn `[0.042]`, nên `stdev()` phát exception.
- Dòng `Calibrated camera center: mm/pixel found: 0.0600` chỉ là sample về tâm,
  không phải kết quả calibration cuối.

### Nguyên nhân gốc

- Dữ liệu detector chia thành hai cụm không tương thích: `0.060–0.067` và
  `0.003–0.004`. Theo công thức `mm/pixel = quãng đường máy / quãng đường ảnh`,
  cụm rất nhỏ tương ứng marker nhảy khoảng 158–175 pixel giữa các điểm, phù hợp
  với việc detector chuyển sang reflection/blob khác.
- Upstream có lỗi thứ cấp: bộ lọc không fail rõ ràng khi còn dưới hai sample mà
  để `statistics.stdev()` phát lỗi Python.

### Kết quả và phạm vi an toàn

- Klipper vẫn `ready`, printer `standby`, bed target `0`, homed `xyz`, vị trí
  `[170,20,40]`; T0 được phần cứng phát hiện.
- kTAMV giữ `is_calibrated=false`, `mm_per_pixels=null`, origin `null`; không có
  matrix hoặc offset nào được chấp nhận.
- Chỉ đọc API, source và log; không gửi thêm G-code, không sửa config/runtime.
- Không chạy `KTAMV_FIND_NOZZLE_CENTER`; trước lần calibration mới phải xác minh
  marker trên ảnh processed nằm đúng lỗ nozzle và cải thiện ánh sáng/focus.

## 3. Đối chiếu ảnh raw và processed sau calibration thất bại

### Bằng chứng ảnh

- Screenshot Mainsail lúc `2026-08-31 12:23:27` hiển thị đồng thời camera raw
  và output processed kTAMV tại X `170`, Y `20`, Z `40`.
- Marker đỏ processed nằm quanh vị trí detector gần `[308,262]`, trên vùng sáng
  bão hòa ở giữa đầu nozzle. Ảnh raw có glare xanh/trắng mạnh; mép lỗ nozzle
  thật không tách rõ khỏi điểm phản xạ trung tâm.
- Marker tĩnh nhìn gần tâm ảnh nhưng không chứng minh cùng một feature được theo
  dõi suốt pattern. Các scale `0.003–0.004` vẫn cho thấy detector đã nhảy khoảng
  158–175 pixel tại bước 6–8.

### Kết luận

- Không dùng ảnh này để chấp nhận calibration hoặc chạy centering.
- Giảm bão hòa/phản xạ, dùng ánh sáng khuếch tán và chỉnh focus để thấy rõ mép
  lỗ nozzle trước lần thử mới; không tăng tolerance để ép detector pass.
- Chỉ phân tích screenshot; không gửi G-code và không thay đổi máy.

## 4. Chỉnh ánh sáng MF-500 và sửa detector kTAMV tại máy thật

### Phạm vi an toàn

- Operator yêu cầu giữ nguyên tool trên camera. Không gửi `G28`, toolchange,
  heater, `KTAMV_CALIB_CAMERA`, `KTAMV_FIND_NOZZLE_CENTER` hoặc bất kỳ lệnh
  chuyển động nào.
- Vòng soi nozzle được xác nhận là WCMCU WS2812B tám LED do ESP32-C3 Mini cấp
  nguồn/điều khiển riêng ở 5%; không nối Klipper và không bị thay đổi.
- `T0_LED` là chuỗi ba LED riêng trên toolhead. Tắt cả ba LED loại được hai vệt
  phản xạ phía dưới nozzle; trạng thái cuối của cả ba là `[0,0,0,0]`.

### Thử camera và bằng chứng ảnh

- Sao lưu camera ban đầu tại
  `/home/voron/printer_data/config_backups/pre-mf500-image-tuning-20260831-124000/`.
- MF-500 chỉ expose brightness/contrast/gamma, không expose exposure/focus.
  Baseline là `brightness=0`, `contrast=36`, `gamma=120`.
- Ba phép thử tạm `-16/28/100`, `-32/20/100`, `-8/36/120` đều làm blob đỏ lớn
  hơn nên đã hoàn nguyên chính xác baseline.
- Khi `T0_LED` còn bật, detector ổn định tĩnh tại `[334,275]` nhưng ảnh raw có
  glare mạnh. Khi tắt `T0_LED`, ảnh raw thấy rõ viền nozzle hơn nhưng pipeline
  upstream chỉ bắt blob giả `[192,134]` ở góc trên-trái khối nhôm.
- Chạy riêng cả năm tổ hợp detector trên ba frame: bốn tổ hợp đầu không có
  keypoint; `superRelaxed/pre2` chỉ trả `[192.2–192.3,133.8]`, cách tâm khoảng
  166 pixel.
- Component sáng compact ở threshold 245 ổn định trong mười frame tại
  `[336.15–336.19,252.83–252.92]`; sau khi làm tròn, cả mười đều là
  `[336,253]`.

### Bản sửa runtime

- Sao lưu trước khi sửa tại:
  - repo: `extras/backups/pre-ktamv-optical-fallback-20260831-125120/`;
  - máy thật:
    `/home/voron/printer_data/config_backups/pre-ktamv-optical-fallback-20260831-125120/`.
- Thêm patch `config/scripts/patches/ktamv-center-highlight-fallback.patch`:
  - loại keypoint super-relaxed xa tâm hơn 120 pixel;
  - khi năm pipeline upstream không có đúng một keypoint hợp lệ, tìm component
    sáng compact trong vùng tâm và gắn algorithm 6;
  - guard `statistics.stdev()` khi chỉ còn một sample, để caller báo không đủ
    75% điểm thay vì phát `StatisticsError`.
- `git apply --check`, `py_compile` và `git diff --check` trên runtime đều đạt.
  Unit test trả `(0.0, 0.06)` cho một sample và `ValueError` rõ ràng cho list
  rỗng.
- `config/scripts/install.sh` hiện preflight đủ marker cho multi-object,
  center-highlight và stdev. Script cùng patch mới đã deploy vào config máy;
  `bash -n` và reverse patch check đều đạt.
- Restart user service `ktamv-server.service`, sau đó hai lần
  `KTAMV_SIMPLE_NOZZLE_POSITION` trước/sau `RESTART` Klipper lần lượt trả
  `[336,253]` sau 5,42 và 5,09 giây. Ảnh processed đặt marker cyan đúng trên
  phản xạ tròn trung tâm nozzle.
- `RESTART` chỉ nạp lại extension, không làm tool vật lý di chuyển. Nó xóa trạng
  thái home; trạng thái cuối `homed_axes=""`, printer `standby`, heater target
  bằng 0, kTAMV `is_calibrated=false`, origin và mm/pixel `null`.
- Sau `RESTART`, `LED_INIT` đã được ghi đè bằng lệnh không chuyển động
  `SET_LED LED=T0_LED RED=0 GREEN=0 BLUE=0 TRANSMIT=1`; `T0_LED` vẫn tắt.
- Camera kết thúc tại baseline `brightness=0`, `contrast=36`, `gamma=120` và
  service kTAMV `active`.

### Tài liệu và giới hạn còn lại

- Cập nhật hướng dẫn Việt/Anh để phân biệt vòng ESP32-C3 5% với `T0_LED`, ghi
  lệnh tắt LED, marker đúng/sai và hai patch runtime đã review.
- Chưa chạy lại calibration vì nó có chuyển động và Klipper hiện chưa home.
  Lần test chuyển động tiếp theo chỉ thực hiện khi operator đứng máy và cho phép
  rõ ràng.

## 5. Đo XY tool offset bằng kTAMV tại Z40

### Cho phép và điều kiện đo

- Operator xác nhận camera có Z an toàn `40` và vùng camera quanh
  `X170 Y20 Z40`, đồng thời yêu cầu thực hiện phép đo XY.
- Không thay đổi vị trí camera, không điều khiển vòng WCMCU WS2812B tám LED
  dùng ESP32-C3 Mini độc lập; vòng này tiếp tục ở mức sáng 5%.
- LED trên tool đang đo được tắt trước khi nhận dạng để tránh glare. Không bật
  heater; tất cả heater target giữ `0 degC`.
- T0 ban đầu đã được operator home và đặt tại `X170 Y20 Z40`. Mọi chuyển động
  đo đều dùng Z G-code `40`; không đo hoặc thay đổi Z offset.

### Camera calibration và origin

- Lần calibration đầu trả mười sample
  `0.036, 0.054, 0.059, 0.059, 0.056, 0.036, 0.010, 0.059, 0.056, 0.052`
  và sample tâm `0.052`. Sau lọc thủ công còn 7/11 sample nên không được dùng,
  dù code upstream báo nhận `0.055`.
- Lần calibration thứ hai trả
  `0.036, 0.056, 0.059, 0.056, 0.056, 0.036, 0.056, 0.059, 0.056, 0.052`
  và sample tâm `0.052`. Sau lọc còn 9/11 sample, mean `0.056 mm/pixel`,
  relative stdev `4.4%`; phép này được chấp nhận cho phiên đo.
- T0 được căn tới UV `[320,240]`. Camera origin trong RAM được đặt tại
  `X168.805 Y18.420`; kTAMV status cuối vẫn là `calibrated=True`,
  `mm_per_pixel=0.056`, `origin=(168.805,18.42)`.
- Phát hiện thêm lỗi upstream: `_get_average_mpp_from_lists()` thay đổi list
  đầu vào tại chỗ, làm kiểm tra giữ tối thiểu 75% sample ở caller trở nên vô
  hiệu. Vì vậy tiêu chí 9/11 nêu trên được kiểm tra độc lập; chưa sửa runtime
  trong phần việc đo này.

### Kết quả đo chỉ báo cáo

`KTAMV_GET_OFFSET` là residual từ camera origin trong hệ G-code hiện hành.
Với KTC đang áp dụng production offset, ứng viên mới được tính theo
`offset đang nạp + residual đo được`.

| Tool | Offset đang nạp X/Y (mm) | Residual lặp (mm) | Ứng viên phiên này X/Y (mm) |
| --- | --- | --- | --- |
| T1 | `-0.243 / -0.252` | pickup đầu `0.000 / 0.000`; pickup sau `+0.027 / +0.049`, `+0.027 / +0.032`, `+0.027 / +0.032` | theo mean pickup sau: `-0.216 / -0.214` |
| T2 | `+0.746 / +0.086` | `+0.001 / +0.154` (3/3 giống nhau) | `+0.747 / +0.240` |
| T3 | `+0.304 / +0.449` | `0.000 / +0.068` (3/3 giống nhau) | `+0.304 / +0.517` |
| T4 | `+0.041 / +0.352` | `+0.079 / -0.091` (3/3 giống nhau) | `+0.120 / +0.261` |

- T1 thể hiện sai khác giữa hai lần pickup. Sau khi hoàn tất T1-T4 và pickup
  lại T0, T0 cần correction `X-0.052 Y+0.055 mm` để trở lại UV `[320,240]`.
  Đây là bằng chứng độ lặp lại toolchange/detector cùng cỡ một pixel
  (`0.056 mm`), nên các ứng viên trên chưa đủ để ghi production trực tiếp.
- Không chạy `SAVE_CONFIG`, không sửa `gcode_x_offset`/`gcode_y_offset`, không
  restart Klipper và không thay đổi file config/runtime trong phép đo.

### Trạng thái máy khi bàn giao

- Toolchanger `ready`; active tool và detected tool đều là T0; homed axes
  `xyz`; printer ở trạng thái standby.
- T0 được để đúng tâm camera tại `X168.753 Y18.475 Z40`, `T0_LED` tắt.
- Extruder T0-T4 và bed đều target `0 degC`; nhiệt độ thực tế khoảng
  `31-34 degC`.
- Calibration và origin chỉ còn trong RAM và sẽ bị xóa khi Klipper restart.

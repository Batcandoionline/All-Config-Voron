# Nhật ký — 2026-08-22

## 1. Đồng bộ máy thật và ghi nhận ToolVision 3.2.1 đang phát triển

### Mục tiêu

- Tải snapshot cấu hình mới từ máy thật `192.168.1.43` và so sánh với payload trên PC.
- Ghi rõ ToolVision đã được cài như một repository phát triển độc lập để tránh nhầm là backend staged/disabled.
- Đồng bộ cấu hình ToolVision 3 đang chạy trên máy về All-Config, giữ đúng phần máy-specific và triển khai lên máy đúng một lần.
- Bảo vệ dữ liệu printer-local sau khi phát hiện lỗ hổng trong danh sách exclude của `install.sh`.

### Trạng thái ToolVision đã xác nhận

- Repository chính: `https://github.com/IDcrazy123/Tool-Vision`.
- Bản PC: `D:\Desktop\Tool-Vision`, nhánh `main`, sạch, tag `v3.2.1`.
- Bản máy thật: `/home/voron/Tool-Vision`, nhánh `main`, sạch, tag `v3.2.1`.
- GitHub `origin/main`, PC và máy thật cùng commit `42202a295d4b28321afe5f047c59b4d367399fed`.
- `tool-vision.service`, `klipper` và `moonraker` đều active.
- Moonraker Update Manager nhận đúng mục `tool-vision`, repository pristine, không dirty và không chậm commit.
- Runtime object: ToolVision `3.2.1`, `switch_ready=true`, `camera_ready=false`, không busy, không có lỗi cuối.
- State schema 2 đã giữ station switch; camera/detector/transform chưa setup.

### Snapshot máy thật

- Thư mục: `extras/Config download/config-20260822-062513/`.
- ZIP: `extras/Config download/config-20260822-062513.zip`.
- Số file: 32.
- SHA-256 ZIP: `CEB433E5248C486DFAF35AC84745E50B4C40BB85D28A633B254C235AD36F359B`.
- Snapshot chỉ chứa cấu hình cần đối chiếu; kiểm tra không có `moonraker.secrets`, Wi-Fi config, key, PEM, env hoặc log.

Trước khi hợp nhất, chỉ có ba file chung khác nhau:

- `Printer-Setup/print-macros.cfg` — PC có giao diện dry mới, máy chưa nhận bản triển khai.
- `moonraker.conf` — máy đã có include Update Manager của ToolVision.
- `Tool-Vision/tool_vision.cfg` — máy dùng cấu hình ToolVision 3 tối giản, repo All-Config còn cấu hình Tool Vision 2 cũ.

`Tool-Vision/moonraker_update_manager.conf` chỉ có trên máy vì do installer ToolVision tạo bằng đường dẫn runtime thật. File này được snapshot để đối chiếu nhưng không chuyển quyền quản lý sang All-Config.

### File đã sửa đổi

- `config/Tool-Vision/tool_vision.cfg` — thay cấu hình Tool Vision 2 bằng cấu hình ToolVision 3.2.1 teach-once; giữ `pin: ^PF2`, đồng bộ chú thích/hook mới từ repository ToolVision.
- `config/moonraker.conf` — thêm include `Tool-Vision/moonraker_update_manager.conf` do installer ToolVision quản lý.
- `config/scripts/install.sh` — bổ sung exclude cho state/result ToolVision, ShakeTune, ZIP snapshot và backup Moonraker printer-local.
- `README.md` — ghi rõ runtime ToolVision đã cài, version/commit, trạng thái station và cách cập nhật độc lập.
- `config/README.md` — cập nhật quyền sở hữu runtime/config/generated updater của ToolVision 3.
- `extras/docs/huong-dan-he-thong-stealthchanger.md` — thay workflow nhập tay X/Y/Z cũ bằng `TV_SETUP_CAMERA`, `TV_SETUP_SWITCH`, `TV_CALIBRATE`, `TV_REPORT`.

### Sao lưu

- [moonraker.conf (Backup)](<file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-toolvision-v3-live-config-20260822-062756/moonraker.conf>)
- [tool_vision.cfg (Backup)](<file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-toolvision-v3-live-config-20260822-062756/tool_vision.cfg>)
- [install.sh (Backup)](<file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-preserve-printer-local-runtime-data-20260822-164359/install.sh>)
- Backup tự động trên máy trước triển khai: `/home/voron/printer_data/config_backups/config-install-20260822-164204/`.

### Triển khai máy thật — đúng một lần

Trước triển khai:

- `print_stats.state=standby`.
- Không pause, ToolVision không busy.
- Bed target `0`, không có chu trình gia nhiệt.

Đã chuyển payload PC vào thư mục tạm và chạy `config/scripts/install.sh` đúng một lần. Script tạo backup máy `config-install-20260822-164204` trước khi thay đổi.

### Sự cố phát hiện trong lúc triển khai và phục hồi

Output `rsync --delete` cho thấy comment của script nói bảo vệ dữ liệu printer-local nhưng danh sách exclude thực tế còn thiếu, làm xóa tạm thời:

- `ShakeTune_results/`.
- `tool_vision_state.json`.
- `tool_vision_results.json`.
- Hai ZIP snapshot `config-*.zip`.
- `moonraker.conf.pre-tool-vision-20260821-215201`.

Do payload được SCP từ Windows, mode của năm thư mục nguồn là `500`; `rsync -a` truyền mode này sang `config/`, `Printer-Setup/`, `scripts/`, `toolchanger/` và `toolchanger/tools/`.

Xử lý trước khi restart:

1. Khôi phục toàn bộ dữ liệu vừa xóa từ backup máy `config-install-20260822-164204`.
2. Trả mode của năm thư mục về `755`, khớp backup gốc.
3. Xóa thư mục tạm sau khi cấp lại quyền ghi cho riêng target đã xác nhận.
4. Vá `install.sh` với các exclude:
   - `ShakeTune_results/`
   - `tool_vision_state.json`
   - `tool_vision_results.json`
   - `config-*.zip`
   - `moonraker.conf.pre-*`
5. Kiểm tra Bash syntax trên máy, đồng bộ riêng file script đã vá và xác nhận SHA-256 PC/máy cùng `8357287321e0929b9080c995e69c5d2ba9c04a39023f3c38429586f3c8483539`.

Không chạy `install.sh` lần thứ hai. Lệnh restart qua `sudo` bị từ chối trước khi thực hiện vì cần mật khẩu; sau đó Klipper được restart đúng một lần qua Moonraker API chính thức. Moonraker không cần restart vì include ToolVision đã tồn tại và nội dung functional không đổi.

### Kiểm tra

- ToolVision source test trên PC: 46/46 đạt.
- Phân tích CFG nghiêm ngặt: đạt.
- Phân tích 21 template theo delimiter Jinja của Klipper: đạt.
- `git diff --check` cho các file cấu hình/tài liệu đã sửa: đạt. Snapshot máy
  được giữ byte-for-byte nên vẫn chứa whitespace/blank EOF có sẵn trong
  Mainsail và KTC readonly; không normalize dữ liệu snapshot.
- Klipper sau restart: `ready`.
- Services: Klipper, Moonraker và ToolVision đều active.
- ToolVision API `/api/v2/health`: `ok=true`, version `3.2.1`.
- Mainsail/Moonraker G-code help có đủ `START_DRYER`, `STOP_DRYER`, `DRYER_STATUS`, `TV_STATUS`, `TV_SETUP_CAMERA`, `TV_SETUP_SWITCH`, `TV_CALIBRATE`, `TV_REPORT`.
- Không còn bảy macro public `DRY_PLA`, `DRY_TPU`, `DRY_PETG`, `DRY_ABS`, `DRY_ASA`, `DRY_NYLON`, `DRY_PC`.
- State ToolVision, result, ShakeTune và ZIP snapshot đều tồn tại sau phục hồi/restart.
- So sánh SHA-256: 25/25 file do All-Config quản lý khớp giữa PC và máy thật.
- Printer sau cùng: standby, không pause, bed target `0`, ToolVision không busy.

### Kết quả

All-Config, máy thật và repository ToolVision đã được đối chiếu và đồng bộ. Máy hiện chạy ToolVision 3.2.1 từ checkout Git độc lập, All-Config giữ cấu hình máy-specific, Mainsail có Update Manager ToolVision và giao diện dry mới đã nạp. Không mất dữ liệu printer-local; lỗi bảo vệ dữ liệu của installer đã được sửa để các lần update sau an toàn hơn.

### Vấn đề còn lại

- Camera ToolVision chưa setup. Chỉ chạy `TV_SETUP_CAMERA` khi có người tại máy, camera MF-500 đã đặt chắc trên gá, T0 sạch và đường đi an toàn.
- Sau setup camera, đo lặp bằng `TV_CALIBRATE MODE=XYZ`, xem `TV_REPORT` và xác nhận bằng bản in trước khi áp dụng offset.
- Installer vẫn cảnh báo KTC readonly configs hiện không phải symlink do installer quản lý. Không chỉnh sửa trực tiếp vùng readonly; xử lý riêng bằng KTC-Easy installer nếu cần nâng KTC.

## 2. Gom dữ liệu sinh tự động và xử lý thư mục ghost trên Mainsail

### Triệu chứng

- Mainsail hiển thị hai dòng `ShakeTune_results`; một dòng có thời gian
  `01/01/1970`, một dòng có thời gian thật.
- `tool_vision_state.json`, `tool_vision_results.json`, `.codex-backups`, hai ZIP
  snapshot và backup `moonraker.conf.pre-tool-vision-*` nằm lẫn trong root
  `~/printer_data/config`.
- Người dùng không thể biết mục nào là cấu hình, dữ liệu runtime hay backup.

### Phân tích nhật ký và filesystem

- Kiểm tra byte-level bằng `ls -labi`/`find` xác nhận chỉ có một thư mục vật lý
  `ShakeTune_results`, inode `534025`; Linux không có hai tên thật trùng nhau.
- Moonraker API cũng chỉ trả một cây vật lý. Dòng thời gian 1970 là entry ghost
  phía Mainsail sau lần rsync xóa/khôi phục thư mục trước đó.
- Moonraker log lúc `2026-08-22 16:54:58` ghi một yêu cầu move sai từ giao diện:
  `[Errno 20] Not a directory: '/home/voron/printer_data/config/tool_vision_results.json/tool_vision_results.json'`.
  Không có dấu hiệu file bị mất.
- Hai JSON là dữ liệu ToolVision hợp lệ: state schema 2 giữ switch station; file
  result schema 1 giữ kết quả Z gần nhất. `ShakeTune_results` là thư mục output
  hợp lệ của Klippain ShakeTune.

### Nguyên nhân gốc

- ToolVision 3.2.1 dùng mặc định hai file JSON ngay trong root `config`.
- ShakeTune cũng dùng một thư mục output ngay trong root.
- Backup/snapshot của các lần cài cũ chưa được chuyển sang `config_backups`.
- Lần đồng bộ trước đã xóa rồi phục hồi `ShakeTune_results` trong cùng phiên
  Mainsail, để lại metadata entry ghost có mtime epoch.

### Sao lưu

- [Backup PC](<file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-organize-generated-data-20260822-170108/>) — cấu hình All-Config, source ToolVision và bản bảo toàn công việc tài liệu đồng thời.
- Backup máy thật: `/home/voron/printer_data/config_backups/pre-organize-generated-data-20260822-170108/`.
- Backup máy thật có `SHA256SUMS` cho 167 file, tổng dung lượng 1.8 MB.

### Hướng khắc phục đã thực hiện

- Gom dữ liệu đang chạy vào một cây printer-local rõ ràng:
  - `Generated-Data/ToolVision/state.json`
  - `Generated-Data/ToolVision/results.json`
  - `Generated-Data/ShakeTune/`
- Sửa `config/Tool-Vision/tool_vision.cfg` và
  `config/Printer-Setup/input-shaper.cfg` để dùng các đường dẫn trên.
- Sửa `config/scripts/install.sh` và `config/.gitignore` để toàn bộ
  `Generated-Data/` không bị rsync/Git quản lý hoặc xóa.
- Di chuyển, không xóa, các artifact khỏi root:
  - `.codex-backups` → `config_backups/codex-backups-20260822-170108/`
  - ZIP và backup Moonraker → `config_backups/root-artifacts-20260822-170108/`
- Phát hành ToolVision `v3.2.2`, commit production `dd92a05`:
  - Default chung chuyển vào `config/Tool-Vision/` thay vì root.
  - Installer tự migrate file legacy nếu người dùng không đặt path tường minh.
  - Backup install/uninstall chuyển vào `config_backups/tool-vision/`.
- Update Manager nâng máy thật từ `v3.2.1` lên `v3.2.2` một lần và restart
  ToolVision, Klipper, Moonraker để nạp code/path mới.
- Tag backup của luồng tài liệu đồng thời từng làm Moonraker hiển thị version
  `?`; không xóa tag backup. Tag `v3.2.2` được làm mới với tagger timestamp mới
  hơn, sau đó Update Manager nhận đúng `v3.2.2-0`.
- Hai file tài liệu ToolVision thay đổi đồng thời đã được bảo toàn SHA-256 và
  khôi phục nguyên byte trên PC ở trạng thái unstaged; không bị lẫn vào release.

### Kiểm tra

- Bash syntax: `install.sh`, `uninstall.sh`, All-Config `install.sh` đạt.
- ToolVision test: 47/47 đạt cả trước và sau triển khai.
- CFG strict parse: `input-shaper.cfg` 3 section, `tool_vision.cfg` 6 section.
- Bốn file thay đổi trên PC/máy thật khớp SHA-256.
- Dữ liệu sau move được `cmp`/`diff -qr` với backup: đạt, không mất file.
- Moonraker file API chỉ còn một top-level `Generated-Data`; không còn entry
  vật lý `ShakeTune_results`, JSON ToolVision, ZIP, `.codex-backups` hoặc backup
  Moonraker ở root.
- Services `klipper`, `moonraker`, `tool-vision`: active; journal từ lúc update
  không có warning.
- Klipper: ready; printer standby, không pause, bed target 0.
- `TOOL_VISION_STATUS`: version/service `3.2.2`, switch setup yes, camera setup
  no, last error none.
- Update Manager: current/remote `v3.2.2-0`, behind 0, dirty false, pristine true.

### Kết quả

Root cấu hình đã gọn và phân biệt rõ cấu hình với dữ liệu sinh tự động. Entry
ShakeTune trùng chỉ là ghost UI, không phải dữ liệu trùng; sau restart Moonraker,
server chỉ trả một cây `Generated-Data`. Dữ liệu ToolVision đã học và kết quả cũ
được giữ nguyên, đồng thời bản cài ToolVision sau không tái tạo rác ở root.

### Vấn đề còn lại

- Trình duyệt Mainsail đang mở từ trước có thể cần bấm nút Refresh trong widget
  Config Files hoặc hard refresh một lần để bỏ state frontend cũ.
- Camera ToolVision vẫn chưa setup; không liên quan đến việc sắp xếp dữ liệu.

## 3. Rà soát mã nguồn và sửa logic Printer-Setup từ tool-crash đến calibration-probe

### Phạm vi và nguyên tắc

- Đọc lần lượt toàn bộ tám file production trong `config/Printer-Setup/`:
  `tool-crash.cfg`, `print-macros.cfg`, `prime-lines.cfg`, `nozzle-clean.cfg`,
  `input-shaper.cfg`, `hardware.cfg`, `fans-leds.cfg` và
  `calibration-probe.cfg`.
- Không sửa KTC readonly, tọa độ cơ khí, PID, Cartographer hay dữ liệu ToolVision
  đã học.
- Tạm dừng bản vá sau yêu cầu kiểm tra sâu; đối chiếu mã Python trước khi tiếp
  tục và chỉ triển khai sau khi kiểm thử render đạt.

### Mã nguồn đã đối chiếu

- Klipper đang chạy commit `60fc7aa67a8da9abb43a2bad825d4992294ebf3f`:
  `gcode_macro.py`, `delayed_gcode.py`, `buttons.py`, `fan.py`,
  `fan_generic.py` và `heaters.py`.
- KTC-Easy commit `e881fe40949a3999b0d63f59c22df589474eae9b`:
  `tool.py` và `toolchanger.py`; source cài trong Klipper khớp repository.
- `tool_crash.py` upstream commit
  `5cb00ad9e0216db97b8139a627b41407c86c88a9`; bản cài máy thật khớp nội dung
  upstream trước khi vá.
- ToolVision `tool_vision.py`: `TOOL_VISION_STATUS` chỉ đọc readiness/service và
  station do ToolVision sở hữu; macro config không thể đọc tọa độ station nội bộ
  qua status object.
- Tài liệu Klipper xác nhận macro được render toàn bộ trước khi lệnh sinh ra chạy,
  macro con render khi được gọi và delayed gcode phải hủy bằng
  `UPDATE_DELAYED_GCODE ... DURATION=0`.

### Lỗi gốc và sửa đổi

- Dryer và print cùng sở hữu bed heater/bed fan: thêm handoff không tắt nhiệt,
  hủy timer dryer và callback tắt fan cũ khi `PRINT_START` tiếp quản; timer dryer
  tự dừng nếu phát hiện print đang active.
- Dryer dock tool trước khi nâng Z đủ cao: chuyển Z lên tối thiểu 200 mm, giới hạn
  theo `axis_maximum.z`, trước `UNSELECT_TOOL`.
- Tham số dryer nâng cao không kiểm tra: chặn BED/CHAMBER/HUMIDITY/TIME/FAN/PARK
  ngoài phạm vi trước mọi chuyển động hoặc gia nhiệt.
- Crash detector tự disable sau crash nhưng RESUME không bật lại: thêm
  `START_CRASH_DETECTION` vào hook RESUME sau khi KTC initialize/verify thành công.
- Upstream `tool_crash.py` gọi crash với mọi cạnh của cả năm detection pin: lưu
  patch tối thiểu tại
  `config/scripts/patches/tool_crash-active-tool-validation.patch`; cạnh sensor
  nay dùng kiểm tra active-tool và confirmation threshold sẵn có của watchdog.
- `CLEAN_NOZZLE` nhầm `toolhead.extruder` là bằng chứng có tool thật: chuyển guard
  sang `toolchanger.tool_number`; khi không có tool sẽ abort trước SAVE/motion/heat.
- Cancel không xử lý vòng đời bed fan và ghi đè LED của T0 vừa pickup: schedule
  fan-off 180 giây như PRINT_END và dùng helper render sau toolchange để đồng bộ
  LED theo active tool thật.
- Fallback input shaper ghi là T0 nhưng không khớp T0: đồng bộ thành X
  `3hump_ei/98.6/0.081`, Y `mzv/35.0/0.076` đúng giá trị trong `T0.cfg`.
- `CALIBRATION_STATUS` hard-code tọa độ PF2 cũ: bỏ bản sao tọa độ và gọi
  `TOOL_VISION_STATUS` để báo trạng thái do ToolVision sở hữu.

### Sao lưu

- PC:
  `extras/backups/pre-fix-printer-setup-logic-20260822-174512/`.
- Máy thật:
  `/home/voron/printer_data/config_backups/pre-fix-printer-setup-logic-20260822-174512/`.
- Backup gồm năm CFG thay đổi và `tool_crash.py` đang chạy trước triển khai.
- Trước khi bổ sung khả năng tái áp patch, `install.sh` cũng được thêm vào cùng
  backup trên PC và máy thật.

### Kiểm thử trước triển khai

- `git diff --check`: đạt.
- `git apply --check` nghiêm ngặt trên cả upstream local và source đang cài trên
  máy thật: đạt.
- Dùng đúng `/home/voron/klippy-env` (Python 3.11.2, Jinja2 2.11.3): biên dịch
  62/62 template G-code trong tám file.
- 15 assertion render đạt: thứ tự nâng Z/dock, dryer handoff, delayed callback,
  nhánh print-active không tắt heat/fan, tham số lỗi abort, CLEAN_NOZZLE không có
  active tool, RESUME crash detector, cancel cleanup và ToolVision status.
- `tool_crash.py` patched compile đạt; mô phỏng xác nhận cạnh inactive không báo
  crash, active loss cần đủ hai lần, cạnh hồi phục reset counter và các guard
  disabled/toolchange/probing vẫn hoạt động.

### Triển khai và xác minh máy thật

- Trước triển khai: printer standby, không pause, bed target 0, bed fan 0,
  dryer 0, ToolVision không busy; Klipper/Moonraker/ToolVision active.
- Lệnh install staging đầu tiên bị PowerShell mở rộng sai biến đường dẫn và dừng.
  Hash sáu file đích được kiểm tra ngay sau đó, xác nhận toàn bộ vẫn là bản cũ;
  không restart ở bước lỗi này.
- Cài lại bằng sáu đường dẫn tuyệt đối, mode `0644`, rồi xác nhận SHA-256 từng
  file khớp staging. Restart Klipper một lần qua Moonraker API; ready sau 7 giây.
- Sau restart: 0 config warning; macro/command mới đều có trong G-code help;
  input shaper nạp đúng fallback T0; ba service active; log phiên Klipper không
  có traceback/config/template/shutdown error.
- Trạng thái cuối lúc kiểm tra: standby, không pause, bed target 0, bed fan 0,
  dryer 0, KTC ready với T0 active; ToolVision `3.3.0-rc1`, không busy.
- Không chạy lệnh gia nhiệt, vệ sinh nozzle, dryer hoặc toolchange để thử. Thư mục
  kiểm thử `/tmp/codex-printer-setup-audit-20260822-1815` đã được xác minh đúng
  target và xóa sau khi hoàn tất.
- Để lần update sau không làm quên bản sửa Python, `install.sh` preflight patch
  với `--fuzz=0`, bỏ qua nếu marker đã tồn tại, backup runtime trước khi áp và
  dừng an toàn nếu source upstream không còn tương thích.
- Bash syntax và bốn nhánh installer được kiểm thử trên máy thật: source chuẩn
  được chấp nhận, source giả lập lệch bị từ chối, runtime đã patch được bỏ qua
  idempotent. `install.sh` và patch canonical đã chép vào `config/scripts/`,
  khớp SHA-256 với PC; không chạy installer lần hai và không restart thêm.

### Kết quả

Các lỗi dùng chung heater/fan, thứ tự dock, vòng đời crash detector, nhận diện
active tool, LED cancel, fallback shaper và status calibration đã được sửa và nạp
trên máy thật. `prime-lines.cfg` và `hardware.cfg` không cần thay đổi sau khi rà
soát; KTC readonly không bị chỉnh sửa.

## 4. Gom cấu hình ToolVision khỏi thư mục riêng trong Mainsail

### Mục tiêu

- Đưa cấu hình Klipper ToolVision vào `Printer-Setup/`.
- Đưa updater ToolVision trực tiếp vào `moonraker.conf`.
- Xác định rõ tác dụng của backup và hai thư mục cùng tên dễ nhầm.
- Dọn `/config/Tool-Vision` mà không làm hỏng runtime hoặc mất dữ liệu đã học.

### Phân tích mã nguồn và máy thật

- `install.sh` của repository ToolVision là nguồn tạo
  `/config/Tool-Vision/tool_vision.cfg` và
  `/config/Tool-Vision/moonraker_update_manager.conf`.
- `backups/pre-v3.2.0-20260821-214510/` là bản bảo toàn trước migration cũ,
  không được runtime hiện tại đọc. Installer mới đã dùng đúng
  `~/printer_data/config_backups/tool-vision/`.
- Bốn file backup legacy được so sánh bằng `diff`, `cmp` và SHA-256 với
  `config_backups/tool-vision/manual-20260822-180254/`; tất cả giống hệt.
- `~/Tool-Vision` không phải thư mục thừa. Đây là Git runtime production tại
  commit `5e79f633`, được `tool-vision.service` dùng làm `WorkingDirectory`, và
  là đích của bốn symlink `klippy/extras/tool_vision*.py` cùng Moonraker updater.
  Xóa thư mục này sẽ làm hỏng service, module Klipper và cập nhật ToolVision.
- Python ToolVision vẫn có default path cũ khi người dùng không override; cấu
  hình máy này đặt rõ state/result dưới `Generated-Data/ToolVision`, nên việc
  chuyển file include không thay đổi hoặc làm mất state đã học.

### File đã sửa đổi

- `config/Printer-Setup/tool_vision.cfg` — chuyển nguyên byte từ
  `config/Tool-Vision/tool_vision.cfg`; SHA-256 giữ nguyên
  `c89cd8a5f9c8026baef0c7a9b4cb668bbed1c8b0b8c99435bd0afde20017215e`.
- `config/printer.cfg` — đổi include sang
  `Printer-Setup/tool_vision.cfg`.
- `config/moonraker.conf` — thay include sinh tự động bằng một section
  `[update_manager tool-vision]` trực tiếp; giữ nguyên runtime, venv, origin,
  branch, requirements và managed services đang hoạt động.
- `config/scripts/install.sh` — bỏ bảo vệ toàn bộ thư mục `Tool-Vision/`, bỏ
  copy riêng file cfg và neo hai exclude JSON legacy vào root để không giữ nhầm
  file cùng tên trong thư mục backup con.
- `config/toolchanger/toolchanger-config.cfg` — cập nhật comment owner/path.
- `README.md`, `config/README.md`,
  `extras/docs/huong-dan-he-thong-stealthchanger.md` — cập nhật cấu trúc, quy
  trình triển khai và version production `3.3.0-rc1`/commit `5e79f63`.
- `.agents/DIRECTORY.md`, `.agents/DECISIONS.md` — ghi nhớ layout mới và quy
  tắc tuyệt đối không nhầm/xóa runtime `~/Tool-Vision`.

### Sao lưu

- [Backup PC](<file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-consolidate-toolvision-config-20260822-184504/>).
- Snapshot đầy đủ máy thật trước thay đổi:
  `/home/voron/printer_data/config_backups/pre-consolidate-toolvision-config-20260822-184504/`
  (40 file, có `SHA256SUMS`).
- Backup tự động khi installer chạy:
  `/home/voron/printer_data/config_backups/config-install-20260822-184951/`.
- Bản legacy vẫn phục hồi được tại
  `/home/voron/printer_data/config_backups/tool-vision/manual-20260822-180254/`.

### Triển khai và dọn dữ liệu

- Xác nhận trước triển khai: printer standby, không pause, bed target 0,
  ToolVision không busy; cả ba service active.
- Payload staging được sửa mode, kiểm tra Bash và đối chiếu hash trên Linux.
- Chạy `config/scripts/install.sh` đúng một lần. Hai rule exclude JSON cũ khiến
  rsync giữ lại hai file trong backup con; sau khi so khớp lại với bản ngoài
  config, dùng `unlink` đúng hai file và `rmdir` từng thư mục rỗng, không dùng
  xóa đệ quy.
- `/config/Tool-Vision` đã được loại bỏ hoàn toàn. Runtime
  `/home/voron/Tool-Vision`, venv, service, symlink và `Generated-Data` được giữ.
- Gửi yêu cầu migration installer/tests/docs vào task Codex của repository
  `D:\Desktop\Tool-Vision` để lần cài sau không tái tạo layout cũ.

### Kiểm tra

- `bash -n` cho `install.sh` và `update.sh`: đạt trên máy Linux.
- `git diff --check`: đạt.
- `moonraker.conf`: đúng một `[update_manager]`, đúng một
  `[update_manager tool-vision]`, không có section trùng.
- Hash bốn file production `tool_vision.cfg`, `printer.cfg`, `moonraker.conf`,
  `install.sh` khớp giữa PC và máy thật.
- Moonraker sau restart: không warning/failed component; Klipper `ready`.
- Klipper, Moonraker, ToolVision: active; ToolVision API `ok=true`, version
  `3.3.0-rc1`, switch vẫn ready, không busy và không có last error.
- State/result còn nguyên dưới `Generated-Data/ToolVision/`; không còn thư mục
  vật lý `/config/Tool-Vision`.
- Update Manager nhận repository `tool-vision` hợp lệ, pristine, không dirty,
  không chậm commit. Version đang hiển thị `?` do tag backup ảnh hưởng
  `git describe`; vấn đề metadata/tag đã được gửi bổ sung sang task ToolVision.

### Kết quả

Mainsail chỉ còn file cấu hình ToolVision trong `Printer-Setup` và updater trong
`moonraker.conf`; thư mục cấu hình ToolVision riêng cùng backup legacy đã được
dọn an toàn. Runtime ngoài config vẫn hoạt động và có thể cập nhật độc lập.

### Vấn đề còn lại

- Chờ task ToolVision hoàn tất migration installer và sửa version metadata để
  reinstall/update không tái tạo layout cũ và Mainsail hiển thị version đúng.
- Camera ToolVision vẫn chưa setup; không liên quan đến thay đổi layout này.

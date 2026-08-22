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

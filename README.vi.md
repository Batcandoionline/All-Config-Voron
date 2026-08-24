# Cấu hình production Voron 2.4 StealthChanger năm tool

[English](README.md) | [Tiếng Việt](README.vi.md) | [Chỉ mục tài liệu](extras/docs/README.vi.md)

Repository này là bộ cấu hình và payload triển khai đã review cho một máy
Voron 2.4 CoreXY 350 mm với năm tool StealthChanger. Đây không phải cấu hình mẫu
dùng chung. Các mã phần cứng, giới hạn chuyển động, vị trí dock và offset bên
dưới được đọc từ cấu hình được Git theo dõi tại commit `9d848f04`, ngày
2026-08-24.

Nhãn trạng thái dùng trong tài liệu:

- **Đang hoạt động:** được `config/printer.cfg` nạp.
- **Đã quan sát:** đã xác nhận trong một phiên làm việc với máy, không phải tuyên
  bố đúng cho mọi phần cứng.
- **Đang phát triển:** đã cài đặt ở nhánh/dự án khác nhưng chưa triển khai lên
  máy này nếu không ghi rõ.

## Hệ thống đang hoạt động

| Hạng mục | Cấu hình được theo dõi |
| --- | --- |
| Máy in | Voron 2.4, CoreXY, X `0..348`, Y `-10..336`, tốc độ tối đa `300 mm/s`, gia tốc tối đa `4000 mm/s²` |
| Bộ điều khiển | BTT Manta M8P V2.0 với CM4; CAN UUID chính `19b203d75137` |
| Toolchanger | KTC-Easy StealthChanger, T0–T4; dock sau ở Z `343 mm` |
| Board tool | Năm BTT EBB36 trên CAN, mỗi tool có extruder/heater/fan/cảm biến filament riêng |
| Z và mesh | Cartographer V3, CAN UUID `da13d909ce34`; Touch lấy mốc Z và adaptive scan mesh |
| Đo offset tool | ToolVision development canary, chỉ báo cáo; switch vật lý ở chân Manta `^PF2` |
| Bed/chamber | Bed AC 1000 W qua SSR `PA1`, cảm biến bed `PB0`, cảm biến chamber `PB1` |
| Vệ sinh nozzle | Purge bucket và pad silicone Bambu A1 |
| UI/slicer | Mainsail, KlipperScreen tiếng Việt, profile OrcaSlicer toolchanger |

KTC-Easy là thành phần duy nhất sở hữu
`config/toolchanger/readonly-configs/`. Repository này chỉ sở hữu override KTC
và định nghĩa T0–T4 có thể sửa. Installer sẽ từ chối tiếp tục nếu sáu symlink
readonly do KTC-Easy tạo bị thiếu hoặc hỏng.

## Sơ đồ tool và offset đã thử nghiệm in

Người vận hành đánh giá first layer hiện tại tốt về hình thức. Vì vậy các giá
trị này là baseline production, không phải giá trị để ghi đè từ một lần đo chẩn
đoán.

| Tool | CAN UUID | Dock XY tại Z 343 | Offset X | Offset Y | Offset Z |
| --- | --- | --- | ---: | ---: | ---: |
| T0 | `441e1484ac41` | `30.20, 1.30` | `0.000` | `0.000` | `0.000` |
| T1 | `6475b5b9e028` | `104.00, 1.10` | `-0.243` | `-0.252` | `+0.228` |
| T2 | `4ad9d622a836` | `176.00, 1.60` | `+0.746` | `+0.086` | `-0.295` |
| T3 | `c2465b7c36f8` | `249.50, 2.50` | `+0.304` | `+0.449` | `-0.268` |
| T4 | `28650279df58` | `321.50, 2.60` | `+0.041` | `+0.352` | `-0.014` |

Nguồn offset là khối `SAVE_CONFIG` trong `config/printer.cfg`. Pin CAN, rotation
distance, đường dock và profile input shaper riêng nằm trong
`config/toolchanger/tools/T0.cfg` đến `T4.cfg`.

## Thứ tự cấu hình đang được nạp

`config/printer.cfg` nạp theo thứ tự:

1. Mainsail và include do KTC-Easy quản lý.
2. Routing Cartographer/calibration và ToolVision.
3. Hardware, fan/LED, input shaper, vệ sinh nozzle, prime line và print macro.
4. Tool-crash sau các định nghĩa tool do KTC-Easy cung cấp.

Axiscope và `[tools_calibrate]` chỉ còn là nội dung rollback đã comment trong
`calibration-probe.cfg`; cả hai section đều không hoạt động. Cartographer là
probe production cho Z/mesh. ToolVision sở hữu PF2 để đo offset tool chẩn đoán
có người giám sát.

## Quy trình in thực sự trong code

`PRINT_START` kiểm tra tham số slicer, dừng trạng thái dryer/crash cũ, bắt đầu
gia nhiệt bed và tool bất đồng bộ, home toàn bộ trục trước khi chọn tool, vệ sinh
T0, đợi bed, thực hiện heat soak tùy chênh lệch nhiệt, chạy QGL, vệ sinh T0 lần
nữa, home bằng Cartographer Touch, tạo adaptive mesh và prime mọi tool được
slicer sử dụng. Tool bắt đầu được prime cuối cùng; crash detection chỉ bật sau
khi khâu chuẩn bị hoàn tất.

Mặc định heat soak tự động đọc từ `print-macros.cfg`:

| Nhóm vật liệu | Soak khi bed lạnh |
| --- | ---: |
| PLA/TPU | 30 giây |
| PETG | 60 giây |
| ABS/ASA/PC/NYLON/PA | 90 giây |

Khi bed cách target không quá 5 °C, bỏ qua soak tự động. Chênh lệch 5–15 °C
dùng 20% thời gian. `SOAK=` ghi đè thời gian; `AUTO_SOAK=0` tắt tính tự động.

`PRINT_END` dừng crash detection, tắt heater/fan thuộc job in, thả tool đang
gắn và park shuttle rỗng. Code **không** hứa kết thúc với T0 đang gắn.

Các macro bảo trì công khai gồm `CLEAN_NOZZLE`, `PURGE_AND_CLEAN`,
`PRIME_LINES`, `CALIBRATION_STATUS`, `CHECK_OFFSETS`, `START_DRYER`,
`STOP_DRYER` và `DRYER_STATUS`.

## ToolVision trên máy này

Tích hợp đã deploy là development canary được giám sát:

- Runtime checkout: `~/Tool-Vision`
- Môi trường Python riêng: `~/tool-vision-env`
- Host service: `tool-vision.service`, API loopback cổng `8085`
- Cấu hình riêng của máy: `config/Printer-Setup/tool-vision.cfg`
- Learned state: `~/printer_data/config/Generated-Data/ToolVision/state.json`
- Kết quả mới nhất: `~/printer_data/config/Generated-Data/ToolVision/results.json`

Panel riêng đang được theo dõi vẫn dùng bố cục Setup/Calibrate chung. Z bằng
switch PF2 và Z bằng Cartographer Touch đều đã được quan sát trên phần cứng thật
ngày 2026-08-23. Camera XY có trong ToolVision nhưng chưa được teach cho lần
triển khai repository này. Mọi kết quả chỉ để chẩn đoán; ToolVision không ghi
offset production T0–T4.

Nhánh ToolVision mới `codex/z-calibration-ux` tại `2d936f3` đã cài đặt nút Z
theo từng method, `VERBOSITY=QUIET`, nhãn `NOT APPLIED` rõ ràng và lịch sử giới
hạn 20 record. Tài liệu test của ToolVision ghi rõ nhánh này mới có bằng chứng
component/fake, chưa deploy hoặc HIL trên máy production. Xem
[trạng thái triển khai](extras/docs/toolvision-z-calibration-ux-proposal.vi.md).

Để xem tích hợp hiện tại và các kiểm tra không chuyển động, dùng
[hướng dẫn tiếng Việt](extras/docs/toolvision-integration-guide.vi.md) hoặc
[hướng dẫn tiếng Anh](extras/docs/toolvision-integration-guide.en.md).

## Preset sấy filament trên bed

`START_DRYER` từ chối chạy khi đang in và có thể home/dock/park nếu người vận
hành yêu cầu. Preset trong `print-macros.cfg` là:

| Vật liệu | Bed | Chamber | Thời gian | Fan nền |
| --- | ---: | ---: | ---: | ---: |
| PLA | 50 °C | 40 °C | 240 phút | 40% |
| TPU | 60 °C | 45 °C | 300 phút | 40% |
| PETG | 70 °C | 55 °C | 240 phút | 50% |
| ABS/ASA | 90 °C | 65 °C | 240 phút | 60% |
| NYLON | 100 °C | 70 °C | 360 phút | 70% |
| PC | 105 °C | 75 °C | 360 phút | 70% |

Tham số tường minh có thể ghi đè preset. `CUSTOM` mặc định bed 55 °C, 240 phút
và fan 40%; không có chamber target nếu người dùng không cung cấp.

## Bố cục repository

```text
Voron 5 Tool/
├── README.md / README.vi.md
├── config/
│   ├── printer.cfg
│   ├── Printer-Setup/
│   ├── toolchanger/
│   └── scripts/
├── Orca Config/
└── extras/
    ├── docs/
    ├── Nhat-ky-chinh-sua/
    ├── backups/
    └── retired-configs/
```

Tài liệu hiện hành và các bản dịch được liệt kê trong
[`extras/docs/README.vi.md`](extras/docs/README.vi.md). Nhật ký lịch sử và
snapshot backup là bằng chứng bất biến; không viết lại chúng để trông giống hệ
thống hiện tại.

## Cài đặt và cập nhật

Cài KTC-Easy trước khi máy idle. Để deploy All-Config lần đầu mà không giữ thêm
Git checkout trên CM4:

```bash
tmp_dir="$(mktemp -d /tmp/all-config-voron.XXXXXX)"
curl -fsSL https://github.com/IDcrazy123/All-Config-Voron/archive/refs/heads/main.tar.gz \
  | tar -xz -C "${tmp_dir}" --strip-components=1
bash "${tmp_dir}/config/scripts/install.sh"
rm -rf -- "${tmp_dir}"
sudo systemctl restart moonraker klipper
```

Các lần cập nhật sau:

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart moonraker klipper
```

`update.sh` tải archive tạm của nhánh `main` rồi gọi `install.sh`. Installer
preflight KTC-Easy, ToolVision và patch tool-crash đã review, tạo bản sao có
timestamp trong `~/printer_data/config_backups/`, rồi deploy các file do
repository sở hữu. Nó loại Markdown, `Generated-Data/`, chẩn đoán local và thư
mục readonly của KTC-Easy. Hai script không tự restart service.

`cleanup-voron.sh` chỉ dry-run/apply các đường dẫn legacy
`config.update-backup-*`, `config.backup-*` và `~/axiscope.bak` sau khi review.
Script không cung cấp retention tổng quát cho `config_backups/`.

## Quy tắc an toàn và đóng góp

- Không sửa `config/toolchanger/readonly-configs/` trong repository này.
- Không deploy, home, toolchange, probe hoặc calibration trong lúc đang in.
- Sao lưu cấu hình được theo dõi trước khi sửa `.cfg`, `.conf` hoặc `.sh`.
- Không đưa dữ liệu sinh trên máy in hoặc credential vào Git.
- Xem kết quả ToolVision là ứng viên chỉ báo cáo cho đến khi đã lặp trong cùng
  điều kiện và xác nhận độc lập bằng bản in hoặc phương pháp được duyệt.
- Giữ nguyên nhật ký lịch sử và snapshot backup; thêm bằng chứng mới thay vì
  viết lại bằng chứng cũ.

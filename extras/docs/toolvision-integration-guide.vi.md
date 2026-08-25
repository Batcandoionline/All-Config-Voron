# Tích hợp ToolVision — máy Voron năm tool riêng

[English](toolvision-integration-guide.en.md) | [Tiếng Việt](toolvision-integration-guide.vi.md)

## Phạm vi đã xác minh

Tài liệu này mô tả tích hợp trong All-Config, không tuyên bố mọi khả năng của
repository ToolVision độc lập. Source và bằng chứng máy được cập nhật tới
2026-08-25 theo:

- worktree All-Config hiện tại và cấu hình live đã được backup;
- nhánh ToolVision `codex/compact-mainsail-output` tại `dd645103`, version
  `3.4.0-rc2`;
- GitHub Security Gate, render prompt Mainsail thật và HIL hai phương pháp có
  người giám sát trên máy năm tool riêng.

ToolVision vẫn chỉ báo cáo. Nó đo offset tương đối ứng viên và không gọi
`SAVE_CONFIG` hoặc ghi offset production T0–T4.

## Quyền sở hữu runtime và dữ liệu

| Đường dẫn | Thành phần sở hữu | Mục đích hiện tại |
| --- | --- | --- |
| `~/Tool-Vision/` | ToolVision/Moonraker Git updater | Source host và Klipper extension |
| `~/tool-vision-env/` | Installer ToolVision | Môi trường Python riêng cho host |
| `/etc/systemd/system/tool-vision.service` | Installer ToolVision | Host API chỉ loopback |
| `Printer-Setup/tool-vision.cfg` | All-Config | PF2, đường JSON và panel Mainsail hiện tại |
| `Generated-Data/ToolVision/state.json` | Runtime ToolVision | Station/method đã học |
| `Generated-Data/ToolVision/results.json` | Runtime ToolVision | Kết quả success mới nhất tương thích ngược |

`Generated-Data/` bị loại khỏi Git và `rsync --delete` của All-Config, nên cập
nhật cấu hình không xóa state hoặc result đã học.

Thư mục history bất biến đang deploy nằm cùng parent của result đã cấu hình:

```text
Generated-Data/ToolVision/tool-vision-history/
```

`results.json` tiếp tục là kết quả mới nhất tương thích ngược; mỗi session hoàn
tất hoặc lỗi cũng ghi một history có ngày và tên method.

## Cấu hình máy đang hoạt động

`printer.cfg` nạp:

```ini
[include Printer-Setup/tool-vision.cfg]
```

Section riêng của máy:

```ini
[tool_vision]
pin: ^PF2
state_file: ~/printer_data/config/Generated-Data/ToolVision/state.json
result_file: ~/printer_data/config/Generated-Data/ToolVision/results.json
toolchanger_recovery_gcode:
  INITIALIZE_TOOLCHANGER
```

Hook recovery đã được review cho máy KTC Easy này. Đây không phải default dùng
chung và không được sao chép sang toolchanger khác nếu chưa xác minh hành vi
initialize tại các vị trí calibration có thể lỗi.

Method switch vật lý cần `tools_calibrate.py` do KTC-Easy cài, nhưng section
`[tools_calibrate]` phải tiếp tục tắt khi `[tool_vision]` hoạt động. Axiscope
cũng đã tắt. Cartographer vẫn là probe production cho Z/mesh.

ToolVision có camera discovery, nhưng file All-Config không đặt camera
source/name và trạng thái máy đã ghi camera setup chưa ready. Không mô tả camera
XY là đang hoạt động trước khi có setup giám sát và bằng chứng mới.

## UI hiện đang deploy

Canary runtime `dd645103` và panel All-Config đã được deploy, HIL có người giám
sát ngày 2026-08-25. Trang chính hiện chỉ gồm:

- `Measure Z - Physical switch`;
- `Measure Z - Cartographer Touch`;
- `Latest results`;
- `Advanced setup` và `Close`.

Mỗi action Z truyền rõ `METHOD=` và `VERBOSITY=QUIET`. Teach station vẫn có thể
đổi default đã lưu nhưng không thể âm thầm đổi phương pháp của hai nút Z đã đặt
tên. `Latest results` lấy method/mode từ record session cuối, giữ đúng drift
`0.0` và luôn ghi `NOT APPLIED`.

Mở panel hiện sinh tám response thay vì mười một. Quiet mode giới hạn chính
ToolVision còn ba message cho mỗi calibration thành công; dòng chờ heater,
toolchange KTC, tiếp xúc switch và Cartographer thuộc các component đó nên vẫn
hiển thị. Không dùng regex để ẩn `action:prompt_*`, warning hoặc error.

## Quy trình cập nhật an toàn

Cập nhật All-Config khi máy idle:

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

Installer kiểm tra checkout ToolVision, Python riêng, systemd unit và năm
symlink module Klipper chính xác trước khi deploy include. Nó cũng kiểm tra sáu
symlink readonly của KTC-Easy và tạo snapshot cấu hình. Script không tự restart.

Sau khi đọc output:

```bash
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

Canary hiện theo nhánh `codex/compact-mainsail-output`. Refresh metadata của
Moonraker trước update để cache remote thấy commit đã review. Không chạy
`git pull` trực tiếp và không chuyển máy khác sang development channel này nếu
chưa có backup cùng kế hoạch HIL có người giám sát riêng.

## Kiểm tra không chuyển động

Trên host:

```bash
systemctl is-active tool-vision moonraker klipper
curl --fail --silent http://127.0.0.1:8085/api/v2/health
```

Trong Mainsail:

```text
CALIBRATION_STATUS
QUERY_ENDSTOPS
TOOL_VISION_STATUS
```

Trước phép đo, mong đợi:

- Klipper ready và printer idle.
- ToolVision không busy, không có last error chưa giải thích.
- `ToolVision switch` thường open khi PF2 không bị nhấn.
- Mọi heater target bằng 0.
- State/result vẫn ở `Generated-Data/ToolVision/`.

Các kiểm tra này không chủ động home, heat, probe hoặc đổi tool. Mở macro
`TOOL_VISION` chỉ mở prompt; action Setup/Calibrate có thể làm máy chuyển động
và nóng.

## Đọc kết quả Z

Dấu đã cài đặt là:

```text
measured Z(tool) = raw contact Z(tool) - raw contact Z(reference)
```

Xem giá trị là offset absolute ứng viên tương đối T0, không phải correction để
cộng vào offset đang cấu hình. Khi so run phải giữ cùng method và nhiệt độ. T0
return drift là evidence chẩn đoán; ToolVision chưa có ngưỡng drift pass/fail
phổ quát.

Ngày 2026-08-25, ba run hợp lệ ở 150 °C cho mỗi phương pháp đã hoàn tất, với
`G28` đầy đủ trước từng run. Mean ứng viên T1–T4:

| Phương pháp | T1 | T2 | T3 | T4 | Mean drift T0 trở về |
| --- | ---: | ---: | ---: | ---: | ---: |
| Switch vật lý PF2 | +0.121 | -0.385 | -0.179 | +0.093 | +0.033 |
| Cartographer Touch | +0.243 | -0.268 | -0.186 | +0.105 | +0.011 |

Cartographer trừ PF2 lần lượt là `+0.121`, `+0.117`, `-0.007` và `+0.011 mm`
cho T1–T4. Hai phương pháp đều lặp lại tốt trong nội bộ, nhưng sai khác hệ thống
T1/T2 nghĩa là không được lấy trung bình hoặc áp kết quả khi chưa điều tra cơ
khí thêm. Tất cả run chỉ report và được giữ trong history có ngày; offset
production không đổi.

## Backup và rollback

Snapshot All-Config dùng:

```text
~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/
```

Ba backup máy được giữ rõ ràng sau lần dọn 2026-08-23 đã được ghi trong nhật ký
bất biến ngày đó. Script không cưỡng chế chính sách tổng quát “giữ N bản mới”.

Trước khi đổi runtime/schema ToolVision hoặc teach lại station, sao lưu riêng:

- `Printer-Setup/tool-vision.cfg`;
- `Generated-Data/ToolVision/state.json`;
- `Generated-Data/ToolVision/results.json`;
- `Generated-Data/ToolVision/tool-vision-history/` trong tương lai nếu tồn tại;
- commit hash ToolVision và trạng thái service.

Không xóa generated data khi chỉ rollback layout All-Config. Chỉ restore
state/result khi chính dữ liệu đó là mục tiêu rollback và schema tương thích
runtime được chọn.

## Xử lý sự cố

- **Unknown section `tool_vision`:** kiểm tra năm symlink extension rồi restart
  Klipper lúc máy idle.
- **Không thấy include:** kiểm tra đúng hoa/thường
  `Printer-Setup/tool-vision.cfg`.
- **Có vẻ mất setup:** kiểm tra `Generated-Data/ToolVision/state.json` trước khi
  teach lại.
- **Latest result ghi sai method hoặc biến drift `0.0` thành `n/a`:** cập nhật
  `dd645103` hoặc mới hơn, đồng bộ panel tương ứng, restart Klipper rồi kiểm tra
  lại `Latest results` không chuyển động.
- **Console quá nhiều dòng:** xác nhận action UI truyền `VERBOSITY=QUIET`.
  ToolVision khi đó chỉ sở hữu ba message calibration; log KTC, heater, probe
  và Cartographer được chủ ý giữ lại.
- **KTC chuyển uninitialized sau nested command error:** máy này dùng hook
  `INITIALIZE_TOOLCHANGER` đã review. Phải xác nhận tool đang physically
  detected trước khi bật hook tương tự trên máy khác.
- **Preflight deploy lỗi:** sửa runtime/symlink/quyền sở hữu KTC được nêu; không
  bypass.

# Tích hợp ToolVision — máy Voron năm tool riêng

[English](toolvision-integration-guide.en.md) | [Tiếng Việt](toolvision-integration-guide.vi.md)

## Phạm vi đã xác minh

Tài liệu này mô tả tích hợp trong All-Config, không tuyên bố mọi khả năng của
repository ToolVision độc lập. Source được đọc lại ngày 2026-08-24 theo:

- cấu hình máy đã deploy tại commit `9d848f04`;
- development-canary đã ghi nhận trên máy tại commit ToolVision `2b3bf2c6`,
  version `3.4.0-rc1`;
- nhánh UX mới chưa deploy `codex/z-calibration-ux` tại `2d936f3`.

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

Khi implementation history mới được review và deploy, thư mục mặc định sẽ nằm
cùng parent của result đã cấu hình:

```text
Generated-Data/ToolVision/tool-vision-history/
```

Sự xuất hiện của đường dẫn trong tài liệu **không** chứng minh runtime production
hiện đã có history. Runtime `2b3bf2c6` được ghi nhận chỉ giữ `results.json`.

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
```

Method switch vật lý cần `tools_calibrate.py` do KTC-Easy cài, nhưng section
`[tools_calibrate]` phải tiếp tục tắt khi `[tool_vision]` hoạt động. Axiscope
cũng đã tắt. Cartographer vẫn là probe production cho Z/mesh.

ToolVision có camera discovery, nhưng file All-Config không đặt camera
source/name và trạng thái máy đã ghi camera setup chưa ready. Không mô tả camera
XY là đang hoạt động trước khi có setup giám sát và bằng chứng mới.

## UI hiện tại và UI đang phát triển

Panel All-Config đã deploy gom Setup và Calibrate, dùng nút Z/XYZ chung. Teach
Switch hoặc Cartographer làm đổi default method đã lưu; action `MODE=Z` chung
sẽ dùng state đó. Luôn đọc method panel hiển thị trước chuyển động.

Nhánh ToolVision `2d936f3` đã cài đặt nhưng chưa deploy production:

- action riêng `Measure Z - Physical switch` và `Measure Z - Cartographer
  Touch`;
- tách Advanced Setup khỏi đo thường xuyên;
- UI luôn truyền `METHOD=` cho run Z;
- `VERBOSITY=QUIET` giảm message do ToolVision sở hữu;
- history bất biến có tên method, retention cố định 20;
- metadata cuối `NOT APPLIED` và `Configuration changed: No`.

Test hiện là bằng chứng L0–L2/component/fake. Tài liệu ToolVision ghi Mainsail,
simulator và HIL trên máy vẫn chưa thực hiện. Xem
[báo cáo trạng thái triển khai](toolvision-z-calibration-ux-proposal.vi.md).

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

Không cập nhật runtime ToolVision lên `2d936f3` chỉ vì tài liệu này mô tả nó.
Đây không phải nhánh `main` của updater; deploy sẽ đổi điều phối Klipper và lưu
result, nên cần backup, review và kế hoạch HIL có người giám sát riêng.

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

Ngày 2026-08-23, một run PF2 150 °C và một run Cartographer Touch 150 °C hoàn
tất. Cả hai đưa máy về idle an toàn với heater target 0, nhưng run thứ hai ghi
đè `results.json` của run đầu. Offset production đã thử nghiệm in không bị đổi.
Giá trị được giữ trong
[báo cáo trạng thái UX](toolvision-z-calibration-ux-proposal.vi.md).

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
- **Run PF2 mới nhất biến mất sau Cartographer:** đây là hành vi runtime
  `2b3bf2c6`; khôi phục evidence từ log gốc, không tự tạo JSON.
- **Console quá nhiều dòng:** UI production hiện chưa truyền quiet mode. Phần
  giảm log chỉ có trong nhánh `2d936f3` chưa deploy.
- **Preflight deploy lỗi:** sửa runtime/symlink/quyền sở hữu KTC được nêu; không
  bypass.

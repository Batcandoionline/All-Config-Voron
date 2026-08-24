# Hướng dẫn tích hợp ToolVision — Bản cài Voron riêng

[English](toolvision-integration-guide.en.md) | [Tiếng Việt](toolvision-integration-guide.vi.md)

## Phạm vi

Tài liệu này mô tả cách tích hợp ToolVision dành riêng cho máy Voron 2.4 năm
tool. ToolVision là runtime độc lập; repository này chỉ quản lý cấu hình Klipper
riêng của máy, các kiểm tra an toàn khi deploy và quy tắc đặt dữ liệu.

ToolVision chỉ báo cáo kết quả. Nó đo các giá trị XYZ ứng viên và độ trôi của
tool tham chiếu, nhưng không tự ghi đè offset production.

## Quyền sở hữu đường dẫn

| Đường dẫn | Thành phần quản lý | Mục đích |
| --- | --- | --- |
| `~/Tool-Vision/` | Git checkout ToolVision | Host service và source Klipper extension |
| `~/tool-vision-env/` | Installer ToolVision | Môi trường Python độc lập |
| `/etc/systemd/system/tool-vision.service` | Installer ToolVision | Host API chỉ lắng nghe loopback |
| `~/printer_data/config/Printer-Setup/tool-vision.cfg` | All-Config | Pin riêng của máy, đường dẫn JSON và panel Mainsail |
| `~/printer_data/config/Generated-Data/ToolVision/state.json` | Runtime ToolVision | Station đã teach và method đang chọn |
| `~/printer_data/config/Generated-Data/ToolVision/results.json` | Runtime ToolVision | Báo cáo phép đo hoàn tất gần nhất |

Mọi JSON do ToolVision sinh ra sau này trên máy này phải nằm trong
`Generated-Data/ToolVision/`. Không đặt dữ liệu sinh tự động cạnh `printer.cfg`
hoặc trong `Printer-Setup/`.

Toàn bộ cây `Generated-Data/` được Git bỏ qua và installer loại khỏi
`rsync --delete`. Vì vậy cập nhật All-Config không xóa station đã teach hoặc kết
quả đo.

## Cấu hình tích hợp bắt buộc

Include đang hoạt động trong `printer.cfg` là:

```ini
[include Printer-Setup/tool-vision.cfg]
```

Cấu hình riêng của máy gán switch ToolVision vào chân Manta M8P `^PF2` và chỉ
rõ vị trí dữ liệu runtime:

```ini
[tool_vision]
pin: ^PF2
state_file: ~/printer_data/config/Generated-Data/ToolVision/state.json
result_file: ~/printer_data/config/Generated-Data/ToolVision/results.json
```

Trước khi deploy include này, `config/scripts/install.sh` kiểm tra Git checkout
ToolVision, Python độc lập, systemd unit và đủ năm symlink Klipper extension.
Installer cũng giữ nguyên thư mục `toolchanger/readonly-configs/` do KTC-Easy
quản lý.

## Quy trình cập nhật an toàn

Chỉ cập nhật khi máy đang idle. Không thực hiện lúc đang in, đang pause,
ToolVision đang chạy job hoặc đang calibration có người giám sát.

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

Updater tải archive nhánh `main` đã review, gọi installer có backup trước,
deploy các file do repository quản lý rồi xóa archive tạm. Updater không tự
restart service.

Sau khi đọc và xác nhận output của installer, restart Moonraker trước rồi
Klipper sau:

```bash
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

Thay đổi bố cục file này không cần home, probe, toolchange hoặc bật heater.

## Kiểm tra không chuyển động

Kiểm tra service và trạng thái Klipper:

```bash
systemctl is-active tool-vision.service moonraker klipper
```

Trong console Mainsail, chạy:

```text
TOOL_VISION_STATUS
QUERY_ENDSTOPS
```

Kết quả mong đợi:

- Klipper `ready`, máy in `standby`.
- ToolVision báo `busy=false` và không có last error.
- `ToolVision switch` thường là `open` khi không có gì đè PF2.
- Target của mọi heater vẫn là `0`, trừ khi người vận hành chủ động bắt đầu
  calibration.
- `state.json` và `results.json` vẫn nằm dưới
  `Generated-Data/ToolVision/`.

Mở macro Mainsail `TOOL_VISION` chỉ hiển thị panel. Các nút Setup và Calibration
có thể làm máy chuyển động nên vẫn phải có người giám sát.

## Lưu ý về Z method

ToolVision có thể lưu `switch` hoặc `cartographer_touch` làm Z method đang chọn.
Teach một method có thể thay method trong `state.json`. Luôn kiểm tra method đang
hiển thị trước khi bắt đầu đo Z.

Z được báo cáo là giá trị đo tương đối so với tool tham chiếu. Hãy xem đó là
giá trị absolute tương đối ứng viên, không phải correction delta để cộng vào
offset production. Nên lặp lại cùng method và nhiệt độ ít nhất ba lần trước khi
đánh giá điều chỉnh bản in thủ công theo bước `0.01 mm`.

## Backup và rollback

Mỗi lần deploy tạo một snapshot có timestamp tại:

```text
~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/
```

Để rollback thay đổi bố cục này, phục hồi `printer.cfg`, file
`tool_vision.cfg` cũ ở root và `scripts/install.sh` từ snapshot tương ứng, sau
đó restart Moonraker và Klipper khi máy idle. Không phục hồi hoặc xóa
`Generated-Data/ToolVision/` trừ khi chính learned state là mục tiêu rollback.

## Xử lý sự cố

- **Unknown section `tool_vision`:** kiểm tra đủ năm symlink Klipper extension
  và restart Klipper sau khi cài runtime.
- **Không tìm thấy include:** xác nhận đúng đường dẫn phân biệt hoa/thường
  `Printer-Setup/tool-vision.cfg`.
- **Có vẻ mất setup:** kiểm tra `Generated-Data/ToolVision/state.json` tồn tại
  và user `voron` đọc được trước khi teach lại.
- **Không có kết quả mới nhất:** kiểm tra
  `Generated-Data/ToolVision/results.json` và `TOOL_VISION_STATUS`; không tự tạo
  JSON rỗng.
- **Preflight từ chối deploy:** sửa đúng runtime, symlink hoặc quyền sở hữu
  KTC-Easy được báo lỗi. Không bỏ qua kiểm tra.

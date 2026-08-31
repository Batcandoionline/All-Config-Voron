# Payload cấu hình Klipper đang hoạt động

[English](README.md) | [Tiếng Việt](README.vi.md)

Thư mục này được triển khai vào `~/printer_data/config` bằng
`scripts/install.sh` và `scripts/update.sh`. Markdown chỉ là tài liệu và bị loại
khỏi payload triển khai.

## Quyền sở hữu và hợp đồng include

`printer.cfg` hiện nạp:

```ini
[include mainsail.cfg]
[include toolchanger/readonly-configs/toolchanger-include.cfg]
[include Printer-Setup/calibration-probe.cfg]
[include Printer-Setup/ktamv.cfg]
[include Printer-Setup/hardware.cfg]
[include Printer-Setup/fans-leds.cfg]
[include Printer-Setup/input-shaper.cfg]
[include Printer-Setup/nozzle-clean.cfg]
[include Printer-Setup/prime-lines.cfg]
[include Printer-Setup/print-macros.cfg]
[include Printer-Setup/tool-crash.cfg]
```

KTC-Easy sở hữu toàn bộ file trong `toolchanger/readonly-configs/`. Không sửa,
thay hoặc chép file thường vào thư mục này. All-Config sở hữu
`toolchanger/toolchanger-config.cfg`, `toolchanger/tools/T*.cfg` và các override
trong `Printer-Setup/`.

## Sơ đồ thư mục

```text
config/
├── printer.cfg
├── mainsail.cfg
├── moonraker.conf
├── crowsnest.conf
├── KlipperScreen.conf
├── Printer-Setup/
│   ├── calibration-probe.cfg
│   ├── ktamv.cfg
│   ├── hardware.cfg
│   ├── fans-leds.cfg
│   ├── input-shaper.cfg
│   ├── nozzle-clean.cfg
│   ├── prime-lines.cfg
│   ├── print-macros.cfg
│   └── tool-crash.cfg
├── toolchanger/
│   ├── toolchanger-config.cfg
│   ├── tools/T0.cfg ... T4.cfg
│   └── readonly-configs/       # symlink do KTC-Easy sở hữu
└── scripts/
    ├── install.sh
    ├── update.sh
    ├── cleanup-voron.sh
    └── patches/
```

## Sơ đồ phần cứng xác nhận từ source

| Thành phần | Giá trị đang hoạt động |
| --- | --- |
| MCU chính | Manta M8P V2.0, CAN UUID `19b203d75137` |
| Cartographer | CAN UUID `da13d909ce34`, offset X `0`, Y `35` |
| Endstop X/Y | `PF0` / `PF1`; Y tối thiểu `-10` |
| Pin step Z | `PG9`, `PB4`, `PG13`, `PB8` |
| Bed | heater `PA1`, sensor `PB0`, tối đa 120 °C |
| Sensor chamber | Generic 3950 tại `PB1` |
| Fan dưới bed | `PF8` |
| LED chamber | WS2812 tại `PD15` |
| Switch tool-offset không active | Manta `^PF2` với GND; kTAMV không dùng |

CAN UUID, dock và offset production của năm tool được ghi trong
[README gốc](../README.vi.md), còn giá trị thực nằm trong `toolchanger/tools/`
và khối `SAVE_CONFIG` của `printer.cfg`.

## Quyền sở hữu calibration

- Cartographer Touch dùng để home Z production.
- Cartographer Scan tạo adaptive bed mesh. Mesh cấu hình từ X `20..320`,
  Y `45..325` với 55 × 55 mẫu.
- kTAMV được nạp từ `Printer-Setup/ktamv.cfg` để đối chiếu X/Y có giám sát. Nó
  không đo Z, không lưu offset và mất camera/origin sau Klipper restart.
- Axiscope và `[tools_calibrate]` chỉ là nội dung rollback đã comment trong
  `calibration-probe.cfg`, không phải backend hoạt động.
- Runtime kTAMV được pin tại commit upstream `72421f2`, chạy user service cổng
  `8086`, tắt cloud upload và có patch nhiều vật thể đã review.

Toàn bộ `Generated-Data/` bị loại khỏi Git deployment và `rsync --delete`.

## Hành vi triển khai

Cài lần đầu mà không giữ All-Config checkout trên CM4:

```bash
tmp_dir="$(mktemp -d /tmp/all-config-voron.XXXXXX)"
curl -fsSL https://github.com/IDcrazy123/All-Config-Voron/archive/refs/heads/main.tar.gz \
  | tar -xz -C "${tmp_dir}" --strip-components=1
bash "${tmp_dir}/config/scripts/install.sh"
rm -rf -- "${tmp_dir}"
sudo systemctl restart moonraker klipper
```

Cập nhật lần sau:

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart moonraker klipper
```

`install.sh` kiểm tra trước khi deploy:

1. Sáu entry readonly KTC-Easy là symlink hợp lệ và target tồn tại.
2. Nếu include kTAMV đang bật, checkout được pin, Python riêng, user service, hai
   symlink Klipper chính xác và patch detector phải tồn tại.
3. `tool_crash.py` đã được patch hoặc khớp đúng preimage đã review.
4. Tạo snapshot có timestamp tại
   `~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/`.

Deployment loại Markdown, `Generated-Data/`, snapshot tải về, chẩn đoán local
và `toolchanger/readonly-configs/`. Script không tự
restart service.

`cleanup-voron.sh` mặc định chỉ liệt kê candidate legacy. `--apply` chỉ xóa các
target đã hiện gồm `config.update-backup-*`, `config.backup-*` và
`~/axiscope.bak` sau khi kiểm tra chặt đường dẫn. Script không tự dọn snapshot
bình thường trong `config_backups/`.

## Kiểm tra an toàn

Thay đổi chỉ tài liệu không cần thao tác máy in. Sau khi deploy cấu hình lúc máy
idle có thể chạy:

```text
CALIBRATION_STATUS
QUERY_ENDSTOPS
KTAMV_STATUS
```

Các lệnh này không chủ động home, probe hoặc chọn tool. Không dùng
`KTAMV_CALIB_CAMERA` hoặc `KTAMV_FIND_NOZZLE_CENTER` để kiểm tra vì cả hai jog X/Y.

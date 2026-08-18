# Tool Vision

Unified XYZ tool alignment system for Klipper multi-tool 3D printers.  
Rebuilt from [kTAMV](https://github.com/TypQxQ/kTAMV) (XY camera vision) and [Axiscope](https://github.com/nic335/Axiscope) (Z probe) into a single, self-contained module.

## Architecture

```
Tool-Vision/
├── klippy/extras/
│   └── tool_vision.py      # Klipper extension (XY + Z + combined commands)
├── server/
│   ├── vision_server.py     # HTTP server (Flask + Waitress)
│   ├── vision_dm.py         # Detection Manager (5-combo blob detection)
│   ├── vision_io.py         # Camera I/O (MJPEG stream reader)
│   └── tool_vision.service  # Systemd service
├── tool_vision.cfg          # Klipper config (Z switch + camera + templates)
├── install.sh               # One-command installation
└── README.md
```

## Features

### From kTAMV
- 10-point radial camera calibration (mm/pixel)
- Camera-to-space transformation matrix (least squares)
- Iterative nozzle centering with wiggle fallback
- 5-combo nozzle detection (Standard / Relaxed / Super Relaxed × 3 preprocessors)
- Async request/result pattern for detection
- Camera preview stream
- Cloud frame upload (optional)

### From Axiscope
- Z switch probing via `tools_calibrate.PrinterProbeMultiAxis`
- Automatic Z offset calculation for all tools
- Config file offset saving (reads/writes `.cfg` or `.offsets` files)
- Custom GCode template support (`start_gcode`, `before_pickup_gcode`, etc.)
- Dynamic endstop position setting

### New (Combined)
- `TV_CALIBRATE_ALL` — Full XYZ calibration in one command
- `TV_CALIBRATE_ALL_XY` — XY-only calibration for all tools
- Unified status reporting

## GCode Commands

| Command | Description | Origin |
|---------|-------------|--------|
| `TV_CALIB_CAMERA` | Calibrate camera mm/pixel | kTAMV |
| `TV_FIND_NOZZLE_CENTER` | Center nozzle in camera view | kTAMV |
| `TV_SET_ORIGIN` | Save position as reference origin | kTAMV |
| `TV_GET_OFFSET` | Get XY offset from origin | kTAMV |
| `TV_SIMPLE_NOZZLE_POSITION` | Check if nozzle is visible | kTAMV |
| `TV_SEND_SERVER_CFG` | Send camera config to server | kTAMV |
| `TV_START_PREVIEW` | Start camera preview | kTAMV |
| `TV_STOP_PREVIEW` | Stop camera preview | kTAMV |
| `TV_MOVE_TO_ZSWITCH` | Move above Z switch | Axiscope |
| `TV_PROBE_ZSWITCH` | Probe Z switch | Axiscope |
| `TV_SET_ENDSTOP_POSITION` | Set endstop position | Axiscope |
| `TV_CALIBRATE_ALL_Z` | Z calibration for all tools | Axiscope |
| `TV_SAVE_TOOL_OFFSET` | Save offsets to config file | Axiscope |
| `TV_SAVE_MULTIPLE_TOOL_OFFSETS` | Save multiple offsets | Axiscope |
| `TV_CALIBRATE_ALL_XY` | XY calibration for all tools | **New** |
| `TV_CALIBRATE_ALL` | Full XYZ calibration | **New** |

## Usage Guide — Hướng dẫn Sử dụng

### Bước 0: Chuẩn bị phần cứng

Trước khi sử dụng Tool Vision, bạn cần:
- ✅ Lắp **công tắc Z (microswitch)** vào vị trí cố định trên khung máy
- ✅ Lắp **camera USB** hướng lên (nhìn thấy đầu nozzle từ dưới lên)
- ✅ Đảm bảo camera đã hoạt động qua Crowsnest (mở trình duyệt kiểm tra stream)
- ✅ Home máy in (G28)

### Bước 1: Cấu hình tọa độ

Mở file `tool_vision.cfg` và điền tọa độ thực tế:

```ini
[tool_vision]
# Tọa độ công tắc Z — di chuyển T0 đến đúng trên công tắc rồi ghi lại XYZ
zswitch_x_pos: 68.0      # X của công tắc
zswitch_y_pos: -10.0      # Y của công tắc
zswitch_z_pos: 7.0        # Z an toàn (phía trên công tắc vài mm)

# URL camera — lấy từ Crowsnest config
nozzle_cam_url: http://127.0.0.1:8080/?action=stream
server_url: http://127.0.0.1:8085
```

### Bước 2: Gửi cấu hình Camera cho Server

Mỗi lần khởi động Klipper, chạy lệnh này **một lần** để server biết camera ở đâu:

```
TV_SEND_SERVER_CFG
```

### Bước 3: Xem trước Camera (tùy chọn)

Để kiểm tra camera có nhìn thấy nozzle không:

```
TV_START_PREVIEW
```
→ Mở trình duyệt vào `http://[IP-máy-in]:8085/image` để xem hình ảnh trực tiếp.  
→ Nếu thấy vòng tròn bao quanh nozzle = camera hoạt động tốt.

```
TV_STOP_PREVIEW
```

### Bước 4: Chạy đo đạc

#### Kịch bản A: Đo đồng thời XYZ cho tất cả Tool (khuyên dùng)

```
TV_CALIBRATE_ALL
```

Hệ thống sẽ tự động:
1. Chọn T0 → Calibrate camera (10 điểm) → Đo Z → Đo XY → Lưu làm mốc
2. Chọn T1 → Đo Z → Đo XY → Tính offset so với T0
3. Chọn T2 → ... (lặp lại cho tất cả tool)
4. Quay về T0 → In bảng tổng kết

#### Kịch bản B: Chỉ đo Z cho tất cả Tool

```
TV_CALIBRATE_ALL_Z
```

#### Kịch bản C: Chỉ đo XY cho tất cả Tool

```
TV_CALIBRATE_ALL_XY
```

#### Kịch bản D: Đo từng bước thủ công

```gcode
; 1. Gửi config camera
TV_SEND_SERVER_CFG

; 2. Chọn T0, di chuyển nozzle đến vùng camera nhìn thấy
T0
G0 X... Y... F3000

; 3. Calibrate camera (tính mm/pixel)
TV_CALIB_CAMERA

; 4. Đưa nozzle T0 vào chính giữa camera
TV_FIND_NOZZLE_CENTER

; 5. Lưu vị trí T0 làm mốc
TV_SET_ORIGIN

; 6. Đổi sang T1
T1

; 7. Đưa nozzle T1 vào giữa camera
TV_FIND_NOZZLE_CENTER

; 8. Tính offset XY so với T0
TV_GET_OFFSET
; -> Kết quả: "Offset from origin: X:0.123 Y:-0.045"

; 9. Đo Z offset
TV_MOVE_TO_ZSWITCH
TV_PROBE_ZSWITCH SAMPLES=10
```

### Bước 5: Lưu kết quả

Sau khi đo xong, lưu offset vào file cấu hình:

```gcode
; Lưu offset 1 tool
TV_SAVE_TOOL_OFFSET TOOL_NAME="tool T1" OFFSETS="[0.123, -0.045, 0.031]"

; Lưu offset nhiều tool cùng lúc
TV_SAVE_MULTIPLE_TOOL_OFFSETS TOOLS="['tool T1', 'tool T2']" OFFSETS="[[0.12, -0.04, 0.03], [0.05, 0.02, -0.01]]"
```

### Bước 6: Thiết lập vị trí Z Switch linh hoạt (tùy chọn)

Nếu muốn thay đổi tọa độ công tắc Z mà không cần sửa file:

```gcode
; Đặt tọa độ cụ thể
TV_SET_ENDSTOP_POSITION X=68.0 Y=-10.0 Z=7.0

; Hoặc dùng vị trí hiện tại của đầu in
TV_SET_ENDSTOP_POSITION CURRENT=1
```

### Bước 7: Tùy chỉnh GCode Templates (nâng cao)

Thêm vào `tool_vision.cfg` nếu muốn chạy macro trước/sau khi đo:

```ini
[tool_vision]
# ... (các config khác) ...

# Chạy trước khi bắt đầu đo
start_gcode:
    G28          ; Home lại cho chắc
    G0 Z20 F600  ; Nâng Z an toàn

# Chạy trước khi đổi tool
before_pickup_gcode:
    G0 Z30 F600  ; Nâng Z cao để tránh va chạm

# Chạy sau khi đổi tool
after_pickup_gcode:
    G4 P500      ; Đợi 0.5s cho ổn định

# Chạy khi hoàn tất toàn bộ
finish_gcode:
    G0 X0 Y0 F3000  ; Về góc
    M118 Tool Vision: Calibration done!
```

---

## Installation

```bash
cd ~/printer_data/config/Voron\ 5\ Tool/extras/Tool-Vision
chmod +x install.sh
./install.sh
```

Then add to `printer.cfg`:
```ini
[include Voron 5 Tool/extras/Tool-Vision/tool_vision.cfg]
```

## Configuration

Edit `tool_vision.cfg` to match your hardware:

```ini
[tool_vision]
# Z Switch
pin: ^PF2
zswitch_x_pos: 68.0
zswitch_y_pos: -10.0
zswitch_z_pos: 7.0

# Camera
nozzle_cam_url: http://127.0.0.1:8080/?action=stream
server_url: http://127.0.0.1:8085

# Offsets file
config_file_path: ~/printer_data/config/tool_vision.offsets
```

## Troubleshooting — Xử lý lỗi

| Vấn đề | Nguyên nhân | Giải pháp |
|--------|------------|-----------|
| "Nozzle not found" | Camera không thấy nozzle | Kiểm tra ánh sáng, lau sạch nozzle, chạy `TV_START_PREVIEW` để xem camera |
| "Camera URL not set" | Chưa gửi config | Chạy `TV_SEND_SERVER_CFG` |
| "Camera not calibrated" | Chưa calibrate mm/pixel | Chạy `TV_CALIB_CAMERA` trước |
| "Must home first" | Máy chưa home | Chạy `G28` |
| "More than 25% failed" | Quá nhiều điểm calibrate lỗi | Lau sạch nozzle, kiểm tra ánh sáng, thử lại |
| "Offset outside frame" | mm/pixel sai | Chạy lại `TV_CALIB_CAMERA` |
| Server không phản hồi | Service chưa chạy | `sudo systemctl restart tool_vision` |

## Credits

This project is a clean-room rewrite combining the best of:
- **kTAMV** by TypQxQ — XY nozzle alignment via camera vision
- **Axiscope** by nic335 — Z offset calibration via microswitch probe

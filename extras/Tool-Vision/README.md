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

## Credits

This project is a clean-room rewrite combining the best of:
- **kTAMV** by TypQxQ — XY nozzle alignment via camera vision
- **Axiscope** by nic335 — Z offset calibration via microswitch probe

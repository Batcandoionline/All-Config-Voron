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
├── tool_vision.cfg          # Klipper config
├── install.sh               # One-command installation
└── README.md
```

## Features

### From kTAMV
- 10-point radial camera calibration (mm/pixel)
- Camera-to-space transformation matrix (polynomial least-squares)
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
- Conflict check with `[axiscope]` section
- All speeds in mm/s with internal conversion

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

## Usage Guide

### Step 0: Hardware Setup

- ✅ Mount **Z microswitch** at a fixed position on the frame
- ✅ Mount **USB camera** facing up (nozzle view from below)
- ✅ Verify camera stream works via Crowsnest
- ✅ Home printer (G28)

### Step 1: Configuration

Edit `tool_vision.cfg` with your actual coordinates:

```ini
[tool_vision]
# Z Switch — move T0 directly above the switch, record XYZ
zswitch_x_pos: 68.0      # X of switch
zswitch_y_pos: -10.0      # Y of switch
zswitch_z_pos: 7.0        # Z safe height (a few mm above switch)

# Camera URL — from Crowsnest config
nozzle_cam_url: http://127.0.0.1:8080/?action=stream
server_url: http://127.0.0.1:8085

# Speeds (all in mm/s)
move_speed: 50            # Camera calibration moves
travel_speed: 100         # XY travel to Z switch
z_move_speed: 10          # Z probing
```

### Step 2: Send Camera Config

Run once after each Klipper startup:

```
TV_SEND_SERVER_CFG
```

### Step 3: Preview Camera (optional)

```
TV_START_PREVIEW
```
→ Open browser: `http://[printer-IP]:8085/image`
→ Circle around nozzle = camera working

```
TV_STOP_PREVIEW
```

### Step 4: Run Calibration

#### Scenario A: Full XYZ for all tools (recommended)

```
TV_CALIBRATE_ALL
```

The system will automatically:
1. T0 → Calibrate camera → Probe Z → Center XY → Set as reference
2. T1 → Probe Z → Center XY → Calculate offset vs T0
3. T2 → ... (repeat for all tools)
4. Return to T0 → Print summary

#### Scenario B: Z-only for all tools

```
TV_CALIBRATE_ALL_Z
```

#### Scenario C: XY-only for all tools

```
TV_CALIBRATE_ALL_XY
```

#### Scenario D: Manual step-by-step

```gcode
TV_SEND_SERVER_CFG
T0
G0 X... Y... F3000        ; Move nozzle above camera
TV_CALIB_CAMERA            ; Calibrate mm/pixel
TV_FIND_NOZZLE_CENTER      ; Center T0 nozzle
TV_SET_ORIGIN              ; Save T0 as reference

T1
TV_FIND_NOZZLE_CENTER      ; Center T1 nozzle
TV_GET_OFFSET              ; -> "Offset from origin: X:0.123 Y:-0.045"

TV_MOVE_TO_ZSWITCH
TV_PROBE_ZSWITCH SAMPLES=10
```

### Step 5: Save Results

```gcode
TV_SAVE_TOOL_OFFSET TOOL_NAME="tool T1" OFFSETS="[0.123, -0.045, 0.031]"

TV_SAVE_MULTIPLE_TOOL_OFFSETS TOOLS="['tool T1', 'tool T2']" OFFSETS="[[0.12, -0.04, 0.03], [0.05, 0.02, -0.01]]"
```

### Step 6: Dynamic Z Switch Position (optional)

```gcode
TV_SET_ENDSTOP_POSITION X=68.0 Y=-10.0 Z=7.0
TV_SET_ENDSTOP_POSITION CURRENT=1       ; Use current toolhead position
```

### Step 7: Custom GCode Templates (advanced)

```ini
[tool_vision]
start_gcode:
    G28
    G0 Z20 F600

before_pickup_gcode:
    G0 Z30 F600

after_pickup_gcode:
    G4 P500

finish_gcode:
    G0 X0 Y0 F3000
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

> **Important:** Remove `[axiscope]` section from your config if present.
> Tool Vision replaces Axiscope's functionality entirely.

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Nozzle not found" | Camera can't see nozzle | Check lighting, clean nozzle, run `TV_START_PREVIEW` |
| "Camera URL not set" | Config not sent | Run `TV_SEND_SERVER_CFG` |
| "Camera not calibrated" | Missing mm/pixel data | Run `TV_CALIB_CAMERA` first |
| "Must home first" | Axes not homed | Run `G28` |
| "More than 25% failed" | Too many calibration failures | Clean nozzle, check lighting |
| "Offset outside frame" | mm/pixel value wrong | Re-run `TV_CALIB_CAMERA` |
| Server not responding | Service not running | `sudo systemctl restart tool_vision` |
| "[axiscope] conflict" | Both sections active | Remove `[axiscope]` from config |

## Credits

This project is a clean-room rewrite combining the best of:
- **kTAMV** by TypQxQ — XY nozzle alignment via camera vision
- **Axiscope** by nic335 — Z offset calibration via microswitch probe

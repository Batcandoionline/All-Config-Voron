# Voron 2.4 StealthChanger (5-Tool)

Production-ready Klipper/Moonraker configuration for a **Voron 2.4 350mm** running a **5-head StealthChanger** system.

---

## 🛠️ Hardware Stack

| Component | Specification | Interface / Notes |
| :--- | :--- | :--- |
| **Printer** | Voron 2.4 350mm — CoreXY | — |
| **Mainboard** | BTT Manta M8P V2.0 + CM4 | CAN Bridge `mcu` (`can0`) |
| **Toolheads** | 5× StealthChanger Toolhead (T0–T4) | EBB36 V1.2 via CAN bus (`EBB0`–`EBB4`) |
| **Hotends** | TZ V6 2.0 (×5) | EBB36 Heater |
| **Extruders** | WW BMG (×5) | EBB36 TMC2209 |
| **Bed Probe / Z Homing** | Cartographer V3 (Touch + Scan mode) | CAN bus `cartographer` (`da13d909ce34`) |
| **Z-Offset Calibrator** | SexBolt / SexBall — **Temporary calibration mount** | Manta M8P `PF4` (M1-STOP) |
| **Nozzle Cleaner** | Bambu A1 Silicone Brush + Purge Bucket | X: 277 → 312, Y: -7 → -10, Z: 1.2mm |
| **Accelerometer** | ADXL345 on each EBB36 + Cartographer V3 | SPI |
| **Chamber Sensor** | Generic 3950 NTC Thermistor | Manta M8P `PB1` (THB port) |
| **Screen** | KlipperScreen (language: vi) | HDMI / Direct |
| **Slicer** | OrcaSlicer (Multi-Color / Multi-Tool) | Profiles in `extras/Orcasilcer setting/` |

> [!NOTE]
> - **Cartographer V3** handles all Z homing, bed leveling (QGL), and adaptive bed mesh during printing (Touch/Scan mode).
> - **SexBolt/SexBall** is a *calibration-only* reference probe — plugged into M1-STOP (`PF4`) when running `CALIBRATE_ALL_OFFSETS` to measure XYZ offsets between tools (T0–T4).
> - **Nozzle Clean System** uses a Bambu A1 silicone pad with `CLEAN_NOZZLE` (flick & 360° circular scrub) and `PURGE_AND_CLEAN` macros to clean nozzles at 150°C before probing/printing.

---

## 📂 Repository Layout

```
Voron 5 Tool/
├── config/                   ← Active Klipper config (synced to ~/printer_data/config)
│   ├── printer.cfg           ← Main entry point (includes, kinematics, SAVE_CONFIG block)
│   ├── Printer-Setup/        ← Hardware, probe, fans, input shaper, macros
│   │   ├── hardware.cfg      ← Steppers, MCU definitions, bed heater, sensors
│   │   ├── calibration.cfg   ← Thermal compensation, retraction, PID
│   │   ├── probe-mesh.cfg    ← Cartographer V3 probe & bed mesh parameters
│   │   ├── nozzle-clean.cfg  ← Bambu A1 silicone brush & bucket cleaning macros
│   │   ├── prime-lines.cfg   ← Per-tool prime line macros (T0–T4)
│   │   ├── print-macros.cfg  ← PRINT_START, PRINT_END, and helper macros
│   │   ├── fans-leds.cfg     ← Chamber fans, bed fans, stealthburner LEDs
│   │   ├── input-shaper.cfg  ← Resonance tuning parameters
│   │   ├── crash_detection_override.cfg ← Tool crash detection macro overrides
│   │   └── tool_crash_cartographer.cfg  ← Cartographer tool crash protection
│   ├── toolchanger/          ← StealthChanger KTC-Easy config & tool definitions
│   │   ├── toolchanger-config.cfg ← Main toolchanger configuration
│   │   ├── tools/            ← T0.cfg … T4.cfg (EBB36 extruders, offsets, fans)
│   │   └── readonly-configs/ ← Managed by klipper-toolchanger-easy (DO NOT EDIT)
│   └── scripts/              ← Deployment & helper scripts (install.sh, update.sh)
├── Orca Config/              ← Custom OrcaSlicer profiles (machine, filament, process)
└── extras/                   ← Documentation, logs, backups, and media
    ├── backups/              ← Local timestamped config backups (gitignored)
    ├── Nhat-ky-chinh-sua/    ← Daily session update logs (Vietnamese)
    ├── pictures/             ← Hardware photos, pinout diagrams, and schematics
    ├── gcode/                ← Test print G-code samples (Voron Cube, PETG test files)
    ├── docs/                 ← StealthChanger guides and hardware user manuals
    ├── Orcasilcer setting/   ← Exported OrcaSlicer JSON profiles
    ├── axiscope-cartographer/← Cartographer axiscope visualizer & calibration data
    └── logs/                 ← Klippy and Moonraker log archives for analysis
```

---

## 🧼 Nozzle Cleaning System (`CLEAN_NOZZLE`)

The nozzle cleaning macro uses a **Bambu A1 silicone pad** and **Purge Bucket**:

- **Bucket Location:** $X = 320.0$, $Y = -8.0$
- **Silicone Pad Bounds:** $X: 277.0 \rightarrow 312.0$, $Y: -7.0 \rightarrow -10.0$ (Center $Y = -8.0$)
- **Cleaning Contact Height:** $Z = 1.2\text{mm}$

### Workflow:
1. **Travel to Bucket:** Lift Z to safe height ($Z = 15\text{mm}$), move to $X=320, Y=-8.0$.
2. **Purge (Optional):** Heat to purge temp, extrude filament into bucket, max fan cool-down to **150°C**.
3. **Flick (5×):** Dip Z to $0.7\text{mm}$, push to $X=307$, snap back to $X=320$ at $13,500\text{mm/min}$ to knock off hanging filament into the bucket.
4. **Circular Scrub (360°):** Move across 5 positions on the silicone pad ($X: 277 \rightarrow 312\text{mm}$), executing CW ($G2$) and CCW ($G3$) circular arcs ($R = 1.5\text{mm}$) to scrub the entire nozzle tip.

### How to Call:
```gcode
CLEAN_NOZZLE                           ; Wipe nozzle at 150°C (default in PRINT_START)
CLEAN_NOZZLE WIPES=8 TEMP=160         ; Custom wipes and clean temperature
PURGE_AND_CLEAN PURGE=15 PURGE_TEMP=240 ; Purge 15mm @ 240°C -> cool down -> wipe @ 150°C
```

---

## 🚀 Setup & Updates

> [!WARNING]
> Do not copy files directly into `~/printer_data/config`. Use the deployment scripts below.
>
> This repository is a **full production config bundle**. On a fresh printer OS image, install the required external dependencies first before deploying this configuration:
> - `klipper-toolchanger-easy`
> - Cartographer plugin support (`cartographer3d-plugin`)
> - `Klippain-ShakeTune`

### Required Dependencies

Install these on a fresh Raspberry Pi / CM4 machine via SSH:

| Component | Installation Command / Link |
| :--- | :--- |
| **`klipper-toolchanger-easy`** | `cd ~ && git clone https://github.com/jwellman80/klipper-toolchanger-easy.git && cd klipper-toolchanger-easy && ./install.sh` |
| **`Klippain-ShakeTune`** | `wget -O - https://raw.githubusercontent.com/Frix-x/klippain-shaketune/main/install.sh \| bash` |
| **Cartographer Plugin** | `curl -s -L https://raw.githubusercontent.com/Cartographer3D/cartographer3d-plugin/refs/heads/main/scripts/install.sh \| bash -s -- --klipper ~/klipper --klippy-env ~/klippy-env` |

### First Install (Deploy Config to Printer)
```bash
cd /tmp && git clone git@github.com:IDcrazy123/All-Config-Voron.git
cd All-Config-Voron && bash config/scripts/install.sh
```

Recommended deployment order on a new printer:
1. Flash base OS image and install Klipper / Moonraker / Mainsail.
2. Install external dependencies listed above.
3. Run `install.sh` to copy this repo's `config/` directory into `~/printer_data/config`.
4. Restart Klipper (`FIRMWARE_RESTART`) and verify all MCU connections (`can0`), probes, and tools load cleanly.

### Pull Updates (After GitHub Push)
```bash
cd ~/printer_data/config && bash scripts/update.sh
```
*Creates a timestamped backup under `~/printer_data/config_backups/` before applying updates.*

---

## 📐 Calibration Workflows

### A. Toolhead Offset Calibration (`CALIBRATE_ALL_OFFSETS`)
Run after any mechanical change (hotend replacement, tool carriage adjustment):

> [!IMPORTANT]
> **Insert the SexBolt/SexBall sensor into the M1-STOP port (`PF4`)** before starting. Remove it after calibration completes.

```gcode
G28
QUAD_GANTRY_LEVEL
CALIBRATE_ALL_OFFSETS    ; Probes T0–T4 sequentially on SexBolt, calculates XYZ offsets
FIRMWARE_RESTART
CHECK_OFFSETS            ; Verify saved offsets in printer.cfg
```

### B. First-Layer Fine-Tuning (Per Tool)
Adjust `gcode_z_offset` for any individual tool directly from KlipperScreen (Live Adjust Z) during a first-layer test print. Values are saved to `#*# [tool Tn]` in `printer.cfg` via `SAVE_CONFIG`.

### C. Adaptive Bed Mesh
```gcode
G28
QUAD_GANTRY_LEVEL
BED_MESH_CALIBRATE       ; Cartographer Touch/Scan mode adaptive mesh
```

---

## 🛡️ Dev & AI Guidelines

- **Backup first:** Always create `extras/backups/pre-[task]-[YYYYMMDD]-[HHmmss]/` before modifying any `.cfg` file.
- **Do not edit `readonly-configs/`:** Files in `config/toolchanger/readonly-configs/` are auto-managed by the KTC-Easy plugin.
- **Git Hygiene:** Maintain daily session logs in `extras/Nhat-ky-chinh-sua/YYYY-MM-DD-session-updates.md`. Commit messages must follow English conventions (`config:`, `fix:`, `feat:`, `docs:`).
- **AI Rules Entry Point:** See [`.agents/AGENTS.md`](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/.agents/AGENTS.md) for full AI assistant rules and guidelines.

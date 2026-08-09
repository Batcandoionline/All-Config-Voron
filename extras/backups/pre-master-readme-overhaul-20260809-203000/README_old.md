# Voron 2.4 StealthChanger (5-Tool)

Production-ready Klipper/Moonraker configuration for a **Voron 2.4 350mm** running a **5-head StealthChanger** system.

---

## 🛠️ Hardware Stack

| Component | Specification | Interface / Pin Assignment |
| :--- | :--- | :--- |
| **Printer** | Voron 2.4 350mm — CoreXY | — |
| **Mainboard** | BTT Manta M8P V2.0 + CM4 | CAN Bridge `mcu` (`canbus_uuid: 19b203d75137`) |
| **Host System** | BTT CM4 running MainsailOS | Mounted directly on Manta M8P |
| **Toolheads** | 5× StealthChanger Toolhead (T0–T4) | BTT EBB36 V1.2 via CAN bus (`EBB0`–`EBB4`) |
| **Hotends** | TZ V6 2.0 (×5) | EBB36 Heater ports |
| **Extruders** | WW BMG (×5) | EBB36 onboard TMC2209 |
| **Bed Probe / Z Homing** | Cartographer V3 fw6.1.0 (Touch + Scan) | CAN bus `cartographer` (`canbus_uuid: da13d909ce34`) |
| **Z-Offset Calibrator** | Microswitch / Axiscope Calibration Switch | Manta M8P `PF2` (GND + `^PF2`) at $X=68.0, Y=-10.0, Z=7.0$ |
| **Nozzle Cleaner** | Bambu A1 Silicone Brush + Purge Bucket | Bucket ($X=320, Y=-8$), Pad ($X: 277 \rightarrow 312$, $Y: -7 \rightarrow -10$, $Z=1.2\text{mm}$) |
| **Accelerometer** | ADXL345 on each EBB36 + Cartographer V3 | SPI / I2C |
| **Chamber Sensor** | Generic 3950 100K NTC Thermistor | Manta M8P `PB1` (THB port) |
| **Bed Heater** | AC Bed Heater with SSR | Thermistor: `PB0` (NTC 100K), Heater: `PA1` |
| **Screen** | KlipperScreen (language: vi) | HDMI / DSI |
| **Slicer** | OrcaSlicer (Multi-Color / Multi-Tool) | Profiles in `extras/Orcasilcer setting/` |

> [!NOTE]
> - **Cartographer V3** handles all primary Z homing, Quad Gantry Leveling (QGL), and high-density adaptive bed mesh (55×55 points).
> - **Axiscope Z-Switch** ($X=68, Y=-10, Z=7$) on pin `PF2` serves as a repeatable hardware baseline reference for relative tool lengths.
> - **Nozzle Cleaning System** uses a Bambu A1 silicone pad with `CLEAN_NOZZLE` (flick & 360° circular scrub) and `PURGE_AND_CLEAN` macros to clean nozzles at 150°C before probing/printing.

---

## 📂 Repository Layout

```
Voron 5 Tool/
├── README.md                 ← Project overview and documentation (English)
│
├── config/                   ← Active Klipper configuration payload
│   ├── README.md             ← Config-specific guide & pinout mapping
│   ├── printer.cfg           ← Main entry point (includes, kinematics, SAVE_CONFIG block)
│   ├── KlipperScreen.conf    ← KlipperScreen display configuration
│   ├── moonraker.conf        ← Moonraker API server & update manager configuration
│   ├── crowsnest.conf        ← Camera streaming configuration (WebRTC)
│   ├── mainsail.cfg          ← Mainsail web interface macros
│   │
│   ├── Printer-Setup/        ← Hardware, probe, fans, input shaper, macros
│   │   ├── hardware.cfg      ← Steppers, MCU definitions, bed heater, chamber sensor
│   │   ├── calibration.cfg   ← Thermal compensation, [axiscope] switch calib (pin: ^PF2)
│   │   ├── probe-mesh.cfg    ← Cartographer V3 probe & adaptive bed mesh parameters
│   │   ├── nozzle-clean.cfg  ← Bambu A1 silicone brush & bucket cleaning macros (`CLEAN_NOZZLE`)
│   │   ├── prime-lines.cfg   ← Per-tool prime line macros (T0–T4)
│   │   ├── print-macros.cfg  ← PRINT_START, PRINT_END, and helper macros
│   │   ├── fans-leds.cfg     ← Chamber fans, bed fans, stealthburner LEDs
│   │   ├── input-shaper.cfg  ← Resonance tuning parameters
│   │   ├── crash_detection_override.cfg ← Tool crash detection macro overrides
│   │   └── tool_crash_cartographer.cfg  ← Cartographer tool crash protection
│   │
│   ├── toolchanger/          ← StealthChanger KTC-Easy config & tool definitions
│   │   ├── toolchanger-config.cfg ← Main toolchanger configuration & switch coords
│   │   ├── tools/            ← T0.cfg … T4.cfg (EBB36 extruders, offsets, fans)
│   │   └── readonly-configs/ ← Managed by klipper-toolchanger-easy (DO NOT EDIT)
│   │
│   └── scripts/              ← Deployment & helper scripts
│       ├── install.sh        ← First-time install script (auto-excludes *.md)
│       ├── update.sh         ← Pull & apply updates (auto-backup & excludes *.md)
│       └── cleanup-voron.sh  ← Clean up legacy backup directories
│
├── Orca Config/              ← Custom OrcaSlicer profiles (machine, filament, process)
│
└── extras/                   ← Documentation, logs, backups, and media
    ├── backups/              ← Timestamped configuration backups (synced on Git)
    ├── Nhat-ky-chinh-sua/    ← Daily session update logs (Vietnamese)
    ├── pictures/             ← Hardware photos, pinout diagrams, and schematics
    ├── gcode/                ← Test print G-code samples
    ├── docs/                 ← StealthChanger guides and hardware user manuals
    ├── Orcasilcer setting/   ← Exported OrcaSlicer JSON profiles
    ├── axiscope-cartographer/← Cartographer axiscope visualizer & calibration data
    └── logs/                 ← Klippy and Moonraker log archives for offline analysis
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
CLEAN_NOZZLE                             ; Wipe nozzle at 150°C (default in PRINT_START)
CLEAN_NOZZLE WIPES=8 TEMP=160           ; Custom wipes and clean temperature
PURGE_AND_CLEAN PURGE=15 PURGE_TEMP=240   ; Purge 15mm @ 240°C -> cool down -> wipe @ 150°C
```

---

## 🚀 Setup & Updates

> [!WARNING]
> Do not copy files directly into `~/printer_data/config`. Use the deployment scripts below.
> The deployment scripts (`install.sh` and `update.sh`) automatically exclude all `README.md` and `*.md` files so that Klipper's config folder remains clean.

### Required Dependencies

Install these on a fresh Raspberry Pi / CM4 machine via SSH:

| Component | Installation Command |
| :--- | :--- |
| **`klipper-toolchanger-easy`** | `cd ~ && git clone https://github.com/jwellman80/klipper-toolchanger-easy.git && cd klipper-toolchanger-easy && ./install.sh` |
| **`Klippain-ShakeTune`** | `wget -O - https://raw.githubusercontent.com/Frix-x/klippain-shaketune/main/install.sh \| bash` |
| **Cartographer Plugin** | `curl -s -L https://raw.githubusercontent.com/Cartographer3D/cartographer3d-plugin/refs/heads/main/scripts/install.sh \| bash -s -- --klipper ~/klipper --klippy-env ~/klippy-env` |

### First Install (Deploy Config to Printer)
```bash
cd /tmp && git clone git@github.com:IDcrazy123/All-Config-Voron.git
cd All-Config-Voron && bash "Voron 5 Tool/config/scripts/install.sh"
```

### Pull Updates (After GitHub Push)
```bash
cd ~/printer_data/config && bash scripts/update.sh
```
*Creates a timestamped backup under `~/printer_data/config_backups/` before pulling and applying updates.*

---

## 📐 Calibration & Z-Offset Strategy

### A. Dual Strategy: Empirical Print Calibration + Hardware Switch Baseline
- **Production Z-Offsets (`printer.cfg`):** Fine-tuned via first-layer test prints for optimal squish and adhesion:
  - `T0`: Reference ($Z = 0.000$)
  - `T1`: `gcode_z_offset = 0.228`
  - `T2`: `gcode_z_offset = -0.295`
  - `T3`: `gcode_z_offset = -0.268`
  - `T4`: `gcode_z_offset = 0.086`
- **Hardware Drift Baseline:** Automated microswitch probing on pin `PF2` ($X=68.0, Y=-10.0, Z=7.0$) allows quick hardware verification without reprinting test swatches after hotend maintenance.

### B. Adaptive Bed Mesh
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

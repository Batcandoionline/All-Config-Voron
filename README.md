# Voron 2.4 StealthChanger (5-Tool Production)

[![Klipper](https://img.shields.io/badge/Klipper-v0.13.0-green.svg)](https://www.klipper3d.org/)
[![Toolchanger](https://img.shields.io/badge/StealthChanger-KTC--Easy-blue.svg)](https://stealthchanger.com/)
[![Cartographer3D](https://img.shields.io/badge/Cartographer-V3%20fw6.1.0-orange.svg)](https://cartographer3d.com/)
[![Axiscope](https://img.shields.io/badge/Axiscope-PF2%20switch-blueviolet.svg)](https://github.com/nic335/Axiscope)
[![WebUI](https://img.shields.io/badge/WebUI-Mainsail-red.svg)](https://docs.mainsail.xyz/)
[![Slicer](https://img.shields.io/badge/Slicer-OrcaSlicer-purple.svg)](https://github.com/SoftFever/OrcaSlicer)

Full production configuration repository for a **Voron 2.4 350mm CoreXY** 3D printer running an automated **5-Tool StealthChanger** system powered by **Klipper**, **Manta M8P V2.0 + CM4**, **5× EBB36 CAN toolheads**, **Cartographer V3**, and a **1000W AC Heated Bed**.

Production status confirmed by the operator on 2026-08-23: the Cartographer and
T4 sensor faults are resolved, and all per-tool Input Shaper profiles are
calibrated. KTC-Easy is the sole owner of `toolchanger/readonly-configs/`;
All-Config manages only the user-editable KTC overrides and tool definitions.

---

## 🛠️ 1. Master Hardware Specifications

| Component | Hardware Specification | Configuration Details / Port |
| :--- | :--- | :--- |
| **Motion Kinematics** | Voron 2.4 CoreXY ($350 \times 350 \times 345\text{ mm}$) | $V_{\text{max}} = 300\text{mm/s}, A = 4000\text{mm/s}^2$ |
| **Controller & Host** | BTT Manta M8P V2.0 + BTT CM4 | MainsailOS (Debian 12 Bookworm, Linux 6.12) |
| **CAN Bus Interface** | `can0` @ 1,000,000 baud | Master bridge UUID: `19b203d75137` |
| **Tool Changing System** | StealthChanger (KTC-Easy) | 5 individual tools (T0–T4) docked at rear gantry |
| **Toolhead MCUs** | 5× BTT EBB36 V1.2 | Dedicated CAN node per toolhead |
| **Extruders & Hotends**| 5× WW BMG + 5× TZ V6 2.0 | TMC2209 @ 0.6A per tool, 3950 NTC thermistors |
| **Z-Probe & Mesh** | Cartographer V3 Flat (fw6.1.0) | CAN UUID: `da13d909ce34` (Touch Z0 + $55 \times 55$ Scan Mesh) |
| **Tool-Offset Calibrator**| Axiscope Z-offset measurement with a PF2 microswitch | Switch center $(X=68, Y=-10, Z=7)$; 10 samples per tool; camera backends inactive |
| **Heated Bed** | 1000W 220V AC Silicone Pad + SSR | SSR Pin `PA1`, Thermistor `PB0` (NTC 100K MGB18) |
| **Nozzle Cleaner** | Bambu A1 Silicone Pad + Purge Bucket | Bucket at $(X=320, Y=-8)$, Silicone Pad at $X: 277 \rightarrow 312$ |
| **Chamber Feedback** | Generic 3950 100K NTC | Thermistor port `THB` (`PB1`) + Under-bed fan `bed_fan` (`PF8`) |
| **Status Lighting** | 40× WS2812B Chamber + Tool LEDs | Chamber strip on `PD15` + 3× NeoPixel per toolhead |

---

## 📡 2. CAN Bus Topology & Toolhead Mapping

| Device | Node Role | CAN Bus UUID | Extruder & Fan Pinout | Tool Status Pin / LED |
| :---: | :---: | :---: | :---: | :---: |
| **`mcu`** | Manta M8P V2.0 | `19b203d75137` | Mainboard, Steppers, 1000W Bed | Chamber NeoPixel: `PD15` |
| **`cartographer`**| Surface & Mesh Probe | `da13d909ce34` | Offsets: $X=0, Y=35.0, Z=0$ | — |
| **`T0`** | Toolhead 0 | `441e1484ac41` | Extruder / Part `PA1` / Hotend `PA0` | Sensor: `^!EBB0:PB6` / LED: `PD3` |
| **`T1`** | Toolhead 1 | `6475b5b9e028` | Extruder / Part `PA1` / Hotend `PA0` | Sensor: `^!EBB1:PB6` / LED: `PD3` |
| **`T2`** | Toolhead 2 | `4ad9d622a836` | Extruder / Part `PA1` / Hotend `PA0` | Sensor: `^!EBB2:PB6` / LED: `PD3` |
| **`T3`** | Toolhead 3 | `c2465b7c36f8` | Extruder / Part `PA1` / Hotend `PA0` | Sensor: `^!EBB3:PB6` / LED: `PD3` |
| **`T4`** | Toolhead 4 | `28650279df58` | Extruder / Part `PA1` / Hotend `PA0` | Sensor: `^!EBB4:PB6` / LED: `PD3` |

---

## 🔧 3. StealthChanger Docks & Calibrated Offsets

### Rear Dock Positions ($Z = 343.0\text{ mm}$)
```
Rear Frame:  [ T0: X=30.20, Y=1.30 ]  [ T1: X=104.00, Y=1.10 ]  [ T2: X=176.00, Y=1.60 ]  [ T3: X=249.50, Y=2.50 ]  [ T4: X=321.50, Y=2.60 ]
```

### Active Production Tool Offsets (`printer.cfg` SAVE_CONFIG)
Empirically calibrated for perfect first-layer squish across all 5 nozzles:

| Tool | X Offset (mm) | Y Offset (mm) | Z Offset (mm) | Role / Status |
| :---: | :---: | :---: | :---: | :--- |
| **T0** | `0.000` | `0.000` | `0.000` | Master Reference Datum |
| **T1** | `-0.243` | `-0.252` | **`+0.228`** | Calibrated optimal squish |
| **T2** | `+0.746` | `+0.086` | **`-0.295`** | Calibrated optimal squish |
| **T3** | `+0.304` | `+0.449` | **`-0.268`** | Calibrated optimal squish |
| **T4** | `+0.041` | `+0.352` | **`-0.014`** | Calibrated optimal squish |

---

## 📐 4. Probing, Leveling & Nozzle Maintenance

### Multi-Layer Calibration Pipeline
1. **Quad Gantry Leveling (`QUAD_GANTRY_LEVEL`):** 4-point mechanical gantry tramming with `0.0075mm` retry tolerance.
2. **Axis Twist Compensation:** Corrects X-axis extrusion twist ($X: 20 \rightarrow 320\text{mm}$).
3. **Cartographer Touch & Scan:** Direct physical Touch at $(174, 168)$ for absolute Z0 reference, followed by high-speed $55 \times 55$ adaptive bed scanning ($3,025$ points).
4. **Tool-offset switch:** Axiscope measures each tool against the PF2 microswitch at $(X=68, Y=-10, Z=7)$. It reports Z deltas for review and does not rewrite the split T0–T4 configuration files automatically.

### Bambu A1 Nozzle Cleaning System (`nozzle-clean.cfg`)
* **Purge Bucket:** $X = 320.0, Y = -8.0$
* **Silicone Pad Scrub Area:** $X: 277.0 \rightarrow 312.0$, $Y: -7.0 \rightarrow -10.0$ at $Z = 1.2\text{mm}$
* **Scrubbing Motion:** $225\text{mm/s}$ flick snap-back + 5-point alternating $360^\circ$ circular arcs ($R = 1.5\text{mm}$).
* **Quick Commands:** `CLEAN_NOZZLE` (Wipe @ 150°C), `PURGE_AND_CLEAN` (Purge @ 240°C into bucket $\rightarrow$ cool $\rightarrow$ scrub).

---

## ☀️ 5. Heated Bed Filament Drying System (`START_DRYER`)

Dries filament spools directly on the 1000W heated bed under a cardboard cover with closed-loop chamber feedback, forced convection (`bed_fan`), and Amber/Orange status lighting:

Mainsail exposes one `START_DRYER` button instead of separate `DRY_PLA`, `DRY_PETG`, and other preset buttons. Clicking it opens a material-selection prompt. The same presets can be started from the console with `START_DRYER MATERIAL=<material>`.

| Material selection | Material | Bed Temp | Target Chamber | Duration | Base Fan (`bed_fan`) | Airflow Profile |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`MATERIAL=PLA`** | PLA / PLA+ | **50°C** | **40°C** | 4 hours | **40%** | Multi-Zone + 20m Flush Pulse |
| **`MATERIAL=TPU`** | TPU / TPE | **60°C** | **45°C** | 5 hours | **40%** | Multi-Zone + 20m Flush Pulse |
| **`MATERIAL=PETG`** | PETG | **70°C** | **55°C** | 4 hours | **50%** | Multi-Zone + 20m Flush Pulse |
| **`MATERIAL=ABS`** | ABS | **90°C** | **65°C** | 4 hours | **60%** | Multi-Zone + 20m Flush Pulse |
| **`MATERIAL=ASA`** | ASA | **90°C** | **65°C** | 4 hours | **60%** | Multi-Zone + 20m Flush Pulse |
| **`MATERIAL=NYLON`** | PA / Nylon | **100°C** | **70°C** | 6 hours | **70%** | Multi-Zone + 20m Flush Pulse |
| **`MATERIAL=PC`** | Polycarbonate | **105°C** | **75°C** | 6 hours | **70%** | Multi-Zone + 20m Flush Pulse |

* **Multi-Zone Adaptive Airflow:** Automatic cold warmup boost (65–85%), active moisture evacuation window (40–50%), and overheat safety protection.
* **Periodic Moisture Flush Pulse:** Automatically increases fan to 70% for 30 seconds every 20 minutes to flush trapped humid air.
* **Optional humidity input:** Dryer macros use `.humidity` only when a separately installed sensor extension exposes that field. Native Klipper does not provide `sensor_type: DHT22`.
* **Direct command:** `START_DRYER MATERIAL=PETG`. Explicit `BED`, `CHAMBER`, `TIME`, `TIME_HOURS`, `FAN`, `PARK`, and humidity parameters override the selected preset when required.
* **Live Telemetry & Controls:** Real-time countdown on LCD/Mainsail (`Dry 3h50m | B:60C C:45C`). The public dryer controls are `START_DRYER`, `STOP_DRYER`, and `DRYER_STATUS`.

---

## 🎨 6. OrcaSlicer Multi-Color Integration

Tuned profiles are located under [extras/Orcasilcer setting/](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/Orcasilcer%20setting/):
* **G-Code Output Format:** `Klipper Toolchanger`
* **Tool Change G-Code:** `T[next_extruder]` (KTC-Easy automatically handles dropoff/pickup, standby temperatures, and input shaper assignment).
* **Purge / Wipe Tower:** Disabled or set to minimal volume (purge bucket + silicone scrub replaces prime towers).
* **Tool Change Retraction:** $1.0\text{mm} \sim 2.0\text{mm}$ at $40\text{mm/s}$.

---

## 📁 7. Repository Layout & SSH Deployment

```
Voron 5 Tool/
├── README.md                 ← Master system documentation (this file)
│
├── config/                   ← Active Klipper configuration payload
│   ├── README.md             ← Config payload notes & pinout reference
│   ├── printer.cfg           ← Core entry point & SAVE_CONFIG block
│   ├── KlipperScreen.conf    ← KlipperScreen touch UI configuration (Language: vi)
│   ├── moonraker.conf        ← Moonraker API server & update manager config
│   ├── crowsnest.conf        ← Camera streamer configuration (WebRTC)
│   ├── mainsail.cfg          ← Mainsail web interface macro bundle
│   │
│   ├── Printer-Setup/        ← Modular printer configuration files
│   │   ├── hardware.cfg      ← Steppers, MCUs, 1000W bed, chamber thermistor
│   │   ├── fans-leds.cfg     ← Chamber fans, bed fans, tool NeoPixels & status macros
│   │   ├── calibration-probe.cfg ← Cartographer/mesh and active Axiscope PF2 calibration
│   │   ├── input-shaper.cfg  ← Global input shaper defaults (per-tool overrides in T0–T4.cfg)
│   │   ├── nozzle-clean.cfg  ← Bambu A1 silicone brush & purge bucket macros
│   │   ├── prime-lines.cfg   ← Per-tool prime line macros (T0–T4)
│   │   ├── print-macros.cfg  ← PRINT_START, PRINT_END, single-prompt Filament Dryer
│   │   └── tool-crash.cfg    ← Tool presence detector, KTC routing, safe pause
│   │
│   ├── toolchanger/          ← StealthChanger KTC-Easy toolchanger config
│   │   ├── toolchanger-config.cfg ← Dropoff/pickup paths & park coords
│   │   ├── tools/ (T0–T4.cfg)     ← Individual tool definitions (EBB36 pins, offsets)
│   │   └── readonly-configs/      ← Managed by KTC-Easy (DO NOT EDIT)
│   │
│   └── scripts/              ← Deployment & maintenance scripts
│       ├── install.sh        ← First-time install script (auto-excludes *.md)
│       ├── update.sh         ← Auto-backup & update pull script (excludes *.md)
│       └── cleanup-voron.sh  ← Maintenance & backup cleaner
│
├── Orca Config/              ← Custom OrcaSlicer machine & process profiles
│
└── extras/                   ← Documentation, backups, and diagnostic archives
    ├── backups/              ← Timestamped configuration backups (Git tracked)
    ├── Nhat-ky-chinh-sua/    ← Daily engineering change logs (Vietnamese)
    ├── pictures/             ← Hardware photos and schematics
    ├── axiscope-cartographer/← Axiscope & Cartographer calibration logs
    └── logs/                 ← Klippy and Moonraker runtime logs
```

### Deployment Commands

KTC-Easy must be installed first. Its installer creates the six managed
symlinks in `~/printer_data/config/toolchanger/readonly-configs/`. Run KTC and
All-Config installers only while the printer is idle; both may require a
Klipper restart.

* **First-Time Install Without a Persistent Clone:**
  ```bash
  tmp_dir="$(mktemp -d /tmp/all-config-voron.XXXXXX)"
  curl -fsSL https://github.com/IDcrazy123/All-Config-Voron/archive/refs/heads/main.tar.gz \
    | tar -xz -C "${tmp_dir}" --strip-components=1
  bash "${tmp_dir}/config/scripts/install.sh"
  rm -rf -- "${tmp_dir}"
  sudo systemctl restart moonraker klipper
  ```

* **Pull & Apply Updates from GitHub:**
  ```bash
  cd ~/printer_data/config
  bash scripts/update.sh
  sudo systemctl restart moonraker klipper
  ```
  *(Downloads a temporary All-Config archive, creates a timestamped backup,
  deploys it, then removes the archive; All-Config keeps no Git clone on the
  Pi.)*

`install.sh` validates all six KTC-Easy readonly symlinks before creating a
backup or changing the live configuration. It then excludes the complete
readonly directory from `rsync`, so KTC updates cannot be overwritten by this
repository. If validation fails, rerun
`bash ~/klipper-toolchanger-easy/install.sh` while the printer is idle and then
retry the All-Config deployment.

### Axiscope PF2 Switch Calibration

Axiscope is the production tool Z-offset measurement backend:

- Source checkout: `~/axiscope`
- Repository: `https://github.com/nic335/Axiscope`
- Klipper module: `~/klipper/klippy/extras/axiscope.py`
- Switch input: Manta M8P `^PF2` with GND
- Switch position: `X=68`, `Y=-10`, `Z=7`
- Measurement: 10 Z samples per tool
- Scope: Z deltas only; existing production XY offsets remain unchanged

Run `CALIBRATION_STATUS` or `QUERY_ENDSTOPS` without motion. Use
`CALIBRATE_ALL_Z_OFFSETS` only with an operator present after homing and checking
the switch path. Results are reported for review; they are not written directly
because each tool is maintained in a separate T0–T4 config file.

ToolVision remains installed but inactive, without a Klipper include or
Moonraker updater. kTAMV and its service/runtime are removed.

`Generated-Data/` is printer-local and deployment-protected. It keeps preserved
ToolVision JSON and ShakeTune graphs under one clearly named folder. The printer
keeps only the current rollback snapshot under `~/printer_data/config_backups/`.

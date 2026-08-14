# Voron 2.4 StealthChanger (5-Tool Production)

[![Klipper](https://img.shields.io/badge/Klipper-v0.13.0-green.svg)](https://www.klipper3d.org/)
[![Toolchanger](https://img.shields.io/badge/StealthChanger-KTC--Easy-blue.svg)](https://stealthchanger.com/)
[![Cartographer3D](https://img.shields.io/badge/Cartographer-V3%20fw6.1.0-orange.svg)](https://cartographer3d.com/)
[![WebUI](https://img.shields.io/badge/WebUI-Mainsail-red.svg)](https://docs.mainsail.xyz/)
[![Slicer](https://img.shields.io/badge/Slicer-OrcaSlicer-purple.svg)](https://github.com/SoftFever/OrcaSlicer)

Full production configuration repository for a **Voron 2.4 350mm** CoreXY printer equipped with a **5-Tool StealthChanger**, **BTT Manta M8P V2.0 + CM4**, **5× BTT EBB36 V1.2 (CAN)**, **Cartographer V3**, and a **1000W AC Heated Bed**.

---

## 🛠️ System Specifications

| Component | Specification | Details / Interface |
| :--- | :--- | :--- |
| **Printer Frame** | Voron 2.4 350mm CoreXY | Build volume: $350 \times 350 \times 345\text{ mm}$ |
| **Mainboard & Host** | BTT Manta M8P V2.0 + BTT CM4 | MainsailOS (Debian 12 Bookworm, Linux 6.12) |
| **Main CAN Bridge** | `mcu` (`19b203d75137`) | `can0` @ 1,000,000 baud |
| **Toolhead MCUs** | 5× BTT EBB36 V1.2 | CAN bus (`EBB0` to `EBB4`) |
| **Hotends & Extruders**| 5× TZ V6 2.0 + 5× WW BMG | TMC2209 @ 0.6A per tool |
| **Z-Probe / Z0** | Cartographer V3 Flat (fw6.1.0) | CAN `da13d909ce34` (Touch + 55×55 Scan Mesh) |
| **Z-Offset Calibrator**| Microswitch / Axiscope Switch | Manta M8P `^PF2` + GND ($X=68.0, Y=-10.0, Z=7.0$) |
| **Heated Bed** | 1000W 220V AC Silicone Pad | SSR control on `PA1`, NTC 100K on `PB0` |
| **Nozzle Cleaner** | Bambu A1 Silicone Pad + Bucket | Purge ($X=320, Y=-8$), Wipe ($X: 277 \rightarrow 312, Z=1.2$) |
| **Thermal Chamber** | 100K NTC (DHT22 / AM2302 ready) | Port `THB` (`PB1`) + Under-bed fan (`bed_fan` on `PF8`) |
| **Lighting** | 40× WS2812B Chamber + Tool LEDs | Chamber strip on `PD15` + individual tool NeoPixels |

---

## 📡 CAN Bus Topology & Toolhead Mapping

All toolheads and probes communicate via high-speed CAN bus (`can0`):

| Device | Role | CAN UUID | Extruder / Fan Pins | Status Pin / LED |
| :---: | :---: | :---: | :---: | :---: |
| **`mcu`** | Manta M8P V2.0 | `19b203d75137` | Mainboard & Steppers | Chamber: `PD15` |
| **`cartographer`** | Probe & Scan Mesh | `da13d909ce34` | $X=0, Y=35, Z=0$ Offset | — |
| **`T0`** | Toolhead 0 | `441e1484ac41` | Extruder / Part `PA1` / Hotend `PA0` | Pin `^!EBB0:PB6` / LED `PD3` |
| **`T1`** | Toolhead 1 | `6475b5b9e028` | Extruder / Part `PA1` / Hotend `PA0` | Pin `^!EBB1:PB6` / LED `PD3` |
| **`T2`** | Toolhead 2 | `4ad9d622a836` | Extruder / Part `PA1` / Hotend `PA0` | Pin `^!EBB2:PB6` / LED `PD3` |
| **`T3`** | Toolhead 3 | `c2465b7c36f8` | Extruder / Part `PA1` / Hotend `PA0` | Pin `^!EBB3:PB6` / LED `PD3` |
| **`T4`** | Toolhead 4 | `28650279df58` | Extruder / Part `PA1` / Hotend `PA0` | Pin `^!EBB4:PB6` / LED `PD3` |

---

## 🔧 StealthChanger Docks & Active Offsets

### 1. Rear Dock Coordinates ($Z = 343\text{ mm}$)
```
Rear Frame:  [ T0: X=30.2, Y=1.3 ]  [ T1: X=104.0, Y=1.1 ]  [ T2: X=176.0, Y=1.6 ]  [ T3: X=249.5, Y=2.5 ]  [ T4: X=321.5, Y=2.6 ]
```

### 2. Active Production Tool Offsets (`printer.cfg`)
Calibrated for optimal first-layer squish across all 5 heads:

| Tool | X Offset (mm) | Y Offset (mm) | Z Offset (mm) | Description |
| :---: | :---: | :---: | :---: | :--- |
| **T0** | `0.000` | `0.000` | `0.000` | Master Reference Tool |
| **T1** | `-0.243` | `-0.252` | **`+0.228`** | Calibrated squish offset |
| **T2** | `+0.746` | `+0.086` | **`-0.295`** | Calibrated squish offset |
| **T3** | `+0.304` | `+0.449` | **`-0.268`** | Calibrated squish offset |
| **T4** | `+0.041` | `+0.352` | **`-0.014`** | Calibrated squish offset |

---

## 📐 Leveling & Nozzle Maintenance

### 1. Bed Leveling Stack
1. **Quad Gantry Leveling (`QUAD_GANTRY_LEVEL`):** 4-point gantry tramming ($50, 25 \rightarrow 300, 275$) with `0.0075mm` tolerance.
2. **Axis Twist Compensation:** Corrects rail twist along X ($X: 20 \rightarrow 320\text{mm}$).
3. **Cartographer Touch & Scan:** Direct physical Touch at $(174, 168)$ for absolute Z0 datum, followed by ultra-fast $55 \times 55$ adaptive bed scanning.

### 2. Bambu A1 Nozzle Cleaning (`nozzle-clean.cfg`)
- **Purge Bucket:** $X = 320.0, Y = -8.0$
- **Silicone Brush Scrub Area:** $X: 277.0 \rightarrow 312.0$, $Y: -7.0 \rightarrow -10.0$ at $Z = 1.2\text{mm}$
- **Cleaning Patterns:** High-speed snap-back flick ($225\text{mm/s}$) + 5-point alternating $360^\circ$ circular arcs ($R = 1.5\text{mm}$).
- **Commands:** `CLEAN_NOZZLE` (Wipe @ 150°C), `PURGE_AND_CLEAN` (Purge @ 240°C into bucket $\rightarrow$ cool $\rightarrow$ scrub).

---

## ☀️ Heated Bed Filament Dryer (`START_DRYER`)

Dries filament spools directly on the 1000W heated bed under a cardboard cover with closed-loop chamber feedback, under-bed convection (`bed_fan`), and automatic Amber/Orange status lighting:

| Preset | Material | Bed Temp | Target Chamber | Duration | Base Fan (`bed_fan`) | Airflow Strategy |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`DRY_PLA`** | PLA / PLA+ | **50°C** | **40°C** | 4 hours | **40%** | Multi-Zone + 20m Flush Pulse |
| **`DRY_TPU`** | TPU / TPE | **60°C** | **45°C** | 5 hours | **40%** | Multi-Zone + 20m Flush Pulse |
| **`DRY_PETG`** | PETG | **70°C** | **55°C** | 4 hours | **50%** | Multi-Zone + 20m Flush Pulse |
| **`DRY_ABS`** | ABS | **90°C** | **65°C** | 4 hours | **60%** | Multi-Zone + 20m Flush Pulse |
| **`DRY_ASA`** | ASA | **90°C** | **65°C** | 4 hours | **60%** | Multi-Zone + 20m Flush Pulse |
| **`DRY_NYLON`** | PA / Nylon | **100°C** | **70°C** | 6 hours | **70%** | Multi-Zone + 20m Flush Pulse |
| **`DRY_PC`** | Polycarbonate | **105°C** | **75°C** | 6 hours | **70%** | Multi-Zone + 20m Flush Pulse |

- **Multi-Zone Airflow:** Fast cold warmup boost (65–85%), active convective drying window (40–50%), and overheat safety modulation.
- **Periodic Moisture Flush:** Automatically boosts fan to 70% for 30s every 20 minutes to evacuate trapped humid air pockets.
- **Telemetry & Stop:** Real-time countdown on LCD/Mainsail (`Dry 3h50m | B:60C C:45C`). Type `STOP_DRYER` or `DRYER_STATUS` anytime.

---

## 📁 Repository Structure & Deployment

```
Voron 5 Tool/
├── README.md                 ← Master system documentation (this file)
│
├── config/                   ← Active Klipper configuration payload
│   ├── README.md             ← Config payload notes & pinout mapping
│   ├── printer.cfg           ← Main entry point & SAVE_CONFIG block
│   ├── KlipperScreen.conf    ← KlipperScreen settings (Language: vi)
│   ├── moonraker.conf        ← Moonraker API server configuration
│   ├── crowsnest.conf        ← Camera WebRTC streaming configuration
│   ├── mainsail.cfg          ← Mainsail web interface macro bundle
│   │
│   ├── Printer-Setup/        ← Modular printer configuration files
│   │   ├── hardware.cfg      ← Steppers, MCUs, 1000W bed, chamber thermistor / DHT22
│   │   ├── fans-leds.cfg     ← Chamber fans, bed fans, tool NeoPixels & status macros
│   │   ├── calibration.cfg   ← Thermal calibration & [axiscope] switch (^PF2)
│   │   ├── input-shaper.cfg  ← Input shaper defaults (per-tool overrides in T0–T4.cfg)
│   │   ├── probe-mesh.cfg    ← Cartographer V3 touch/scan & 55×55 bed mesh
│   │   ├── nozzle-clean.cfg  ← Bambu A1 silicone brush & purge bucket macros
│   │   ├── prime-lines.cfg   ← Per-tool prime line macros (T0–T4)
│   │   ├── print-macros.cfg  ← PRINT_START, PRINT_END, Filament Dryer suite & presets
│   │   ├── crash_detection_override.cfg ← Tool crash detection overrides
│   │   └── tool_crash_cartographer.cfg  ← Cartographer crash safety
│   │
│   ├── toolchanger/          ← StealthChanger KTC-Easy toolchanger config
│   │   ├── toolchanger-config.cfg ← Dropoff/pickup paths & park coords
│   │   ├── tools/ (T0–T4.cfg)     ← Individual tool definitions (EBB36 pins, offsets)
│   │   └── readonly-configs/      ← Managed by KTC-Easy (DO NOT EDIT)
│   │
│   └── scripts/              ← Deployment & maintenance scripts
│       ├── install.sh        ← First-time install script (auto-excludes *.md)
│       ├── update.sh         ← Auto-backup & update pull script (excludes *.md)
│       └── cleanup-voron.sh  ← Maintenance & backup directory cleaner
│
├── Orca Config/              ← Custom OrcaSlicer machine & process profiles
│
└── extras/                   ← Documentation, backups, and engineering logs
    ├── backups/              ← Timestamped configuration backups (Git tracked)
    ├── Nhat-ky-chinh-sua/    ← Daily engineering change logs (Vietnamese)
    ├── pictures/             ← Hardware photos and schematics
    ├── axiscope-cartographer/← Axiscope & Cartographer calibration logs
    └── logs/                 ← Klippy and Moonraker runtime logs
```

### Quick Commands (SSH)

* **First-Time Install:**
  ```bash
  cd /tmp && git clone git@github.com:IDcrazy123/All-Config-Voron.git
  cd All-Config-Voron && bash "Voron 5 Tool/config/scripts/install.sh"
  sudo systemctl restart moonraker klipper
  ```

* **Pull Updates from GitHub:**
  ```bash
  cd ~/printer_data/config && bash scripts/update.sh
  sudo systemctl restart moonraker klipper
  ```
  *(Creates an automatic backup under `~/printer_data/config_backups/` before applying updates).*

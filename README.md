# Voron 2.4 StealthChanger (5-Tool)

Production-ready Klipper/Moonraker configuration for a **Voron 2.4 350mm** running a **5-head StealthChanger** system.

---

## 🛠️ Hardware Stack

| Component | Specification | Interface |
| :--- | :--- | :--- |
| **Printer** | Voron 2.4 350mm — CoreXY | — |
| **Mainboard** | BTT Manta M8P V2.0 + CM4 | CAN Bridge `mcu` |
| **Toolheads** | 5× StealthChanger Toolhead (T0–T4) | EBB36 V1.2 via CAN bus |
| **Hotends** | TZ V6 2.0 (×5) | EBB36 Heater |
| **Extruders** | WW BMG (×5) | EBB36 TMC2209 |
| **Bed Probe / Z Homing** | Cartographer V3 (Touch + Scan mode) | CAN bus `cartographer` |
| **Z-Offset Calibrator** | SexBolt / SexBall — **Temporary mount only during `CALIBRATE_ALL_OFFSETS`** | Manta M8P `PF4` (M1-STOP) |
| **Accelerometer** | ADXL345 on each EBB36 + on Cartographer V3 | SPI |
| **Chamber Sensor** | Generic 3950 NTC | Manta M8P `PB1` (THB) |
| **Screen** | KlipperScreen (language: vi) | — |
| **Slicer** | OrcaSlicer (Multi-Color / Multi-Tool) | — |

> [!NOTE]
> **Cartographer V3** handles all Z homing and bed leveling during printing (Touch/Scan).
> **SexBolt/SexBall** is a *calibration-only* reference probe — inserted temporarily into the M1-STOP port when running `CALIBRATE_ALL_OFFSETS` to measure XYZ offsets between tools. It is **not present during normal printing**.

---

## 📂 Repository Layout

```
Voron 5 Tool/
├── config/                   ← Active Klipper config (synced to ~/printer_data/config)
│   ├── printer.cfg           ← Main config (includes, printer kinematics, SAVE_CONFIG block)
│   ├── Printer-Setup/        ← Hardware, probe, fans, input shaper, macros
│   ├── toolchanger/          ← StealthChanger KTC-Easy config & tool definitions (T0–T4)
│   │   ├── tools/            ← T0.cfg … T4.cfg (EBB36 extruder, fans, offsets per tool)
│   │   └── readonly-configs/ ← Auto-managed by klipper-toolchanger-easy (DO NOT EDIT)
│   └── scripts/              ← install.sh, update.sh, cleanup scripts
└── extras/
    ├── backups/              ← Local config backups (gitignored)
    ├── Nhat-ky-chinh-sua/    ← Daily change logs (Vietnamese)
    └── logs/                 ← klippy.log / moonraker.log (manual copy for analysis)
```

---

## 🚀 Setup & Updates

> [!WARNING]
> Do not copy files directly into `~/printer_data/config`. Use the scripts below.
>
> This repository is a **full production config bundle**, not a standalone Klipper starter pack.
> On a fresh printer that only has Klipper installed, this repo will **not** work until the required
> dependencies are installed first, including:
> - `klipper-toolchanger-easy`
> - Cartographer / Cartographer plugin support
> - `Klippain-ShakeTune`
> - any printer-specific CAN / toolhead / webcam dependencies required by your hardware
>
> The install/update scripts in this repo only copy configuration files. They do **not** install plugins.
> Install those platform dependencies first, then deploy this repo's `config/` files.

### Required Dependencies

Install these first on a fresh Klipper machine:

| Component | Install / Docs |
| :--- | :--- |
| `klipper-toolchanger-easy` | [GitHub install docs](https://github.com/jwellman80/klipper-toolchanger-easy) |
| Cartographer / Cartographer plugin | [Cartographer3D org](https://github.com/Cartographer3D) and [Cartographer plugin repo](https://github.com/Cartographer3D/cartographer3d-plugin) |
| `Klippain-ShakeTune` | [GitHub install docs](https://github.com/Frix-x/klippain-shaketune) |

If you prefer SSH install commands, use the vendor docs above. The important part is to have these dependencies working **before** applying this repo's `config/`.

Quick SSH references:

```bash
# klipper-toolchanger-easy
cd ~
git clone https://github.com/jwellman80/klipper-toolchanger-easy.git
cd ~/klipper-toolchanger-easy
./install.sh

# Klippain-ShakeTune
wget -O - https://raw.githubusercontent.com/Frix-x/klippain-shaketune/main/install.sh | bash
```

### First Install (SSH to Printer)
```bash
cd /tmp && git clone git@github.com:Batcandoionline/All-Config-Voron.git
cd All-Config-Voron && bash config/scripts/install.sh
```
Recommended order on a new machine:
1. Install Klipper and the printer base OS image.
2. Install external dependencies used by this config, especially the toolchanger and probe plugins.
3. Copy this repository's `config/` into `~/printer_data/config` with `install.sh`.
4. Restart `moonraker` and `klipper`.
5. Run `FIRMWARE_RESTART` in Mainsail and verify all macros, toolheads, and probes load cleanly.

*If any dependency is missing, Klipper may fail to load sections from this repo and the printer will not become ready.*

### Pull Updates (After GitHub Push)
```bash
cd ~/printer_data/config && bash scripts/update.sh
```
*Creates a timestamped backup under `~/printer_data/config_backups/` before applying. Use this only after the same dependencies are already present on the machine.*

---

## 📐 Calibration Workflows

### A. Z-Offset for All Tools (SexBolt / SexBall)
Run after any mechanical change (hotend swap, dock adjustment):

> [!IMPORTANT]
> **Insert the SexBolt/SexBall into the M1-STOP port** before starting. Remove it after calibration completes.

```gcode
G28
QUAD_GANTRY_LEVEL
CALIBRATE_ALL_OFFSETS    ; probes T0–T4 sequentially, saves XYZ offsets to printer.cfg
FIRMWARE_RESTART
CHECK_OFFSETS            ; verify saved values
```

### B. First-Layer Fine-Tuning (Per Tool)
Adjust `gcode_z_offset` for any individual tool directly from KlipperScreen (Live Adjust Z) during a first-layer test print. The value is persisted to the `#*# [tool Tn]` block in `printer.cfg` by `SAVE_CONFIG`.

### C. Bed Mesh
```gcode
G28
QUAD_GANTRY_LEVEL
BED_MESH_CALIBRATE       ; runs adaptive mesh (55×55 probe points, adaptive margin 10mm)
```

---

## 🛡️ Dev & AI Guidelines

- **Backup first:** Always create `extras/backups/pre-[task]-[YYYYMMDD]-[HHmmss]/` before modifying any `.cfg` file.
- **Do not touch `readonly-configs/`:** Files there are auto-managed by the KTC-Easy plugin.
- **Git hygiene:** Do not commit `extras/logs/`, `extras/backups/`, or `printer-*.cfg` temp files.
- **Rules entry:** See [`.agents/AGENTS.md`](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/.agents/AGENTS.md) for full AI assistant rules.

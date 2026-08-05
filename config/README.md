# Config — Voron 2.4 StealthChanger (5-Tool)

This directory is the **active Klipper configuration payload**. Its contents are deployed directly to `~/printer_data/config` on the printer via `scripts/install.sh` and `scripts/update.sh`.

> [!WARNING]
> Do not copy the repository root directly into `~/printer_data/config`. Use `scripts/install.sh` or `scripts/update.sh`.

---

## 📂 Directory Structure

```
config/
├── printer.cfg                   ← Main entry point (includes sub-configs, kinematics, SAVE_CONFIG block)
├── KlipperScreen.conf            ← KlipperScreen settings (language: vi, screen blanking)
├── moonraker.conf                ← Moonraker API server & update manager config
├── crowsnest.conf                ← Camera streaming config (WebRTC / MJPEG)
├── mainsail.cfg                  ← Mainsail web interface macros
│
├── Printer-Setup/                ← Hardware, probe, fans, input shaper & macros
│   ├── hardware.cfg              ← MCU definitions (Manta M8P V2 + Cartographer), X/Y/Z steppers, bed heater, chamber sensor
│   ├── probe-mesh.cfg            ← Cartographer V3 touch/scan probe parameters, adaptive bed mesh (55×55)
│   ├── calibration.cfg           ← Thermal calibration parameters, SexBolt workflow helpers
│   ├── fans-leds.cfg             ← Enclosure/CM4 fans, toolhead NeoPixels, LED status macros
│   ├── input-shaper.cfg          ← Global input shaper defaults (per-tool overrides in T0–T4.cfg)
│   ├── nozzle-clean.cfg          ← Bambu A1 silicone brush & bucket nozzle cleaning macros (`CLEAN_NOZZLE`)
│   ├── prime-lines.cfg           ← Per-tool prime line macros (T0–T4)
│   ├── print-macros.cfg          ← PRINT_START, PRINT_END, G32, idle timeout, exclude object
│   ├── crash_detection_override.cfg ← Tool crash detection macro overrides
│   └── tool_crash_cartographer.cfg  ← Cartographer-assisted tool crash protection
│
├── toolchanger/                  ← StealthChanger KTC-Easy config & tool definitions
│   ├── toolchanger-config.cfg    ← StealthChanger motion paths, SexBolt position, [tools_calibrate]
│   ├── tools/
│   │   ├── T0.cfg                ← EBB36 V1.2 (EBB0), extruder, fans, dock coords, input shaper
│   │   ├── T1.cfg                ← EBB36 V1.2 (EBB1)
│   │   ├── T2.cfg                ← EBB36 V1.2 (EBB2)
│   │   ├── T3.cfg                ← EBB36 V1.2 (EBB3)
│   │   └── T4.cfg                ← EBB36 V1.2 (EBB4)
│   └── readonly-configs/         ← Auto-managed by klipper-toolchanger-easy (DO NOT EDIT)
│
└── scripts/                      ← Deployment and maintenance scripts
    ├── install.sh                ← First-time install script
    ├── update.sh                 ← Pull & apply updates (auto-backup before applying)
    └── cleanup-voron.sh          ← Clean up old scattered backup directories
```

---

## 🛠️ Hardware Specification & Pinout Reference

| Component | Specification | Interface / Pin Assignment |
| :--- | :--- | :--- |
| **Mainboard** | BTT Manta M8P V2.0 + CM4 | CAN Bridge `mcu` (`canbus_uuid: 19b203d75137`) |
| **Toolhead MCUs** | 5× BTT EBB36 V1.2 | CAN bus (`EBB0`–`EBB4`) |
| **Z Homing & Probe** | Cartographer V3 (Touch + Scan) | CAN bus `cartographer` (`canbus_uuid: da13d909ce34`) |
| **Z-Offset Sensor** | SexBolt / SexBall (Calibration only) | Manta M8P `PF4` (M1-STOP port) |
| **Nozzle Cleaner** | Bambu A1 Silicone Pad + Bucket | Bucket ($X=320, Y=-8$), Pad ($X: 277 \rightarrow 312$, $Y: -7 \rightarrow -10$, $Z=1.2\text{mm}$) |
| **Chamber Thermistor** | Generic 3950 100K NTC | Manta M8P `PB1` (THB port) |
| **Bed Heater Thermistor** | NTC 100K MGB18-104F39050L32 | Manta M8P `PB0` / Heater `PA1` |
| **X / Y Steppers** | 0.9° NEMA17 | `stepper_x` (PF0 endstop), `stepper_y` (PF1 endstop, `position_min: -10`) |
| **Z Steppers (4×)** | CoreXY Z Drive (80:16 ratio) | `stepper_z` (PG9), `stepper_z1` (PB4), `stepper_z2` (PG13), `stepper_z3` (PB8) |

---

## 🧼 Nozzle Cleaner Macro Parameters (`nozzle-clean.cfg`)

- **Purge Bucket:** $X = 320.0$, $Y = -8.0$
- **Silicone Brush Range:** $X: 277.0 \rightarrow 312.0$, $Y: -7.0 \rightarrow -10.0$ (Center $Y = -8.0$)
- **Cleaning Contact Height:** $Z = 1.2\text{mm}$
- **Circle Arc Radius (`circle_r`):** $1.5\text{mm}$ (Min Y = $-9.5\text{mm}$, safely above `position_min: -10`)

```gcode
CLEAN_NOZZLE                            ; Wipe nozzle at 150°C (default in PRINT_START)
PURGE_AND_CLEAN PURGE=15 PURGE_TEMP=240  ; Purge 15mm @ 240°C into bucket -> cool down -> wipe
```

---

## 🚀 Deployment & Updates

### First-Time Install
```bash
cd /tmp && git clone git@github.com:IDcrazy123/All-Config-Voron.git
cd All-Config-Voron && bash config/scripts/install.sh
sudo systemctl restart moonraker klipper
```

### Pull & Apply Updates
```bash
cd ~/printer_data/config && bash scripts/update.sh
sudo systemctl restart moonraker klipper
```

---

## ⚠️ Dev Guidelines
- Always create a backup in `extras/backups/pre-[task]-[YYYYMMDD]-[HHmmss]/` before modifying configuration files.
- Do **not** edit files inside `toolchanger/readonly-configs/` — they are managed by the `klipper-toolchanger-easy` plugin.

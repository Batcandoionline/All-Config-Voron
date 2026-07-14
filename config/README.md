# Config — Voron 2.4 StealthChanger (5-Tool)

This directory is the **active Klipper configuration payload**. Contents are synced to `~/printer_data/config` on the printer via the install/update scripts.

> [!WARNING]
> Do not copy the repository root directly into `~/printer_data/config`. Use the scripts in `scripts/` below.

---

## 📂 Directory Layout

```
config/
├── printer.cfg                   ← Main entry point (includes all sub-configs, SAVE_CONFIG block)
├── KlipperScreen.conf            ← KlipperScreen settings (language: vi, screen blanking)
├── moonraker.conf                ← Moonraker API server config
├── crowsnest.conf                ← Camera streaming config
├── mainsail.cfg                  ← Mainsail web interface macros
│
├── Printer-Setup/
│   ├── hardware.cfg              ← MCU, steppers X/Y/Z×4, bed heater, chamber sensor
│   ├── probe-mesh.cfg            ← Cartographer V3 config, bed mesh (55×55), ADXL345
│   ├── calibration.cfg           ← Calibration temperatures, SexBolt workflow helpers
│   ├── fans-leds.cfg             ← Controller/CM4/enclosure fans, toolhead NeoPixels, LED states
│   ├── input-shaper.cfg          ← Input shaper defaults (per-tool overrides in T0–T4.cfg)
│   ├── nozzle-clean.cfg          ← Nozzle cleaning macros
│   ├── prime-lines.cfg           ← Prime line macros per tool
│   ├── print-macros.cfg          ← PRINT_START / PRINT_END, G32, idle timeout, exclude object
│   ├── crash_detection_override.cfg  ← Tool crash detection (Cartographer + SexBall)
│   └── tool_crash_cartographer.cfg   ← Cartographer-specific crash detection integration
│
├── toolchanger/
│   ├── toolchanger-config.cfg    ← StealthChanger motion paths, SexBolt position, [tools_calibrate]
│   ├── tools/
│   │   ├── T0.cfg                ← EBB36 V1.2 (EBB0), extruder, fans, dock coords, input shaper
│   │   ├── T1.cfg                ← EBB36 V1.2 (EBB1)
│   │   ├── T2.cfg                ← EBB36 V1.2 (EBB2)
│   │   ├── T3.cfg                ← EBB36 V1.2 (EBB3)
│   │   └── T4.cfg                ← EBB36 V1.2 (EBB4)
│   └── readonly-configs/         ← Auto-managed by klipper-toolchanger-easy. DO NOT EDIT.
│
└── scripts/
    ├── install.sh                ← First-time install
    ├── update.sh                 ← Pull & apply updates (auto-backup before applying)
    └── cleanup-voron.sh          ← Clean up old scattered backup directories
```

---

## 🚀 First-Time Install

SSH into the printer, then:

```bash
cd /tmp
git clone git@github.com:IDcrazy123/All-Config-Voron.git
cd All-Config-Voron
bash config/scripts/install.sh
```

The installer backs up the existing `~/printer_data/config` before copying this `config/` into place.

After install, restart services:

```bash
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

Then open Mainsail and run `FIRMWARE_RESTART`.

---

## 🔄 Updating Configuration

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

- Creates a timestamped backup under `~/printer_data/config_backups/config-YYYYMMDD-HHMMSS/` before pulling.
- Retains the 10 newest backups by default. Override: `BACKUP_KEEP=20 bash scripts/update.sh`

**Manual restore:**
```bash
rsync -a --delete ~/printer_data/config_backups/config-YYYYMMDD-HHMMSS/ ~/printer_data/config/
sudo systemctl restart klipper
```

**Cleanup old backup folders:**
```bash
bash scripts/cleanup-voron.sh          # dry-run
bash scripts/cleanup-voron.sh --apply  # apply
```

---

## 🛠️ Hardware Reference

| Component | Specification | Interface |
| :--- | :--- | :--- |
| **Mainboard** | BTT Manta M8P V2.0 + CM4 | CAN Bridge — `canbus_uuid: 19b203d75137` |
| **Toolheads** | 5× StealthChanger (T0–T4) | 5× EBB36 V1.2 via CAN bus |
| **Hotends** | TZ V6 2.0 ×5 | EBB36 heater pin `PB13` |
| **Extruders** | WW BMG ×5 | EBB36 TMC2209 |
| **Bed Probe / Z Homing** | Cartographer V3 — Touch + Scan | CAN — `canbus_uuid: da13d909ce34` |
| **Z-Offset Calibrator** | SexBolt / SexBall (temporary, calibration only) | Manta M8P `PF4` (M1-STOP) |
| **Accelerometers** | ADXL345 on each EBB36 + built-in on Cartographer | SPI |
| **Bed Heater** | NTC 100K MGB18-104F39050L32 | Manta M8P `PB0` / `PA1` |
| **Chamber Sensor** | Generic 3950 NTC | Manta M8P `PB1` (THB) |
| **Kinematics** | CoreXY, max 300 mm/s, max 4000 mm/s² | — |
| **Build Volume** | 348×336×347 mm (usable) | — |

> [!NOTE]
> **Cartographer V3** is the Z virtual endstop (`endstop_pin: probe:z_virtual_endstop`) and runs bed mesh during printing.
> **SexBolt/SexBall** plugs into `PF4` only during `CALIBRATE_ALL_OFFSETS` to measure XYZ offsets between tools. **Not present during normal printing.**

---

## ⚠️ Safety Notes

- Always create a backup before modifying any live config (see `../extras/backups/`).
- Do not use this config on a different printer without verifying CAN UUIDs, pin assignments, dock coordinates, and probe settings.
- After any update, test tool pickup/dropoff manually before starting a print.
- Do **not** edit files inside `toolchanger/readonly-configs/` — they are auto-managed by the KTC-Easy plugin.

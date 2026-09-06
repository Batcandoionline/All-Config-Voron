# Production Klipper Configuration Payload

[English](README.md) | [Tiếng Việt](README.vi.md)

This directory contains the operational Klipper configuration deployed to `~/printer_data/config` on the printer. Documentation (`*.md`) files are excluded from active deployment.

---

## 1. Include Chain (`printer.cfg`)

The root `printer.cfg` acts as the master coordinator and loads modules in the following order:

```ini
[include mainsail.cfg]                                          # Web UI macros
[include toolchanger/readonly-configs/toolchanger-include.cfg]  # KTC-Easy core (symlink)
[include Printer-Setup/calibration-probe.cfg]                   # Cartographer probe & mesh
[include Printer-Setup/ktamv.cfg]                               # kTAMV camera backend (XY-only)
[include Printer-Setup/hardware.cfg]                            # Steppers, TMC drivers, heaters
[include Printer-Setup/fans-leds.cfg]                           # CPAP, chamber fans & LEDs
[include Printer-Setup/input-shaper.cfg]                        # Unified resonance filters
[include Printer-Setup/nozzle-clean.cfg]                        # Silicone brush nozzle wipe
[include Printer-Setup/prime-lines.cfg]                         # Tool-specific prime lines
[include Printer-Setup/print-macros.cfg]                        # Core print start/end macros
[include Printer-Setup/filament-dryer.cfg]                      # Bed-based filament drying
[include Printer-Setup/test-speed.cfg]                          # TEST_SPEED & TEST_Z_SPEED
[include Printer-Setup/tool-temp-bench.cfg]                      # MEASURE_TOOL_HEATUP hotend heating rate
[include Printer-Setup/tool-crash.cfg]                          # Tool drop/crash detection
```

---

## 2. Directory & Component Ownership

| Path | Owner | Description & Rules |
| :--- | :--- | :--- |
| `printer.cfg` | User / Git | Kinematics, limits, MCU UUID, includes. Contains live `#*# <SAVE_CONFIG>` block. |
| `Printer-Setup/*.cfg` | User / Git | Modular printer subsystems, safety macros, and hardware mappings. |
| `toolchanger/toolchanger-config.cfg` | User / Git | StealthChanger dock coordinates, pickup/dropoff speeds, LED hooks. |
| `toolchanger/tools/T0.cfg` ... `T4.cfg` | User / Git | Extruder motor profiles, nozzle offsets, and standby temperatures. |
| `toolchanger/readonly-configs/` | **KTC-Easy** | **DO NOT EDIT.** Installer-managed symlinks to `~/klipper-toolchanger-easy/`. |
| `scripts/*.sh` | User / Git | Deployment (`install.sh`), updater (`update.sh`), maintenance (`cleanup-voron.sh`). |
| `moonraker.conf` | Moonraker / Git | API server settings, security, and Update Manager components. |
| `crowsnest.conf`, `KlipperScreen.conf` | System / Git | WebRTC webcam streaming and touchscreen display configs. |

---

## 3. Hardware & Kinematics Mapping

| Function | Hardware / Pin Assignment | Operating Limits |
| :--- | :--- | :--- |
| **Main MCU** | BTT Manta M8P V2.0 (`19b203d75137`) | CANbus 1 Mbps |
| **Probe / Z Homing** | Cartographer V3 (`da13d909ce34`) | Touch homing + 55×55 Scan adaptive bed mesh |
| **Input Shaper Sensor** | Onboard ADXL345 on Cartographer | Shuttle-mounted; X: MZV 43.6 Hz, Y: MZV 33.4 Hz |
| **CoreXY Kinematics** | Stepper X: `PE6` / PF0 endstop; Stepper Y: `PE2` / PF1 endstop | Max Vel: 350 mm/s (tested 500), Accel: 7000 mm/s² (tested 15k) |
| **Quad Z Gantry** | Z0: `PG9`, Z1: `PB4`, Z2: `PG13`, Z3: `PB8` | Max Z Vel: 70 mm/s (tested 80), Z Accel: 900 mm/s² (tested 1k) |
| **Heated Bed** | Heater `PA1`, Sensor `PB0` (NTC 100K) | 220V 1000W AC, max 120 °C |
| **Chamber Sensor / Fan** | Chamber Thermistor: `PB1` (Generic 3950); Bed Fan: `PF8` | Auto chamber temperature control |
| **Enclosure / CM4 Fans** | CM4 Fan: `PF7`, Enclosure Fan: `PF9`, Chamber LEDs: `PD15` | Temperature-regulated chassis cooling |
| **Tool Extruders & Fans** | 5x EBB36 V1.2 CAN boards; Hotend fan `PA0`, Part fan `PA1` | Extruder: TMC2209 at 0.6A; Part fans dynamically managed by `M106` |

---

## 4. 1-Click Mainsail Update & Lean Deployment

### 4.1. One-Time Setup on Printer (Sparse Checkout - Saves 97.7% Disk Space)
To avoid downloading 600MB+ of PC backups and git history, run via SSH once:
```bash
git clone --depth=1 --filter=blob:none --sparse https://github.com/IDcrazy123/All-Config-Voron.git ~/All-Config-Voron
cd ~/All-Config-Voron
git sparse-checkout set config
sudo systemctl restart moonraker
```

### 4.2. Daily Operations
- Push commits from PC (`git push origin main`).
- In **Mainsail > Settings > Update Manager**, click **Update** on `All-Config-Voron`.
- Moonraker pulls changes, executes `install.sh` (which verifies KTC symlinks, retains only the 5 most recent backups, purges markdown files, and deploys configs), then restarts Klipper.

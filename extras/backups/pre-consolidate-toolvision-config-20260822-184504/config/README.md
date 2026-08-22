# Config — Voron 2.4 StealthChanger (5-Tool)

This directory is the **active Klipper configuration payload**. Its contents are deployed directly to `~/printer_data/config` on the printer via `scripts/install.sh` and `scripts/update.sh`.

> [!NOTE]
> When deployed via `install.sh` or `update.sh`, markdown files (including this `README.md`) are automatically excluded to keep Klipper's configuration environment clean.

---

## 📂 Directory Structure

```
config/
├── printer.cfg                   ← Main entry point (includes sub-configs, kinematics, SAVE_CONFIG block)
├── KlipperScreen.conf            ← KlipperScreen settings (language: vi, screen blanking)
├── moonraker.conf                ← Moonraker API server; includes the ToolVision updater generated on the printer
├── crowsnest.conf                ← Camera streaming config (WebRTC)
├── mainsail.cfg                  ← Mainsail web interface macros
│
├── Printer-Setup/                ← Hardware, probe, fans, input shaper & macros
│   ├── hardware.cfg              ← MCU definitions (Manta M8P V2 + Cartographer), X/Y/Z steppers, bed heater, chamber sensor
│   ├── calibration-probe.cfg     ← Cartographer/mesh plus Tool Vision PF2 ownership and Axiscope rollback data
│   ├── fans-leds.cfg             ← Enclosure/CM4 fans, toolhead NeoPixels, LED status macros
│   ├── input-shaper.cfg          ← Global input shaper defaults (per-tool overrides in T0–T4.cfg)
│   ├── nozzle-clean.cfg          ← Bambu A1 silicone brush & bucket nozzle cleaning macros (`CLEAN_NOZZLE`)
│   ├── prime-lines.cfg           ← Per-tool prime line macros (T0–T4)
│   ├── print-macros.cfg          ← PRINT_START, PRINT_END, G32, single-prompt Filament Dryer presets
│   └── tool-crash.cfg            ← tool_crash detector, KTC routing, and safe-pause handler
│
├── toolchanger/                  ← StealthChanger KTC-Easy config & tool definitions
│   ├── toolchanger-config.cfg    ← StealthChanger motion paths, switch position, toolchanger logic
│   ├── tools/
│   │   ├── T0.cfg                ← EBB36 V1.2 (EBB0), extruder, fans, dock coords, input shaper
│   │   ├── T1.cfg                ← EBB36 V1.2 (EBB1)
│   │   ├── T2.cfg                ← EBB36 V1.2 (EBB2)
│   │   ├── T3.cfg                ← EBB36 V1.2 (EBB3)
│   │   └── T4.cfg                ← EBB36 V1.2 (EBB4)
│   └── readonly-configs/         ← Auto-managed by klipper-toolchanger-easy (DO NOT EDIT)
│
├── Tool-Vision/
│   └── tool_vision.cfg           ← Active ToolVision 3 teach-once config; PF2 switch ready, camera setup pending
│
└── scripts/                      ← Deployment and maintenance scripts
    ├── install.sh                ← First-time install script; validates/applies the reviewed tool_crash runtime patch
    ├── patches/                  ← Minimal machine runtime patches applied by install.sh
    ├── update.sh                 ← Pull & apply updates (auto-backup & excludes *.md)
    └── cleanup-voron.sh          ← Clean up legacy backup directories
```

---

## 🛠️ Hardware Specification & Pinout Reference

| Component | Specification | Interface / Pin Assignment |
| :--- | :--- | :--- |
| **Mainboard** | BTT Manta M8P V2.0 + CM4 | CAN Bridge `mcu` (`canbus_uuid: 19b203d75137`) |
| **Toolhead MCUs** | 5× BTT EBB36 V1.2 | CAN bus (`EBB0`–`EBB4`) |
| **Z Homing & Probe** | Cartographer V3 fw6.1.0 (Touch + Scan) | CAN bus `cartographer` (`canbus_uuid: da13d909ce34`) |
| **Tool-Offset Sensor** | ToolVision 3.2.2 active; removable MF-500 camera + PF2 microswitch | Manta M8P `PF2` (GND + `^PF2`); station positions are learned into printer-local state |
| **Nozzle Cleaner** | Bambu A1 Silicone Pad + Bucket | Bucket ($X=320, Y=-8$), Pad ($X: 277 \rightarrow 312$, $Y: -7 \rightarrow -10$, $Z=1.2\text{mm}$) |
| **Chamber Thermistor** | Generic 3950 100K NTC | Manta M8P `PB1` (THB port) |
| **Bed Heater & SSR** | AC Silicone 1000W + SSR | Manta M8P `PB0` (NTC 100K MGB18) / Heater `PA1` |
| **Under-Bed Fan** | Chamber Circulation Fan (`bed_fan`) | Manta M8P `PF8` (Fan3) |
| **Chamber Lighting** | 40× WS2812B Neopixel Strip | Manta M8P `PD15` (GRB order) |
| **X / Y Steppers** | 0.9° NEMA17 | `stepper_x` (PF0 endstop), `stepper_y` (PF1 endstop, `position_min: -10`) |
| **Z Steppers (4×)** | CoreXY Z Drive (80:16 ratio) | `stepper_z` (PG9), `stepper_z1` (PB4), `stepper_z2` (PG13), `stepper_z3` (PB8) |

---

## 🧼 Nozzle Cleaner Macro Parameters (`nozzle-clean.cfg`)

- **Purge Bucket:** $X = 320.0$, $Y = -8.0$
- **Silicone Brush Range:** $X: 277.0 \rightarrow 312.0$, $Y: -7.0 \rightarrow -10.0$ (Center $Y = -8.0$)
- **Cleaning Contact Height:** $Z = 1.2\text{mm}$
- **Circle Arc Radius (`circle_r`):** $1.5\text{mm}$ (Min Y = $-9.5\text{mm}$, safely above `position_min: -10`)

```gcode
CLEAN_NOZZLE                             ; Wipe nozzle at 150°C (default in PRINT_START)
PURGE_AND_CLEAN PURGE=15 PURGE_TEMP=240   ; Purge 15mm @ 240°C into bucket -> cool down -> wipe
```

---

## 🚀 Deployment & Updates

### First-Time Install Without a Persistent Clone
```bash
tmp_dir="$(mktemp -d /tmp/all-config-voron.XXXXXX)"
curl -fsSL https://github.com/IDcrazy123/All-Config-Voron/archive/refs/heads/main.tar.gz \
  | tar -xz -C "${tmp_dir}" --strip-components=1
bash "${tmp_dir}/config/scripts/install.sh"
rm -rf -- "${tmp_dir}"
sudo systemctl restart moonraker klipper
```

### Pull & Apply Updates
```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart moonraker klipper
```

`update.sh` downloads a temporary All-Config source archive, creates a backup,
deploys the managed payload, and removes the archive. All-Config does not keep a
Git clone on the printer. ToolVision is different by design: its active v3.2.2
runtime is the persistent `~/Tool-Vision` Git checkout and is updated through
Mainsail's Update Manager. This repository synchronizes only the editable
`Tool-Vision/tool_vision.cfg`; the ToolVision installer owns and regenerates
`Tool-Vision/moonraker_update_manager.conf`, which deployment preserves.

Generated runtime data is grouped under `Generated-Data/ToolVision/` and
`Generated-Data/ShakeTune/` on the printer. `install.sh` excludes the entire
`Generated-Data/` tree, while historical backups and downloaded config archives
are stored under `~/printer_data/config_backups/` rather than the config root.

`install.sh` also preflights `scripts/patches/tool_crash-active-tool-validation.patch`
against the installed `~/klipper/klippy/extras/tool_crash.py`. It skips an
already-patched runtime, backs up an unpatched matching source before applying,
and refuses deployment when the installed upstream source is incompatible.

---

## ⚠️ Dev Guidelines
- Always create a backup in `extras/backups/pre-[task]-[YYYYMMDD]-[HHmmss]/` before modifying configuration files.
- Do **not** edit files inside `toolchanger/readonly-configs/` — they are managed by the `klipper-toolchanger-easy` plugin.

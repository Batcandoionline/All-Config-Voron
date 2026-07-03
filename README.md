# Voron 2.4 StealthChanger (5-Tool)

A production-ready Klipper/Moonraker configuration for a **Voron 2.4 350mm** printer equipped with a **5-Tool StealthChanger** system.

---

## 🛠️ Hardware Stack

| Component | Specification | MCU / Pin |
| :--- | :--- | :--- |
| **Mainboard** | BTT Manta M8P V2.0 + CB1/CM4 | `mcu` (CAN Bridge) |
| **Toolheads** | 5x StealthChanger Toolheads (T0–T4) | 5x EBB36 V1.2 via CAN |
| **Bed Probe & Z Homing** | Cartographer V3 (Touch/Scan mode) | `cartographer` via CAN |
| **Z-Offset Calibrator** | SexBolt/SexBall (Temporary mount during calibration) | Pin `PF4` (M1-STOP) |
| **Extruders** | WW BMG Extruders | EBB Steppers |
| **Hotends** | TZ V6 2.0 Hotends | EBB Heaters |

---

## 📂 Repository Layout

*   [`config/`](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/config) — Active Klipper config (synced to printer's `~/printer_data/config`).
*   [`extras/`](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras) — Calibration logs, local backups, and helper scripts.

---

## 🚀 Setup & Updates

> [!WARNING]
> Do not copy files directly. Use the scripts below to prevent configuration loss.

### 1. Fresh Install (SSH to Printer)
```bash
cd /tmp && git clone git@github.com:Batcandoionline/All-Config-Voron.git
cd All-Config-Voron && bash config/scripts/install.sh
```
*Run `FIRMWARE_RESTART` in Mainsail after installation.*

### 2. Update Configuration (Pull changes from GitHub)
```bash
cd ~/printer_data/config && bash scripts/update.sh
```
*Creates an automatic backup under `~/printer_data/config_backups/` before pulling.*

---

## 📐 Quick SexBolt Calibration Workflow

Follow this to calibrate XYZ offsets for all tools relative to T0:

1. **Prep:** Ensure all tool nozzles are perfectly clean (plastic residue corrupts offsets).
2. **Home & Align:**
   ```gcode
   G28
   QUAD_GANTRY_LEVEL
   ```
3. **Calibrate:**
   ```gcode
   CALIBRATE_ALL_OFFSETS
   ```
   *(Macro probes T0–T4 sequentially and automatically saves offsets to `printer.cfg`)*
4. **Apply & Verify:**
   ```gcode
   FIRMWARE_RESTART
   CHECK_OFFSETS
   ```

---

## 🛡️ Dev Guidelines (For AI & Maintainers)
- **Always Backup:** Run a local backup to `extras/backups/pre-[task]-[date]/` before modifying configurations.
- **Git Hygiene:** Do not commit logs, ShakeTune results, or temporary Klipper backups.
- **Rules Entry:** See [`.agents/AGENTS.md`](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/.agents/AGENTS.md) for full assistant rules.

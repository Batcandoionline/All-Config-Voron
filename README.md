# Voron 2.4 StealthChanger 5-Tool Configuration

Optimized Klipper/Moonraker configuration payload for a **Voron 2.4 StealthChanger** printer equipped with 5 independent toolheads.

## 🛠️ System Hardware
*   **Main Controller:** BTT Manta M8P V2.0 + Raspberry Pi CM4
*   **Toolhead Controllers:** 5x EBB36 V1.2 (CAN bus)
*   **Bed Probe:** Cartographer V3 CAN bus
*   **Toolhead Calibration:** SexBolt/SexBall mechanical probe (pin `PF4`/M1-STOP)
*   **Hotend & Extruder:** TZ V6 2.0 hotends + WW BMG extruders

---

## 📂 Repository Layout
*   `config/`: Main active configuration payload. This is synchronized to `~/printer_data/config` on the printer.
*   `extras/`: Reference manuals, images, sample G-codes, and local backups (not copied to the printer).

---

## 🚀 Installation & Update Instructions

> [!WARNING]
> Do not copy the repository root directly into `~/printer_data/config`. Use the scripts below to safely install or update configurations.

### 1. First-Time Installation (SSH to the printer)
```bash
cd /tmp
git clone git@github.com:Batcandoionline/All-Config-Voron.git
cd All-Config-Voron
bash config/scripts/install.sh
```
*(After the script completes, open the Mainsail/Fluidd web interface and run `FIRMWARE_RESTART`)*

### 2. Updating Configurations (After pushing changes to GitHub)
```bash
cd ~/printer_data/config
bash scripts/update.sh
```
*(The update script automatically creates a full backup under `~/printer_data/config_backups/config-YYYYMMDD-HHMMSS` before pulling and applying the new configuration)*

---

## 📐 Quick Calibration Workflow (SexBolt / SexBall)

To calibrate XYZ offsets for all tools relative to T0 after any mechanical adjustment:

1.  **Clean the Nozzles:** Thoroughly clean T0 and all other tool nozzles (plastic residue will corrupt the measurements).
2.  **Home & Level the Gantry:**
    ```gcode
    G28
    QUAD_GANTRY_LEVEL
    ```
3.  **Run Auto Calibration:**
    ```gcode
    CALIBRATE_ALL_OFFSETS
    ```
    *(The macro will probe T0 through T4 sequentially and automatically save the offsets)*
4.  **Restart & Verify:**
    ```gcode
    FIRMWARE_RESTART
    CHECK_OFFSETS
    ```

---

## 🛡️ Operational & Development Guidelines (For AI & Developers)
*   **Mandatory Backups:** Always create a backup directory under `extras/backups/pre-...` before modifying any configuration files.
*   **Keep Git Clean:** Do not commit logs, ShakeTune graphs (`ShakeTune_results`), or temporary Klipper backups (`printer-*.cfg`) to the main `config/` directory on GitHub.

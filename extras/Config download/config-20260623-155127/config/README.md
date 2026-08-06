# Voron Printer Config

Klipper configuration for a Voron 2.4 StealthChanger 5-tool setup.

This directory is the machine config payload. Its contents should be copied to:

```bash
~/printer_data/config
```

The parent repository also contains `extras/` reference files, so do not copy the repository root directly into `~/printer_data/config`.

## First-Time Install

SSH into the printer and run:

```bash
cd /tmp
git clone git@github.com:Batcandoionline/All-Config-Voron.git
cd All-Config-Voron
bash config/scripts/install.sh
```

The installer backs up the existing `~/printer_data/config` directory before copying this `config/` directory into place.

After install:

```bash
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

Then open Mainsail and run:

```gcode
FIRMWARE_RESTART
```

## Updating Later

From the printer:

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

The update script keeps a full backup under `~/printer_data/config_backups/config-YYYYMMDD-HHMMSS`, updates/clones the source repository at `~/All-Config-Voron`, then copies only `~/All-Config-Voron/config/` into `~/printer_data/config`.

By default it keeps the newest 10 update backups. Override that when needed:

```bash
BACKUP_KEEP=20 bash scripts/update.sh
```

Restore a backup manually:

```bash
rsync -a --delete ~/printer_data/config_backups/config-YYYYMMDD-HHMMSS/ ~/printer_data/config/
sudo systemctl restart klipper
```

Dry-run cleanup for old scattered backup folders:

```bash
bash scripts/cleanup-voron.sh
```

Apply cleanup after checking the listed paths:

```bash
bash scripts/cleanup-voron.sh --apply
```

## Current Machine

- Printer: Voron 2.4 StealthChanger
- Toolchanger: StealthChanger, 5 independent toolheads
- Frame: Voron 2.4 350 mm base frame with a StealthChanger top extension adding 250 mm of height
- Motion system: CoreXY
- Main controller: BIGTREETECH Manta M8P V2.0 with Raspberry Pi CM4
- Toolhead controllers: 5x BIGTREETECH EBB36 V1.2
- CAN devices: Manta M8P, Cartographer V3, and all five EBB toolhead boards
- Probe: Cartographer V3 mounted on the shuttle
- Toolhead hardware: TZ V6 2.0 hotends with WW BMG extruders

## Safety Notes

- Always keep a backup before replacing a live printer config.
- Do not run this configuration on a different printer without checking pins, CAN UUIDs, tool dock coordinates, bed size, and probe settings.
- After any update, test tool pickup/dropoff manually before starting a print.

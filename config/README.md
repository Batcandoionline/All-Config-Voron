# Stealth-changer-config

Klipper configuration for a Voron 2.4 StealthChanger 5-tool setup.

## Source

This repository is based on the working printer configuration from the Batcandoionline Voron 2.4 StealthChanger machine.

Main upstream projects used by this configuration:

- Klipper: <https://github.com/Klipper3d/klipper>
- Moonraker: <https://github.com/Arksine/moonraker>
- Mainsail: <https://github.com/mainsail-crew/mainsail>
- Klipper ToolChanger Easy: <https://github.com/jwellman80/klipper-toolchanger-easy>
- Cartographer: <https://docs.cartographer3d.com/>
- StealthChanger documentation: <https://stealthchanger.com/>
- Tool crash detection: <https://github.com/cekim-git/tool_crash>
- DraftShift StealthChanger references: <https://github.com/DraftShift>
- Klippain Shake&Tune resonance measurement: <https://github.com/Frix-x/klippain-shaketune>

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
- Toolhead sensors: tool presence detection pins, filament switch sensors, ADXL345 accelerometers, and 3-LED WS2812 chains on each tool
- Bed and chamber: 100K NTC bed thermistor, chamber thermistor on Manta THB, bed heater on Manta bed output
- Cooling and lighting: hotend fans, part cooling fans, electronics bay fans, chamber circulation fan, and 40-LED chamber light strip

## Repository Layout

This repository is designed to be cloned directly into:

```bash
~/printer_data/config
```

The root contains `printer.cfg`, `moonraker.conf`, `mainsail.cfg`, and the included config folders used by Klipper.

## First-Time Install On The Printer

SSH into the printer and run:

```bash
cd /tmp
git clone https://github.com/Batcandoionline/Stealth-changer-config.git
cd Stealth-changer-config
bash scripts/install.sh
```

The installer backs up the existing `~/printer_data/config` directory before replacing it with this repository.

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

If this repository is already installed at `~/printer_data/config`:

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

Or manually:

```bash
cd ~/printer_data/config
git pull
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

## Moonraker Update Manager

To make the config visible in Mainsail Update Manager, keep this section in `moonraker.conf`:

```ini
[update_manager stealth-changer-config]
type: git_repo
path: ~/printer_data/config
origin: https://github.com/Batcandoionline/Stealth-changer-config.git
primary_branch: main
managed_services: klipper
```

Moonraker can pull the repository from Update Manager. If `moonraker.conf` itself changes, restart Moonraker manually after the update.

## Safety Notes

- Always keep a backup before replacing a live printer config.
- Do not run this configuration on a different printer without checking pins, CAN UUIDs, tool dock coordinates, bed size, and probe settings.
- After any update, test tool pickup/dropoff manually before starting a print.
- Recommended toolchange smoke test:

```gcode
FIRMWARE_RESTART
INITIALIZE_TOOLCHANGER
T0
T1
T2
T3
T4
T0
```

# Production configuration payload

This directory is deployed to `~/printer_data/config` for the Voron 2.4 350
five-tool printer. Values describe the real machine; templates for other
hardware belong in the independent Tool Vision project, not in this payload.

## Include order

`printer.cfg` loads configuration in this order:

1. `mainsail.cfg`.
2. KTC-Easy `toolchanger/readonly-configs/toolchanger-include.cfg`.
3. `Printer-Setup/crash_detection_override.cfg`.
4. Calibration and installed hardware modules.
5. Probe, fan/LED, input-shaper, cleaning, prime, and print macros.
6. `Printer-Setup/tool_crash_cartographer.cfg` after all tool sections.

The Tool Vision include is commented. It must not be enabled while `[axiscope]`
is active.

## Ownership boundaries

| Path | Owner | Rule |
|---|---|---|
| `Printer-Setup/*.cfg` | This repository | Back up, review, deploy |
| `toolchanger/tools/T0.cfg` ... `T4.cfg` | This repository | Preserve measured pins/docks |
| `toolchanger/toolchanger-config.cfg` | This repository | User overrides only |
| `toolchanger/readonly-configs/` | KTC-Easy installer | Never edit or overwrite |
| `Tool-Vision/` on the Pi | Tool Vision installer/user | Preserved by deploy scripts |
| `printer.cfg` SAVE_CONFIG | Klipper | Preserve calibrated values |

The install/update scripts exclude `readonly-configs/` because current KTC-Easy
uses installer-managed links. A warning means the official KTC installer must
repair those links; copying tracked snapshots over them is not a repair.

## Measured hardware

| Component | Production configuration |
|---|---|
| Manta M8P V2 MCU | CAN `19b203d75137` |
| Cartographer V3 | CAN `da13d909ce34`, Touch threshold 1819 |
| Toolheads | EBB0..EBB4 UUIDs in `toolchanger/tools/T*.cfg` |
| X/Y limits | X `0..348`, Y `-10..336` |
| Bed | Heater `PA1`, MGB18 thermistor `PB0`, max 120 C |
| Chamber | Generic 3950 NTC `PB1` |
| Calibration switch | `^PF2`, measured X=68, Y=-10, Z=7 |
| Cartographer reference | Nozzle position `174,168` |
| Nozzle cleaner | Bucket X=320/Y=-8; brush X=277..312 near Y=-8 |

Klipper has no native `sensor_type: DHT22`; any future humidity sensor needs a
separately installed integration. Dryer macros only display humidity when an
existing runtime object actually exposes a `.humidity` field.

## Calibration backend

`Printer-Setup/calibration.cfg` currently enables Axiscope as a temporary
fallback. Tool Vision is staged, and legacy `tools_calibrate` is disabled.
The macros `CALIBRATE_ALL_OFFSETS`, `CALIBRATE_MOVE_OVER_PROBE`, and
`CALIBRATE_NOZZLE_PROBE_OFFSET` intentionally reject execution while the legacy
backend is absent instead of accessing undefined Klipper objects.

Read-only checks:

```gcode
CALIBRATION_STATUS
CHECK_OFFSETS
```

For Tool Vision, users manually measure both station coordinate sets and store
them in `Tool-Vision/tool_vision.cfg`. Camera coordinates must be measured after
placing the MF-500 on its keyed magnetic bed mount; switch coordinates are
measured by manually jogging T0 to the switch center/contact. No value is
derived from camera resolution, and native frames are not forced to 640x480.

## Crash detection

- `tool_crash_cartographer.cfg` configures `tool_crash` and its safe pause.
- `crash_detection_override.cfg` routes KTC-Easy start/stop calls to that plugin.
- The detector reads each tool's `detection_pin`, not Cartographer.
- A detected failure during a virtual-SD print pauses without an XYZ park move.
- Do not remove the override merely because the detector file exists; they have
  different responsibilities.

## Deploy

```bash
bash scripts/update.sh
```

Protected from rsync deletion/copy:

- `.codex-backups/`
- `.moonraker.conf.bkp`
- `Tool-Vision/`
- `Nhat-ky-chinh-sua/`
- `toolchanger/readonly-configs/`
- `README.md` and all `*.md`

After deployment, restart only when the machine is idle and heaters are off.
Parse success is not permission to home, probe, or toolchange unattended.

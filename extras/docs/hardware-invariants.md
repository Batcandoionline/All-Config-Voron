# Hardware preservation contract

Verified against the PC configuration and the live printer at `192.168.1.43`
on 2026-08-20. These values are machine data, not software defaults. A refactor
must preserve them unless the owner reports a physical hardware change and a
new backup is made first.

## Controller and probes

| Item | Locked value |
|---|---|
| Printer | Voron 2.4, 350 mm class |
| Controller/host | BTT Manta M8P V2 + CM4 |
| Main MCU CAN UUID | `19b203d75137` |
| CAN interface | `can0`, 1,000,000 bit/s |
| Cartographer CAN UUID | `da13d909ce34` |
| Cartographer firmware | 6.1.0 |
| Touch threshold | 1819 |
| Touch Z offset | -0.05 mm |
| Scan reference temperature | 42.44 C |
| Bed-mesh zero reference | nozzle X=174, Y=168 |
| Calibration switch | `^PF2`, current X=68, Y=-10, contact reference Z=7 |

## Five toolheads

All five tools use BTT EBB36 V1.2, TZ V6 2.0 hotends, and WW BMG extruders.

| Tool | CAN UUID | Presence pin | Dock X/Y/Z | Production X/Y/Z offset |
|---|---|---|---|---|
| T0 | `441e1484ac41` | `^!EBB0:PB6` | `30.20 / 1.30 / 343` | `0 / 0 / 0` |
| T1 | `6475b5b9e028` | `^!EBB1:PB6` | `104.00 / 1.10 / 343` | `-0.243 / -0.252 / +0.228` |
| T2 | `4ad9d622a836` | `^!EBB2:PB6` | `176.00 / 1.60 / 343` | `+0.746 / +0.086 / -0.295` |
| T3 | `c2465b7c36f8` | `^!EBB3:PB6` | `249.50 / 2.50 / 343` | `+0.304 / +0.449 / -0.268` |
| T4 | `28650279df58` | `^!EBB4:PB6` | `321.50 / 2.60 / 343` | `+0.041 / +0.352 / -0.014` |

## Motion and thermal hardware

| Item | Locked value |
|---|---|
| X travel | 0..348 mm, endstop PF0 |
| Y travel | -10..336 mm, endstop PF1 |
| Z travel | -5..347 mm, Cartographer virtual endstop |
| XY motors | 0.9 degree, 16 microsteps, 40 mm rotation distance |
| Z drive | 32 mm rotation distance, 80:16 ratio, four motors |
| Bed heater | 1000 W AC silicone pad through SSR control PA1 |
| Bed sensor | NTC 100K MGB18 on PB0 |
| Chamber sensor | Generic 3950 100K NTC on PB1 |
| Under-bed fan | PF8 |

## Mechanical stations

| Station | Locked/current value |
|---|---|
| Cleaner brush | X=277..312, Y near -8, contact Z=1.2 |
| Purge bucket | X=320, Y=-8 |
| Toolchange safe Y | 120 |
| Toolchange close Y | 30 |
| Toolchange fast speed | 15000 mm/min |
| Toolchange path speed | 900 mm/min |

Camera station coordinates are intentionally absent. The MF-500 normally views
the chamber and is placed on a keyed magnetic bed mount for calibration. The
user must manually determine and configure the station after physical mounting.

## Recovery source

The full pre-change PC, live-printer, and Tool Vision snapshots are stored in:

`extras/backups/pre-five-tool-rewrite-20260820-181903/`

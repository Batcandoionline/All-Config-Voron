# Voron 2.4 StealthChanger — five-tool production configuration

[English](README.md) | [Tiếng Việt](README.vi.md) | [Documentation index](extras/docs/README.md) | [Active config reference](config/README.md)

This repository contains the reviewed production configuration, deployment
scripts, OrcaSlicer profiles and operating notes for one specific Voron 2.4
350 mm CoreXY printer with a five-tool StealthChanger. It is not a generic
drop-in configuration.

> [!IMPORTANT]
> Hardware identifiers, motion limits, dock coordinates and offsets in this
> document are machine-specific. Read the source file named beside each value
> before adapting anything to another printer. Configuration state was reviewed
> again on 2026-08-24 from revision `1a09b7f`.

## Start here

| I want to… | Read or run |
| --- | --- |
| Understand the machine | [System overview](#system-overview) and [tool map](#tool-map) |
| Prepare a normal print | [Normal print workflow](#normal-print-workflow) |
| Find a Mainsail/Klipper command | [Operator macro reference](#operator-macro-reference) |
| Check current offsets without motion | `CHECK_OFFSETS` |
| Check the active calibration backend | `CALIBRATION_STATUS` |
| Use ToolVision | [ToolVision report-only calibration](#toolvision-report-only-calibration) |
| Clean or purge a nozzle | [Nozzle cleaning and prime lines](#nozzle-cleaning-and-prime-lines) |
| Dry filament on the bed | [Heated-bed filament dryer](#heated-bed-filament-dryer) |
| Update the printer configuration | [Install and update](#install-and-update) |
| Restore or clean backups | [Backups, rollback and cleanup](#backups-rollback-and-cleanup) |
| Diagnose a common fault | [Troubleshooting](#troubleshooting) |
| Edit this repository | [Safe contribution workflow](#safe-contribution-workflow) |

## Status vocabulary

Documentation uses the following labels deliberately:

- **Active:** loaded by `config/printer.cfg` or used by a tracked deployment
  script.
- **Observed:** confirmed in a dated printer session; it is evidence for this
  machine, not a universal hardware claim.
- **Development:** implemented in another branch/project but not deployed to
  this printer unless explicitly stated.
- **Retired:** retained for rollback or historical comparison and not loaded.

## Safety summary

- Never deploy, home, probe, align a dock, change a tool or run ToolVision while
  a print is active.
- Keep an emergency stop available during first motion after mechanical or
  configuration work.
- Never edit `config/toolchanger/readonly-configs/`; KTC-Easy owns it.
- Never replace print-tested production offsets from a single measurement.
- Back up before changing `.cfg`, `.conf` or `.sh`.
- Keep `Generated-Data/`, credentials and printer-local results out of Git.
- Opening a Mainsail prompt is harmless; confirming Setup, Calibrate, Align,
  Clean, Prime or Dryer actions can move or heat the printer.

## System overview

| Area | Active configuration |
| --- | --- |
| Printer | Voron 2.4, 350 mm CoreXY |
| Motion envelope | X `0..348`, Y `-10..336`, Z `-5..347` mm |
| Motion limits | XY velocity `300 mm/s`, acceleration `4000 mm/s²`, Z velocity `60 mm/s`, Z acceleration `700 mm/s²` |
| Controller/host | BTT Manta M8P V2.0 with BTT CM4 |
| Toolchanger | KTC-Easy StealthChanger, five rear docks, T0–T4 |
| Tool boards | Five BTT EBB36 V1.2 boards over CAN |
| Extruders/hotends | Five WW BMG geared extruders, five TZ V6 2.0 hotends, 0.4 mm nozzles |
| Production Z/mesh | Cartographer V3 Touch + Scan, fixed to the shuttle |
| Tool-offset diagnostics | ToolVision development canary; PF2 switch and Cartographer Touch methods; report-only |
| Bed | 1000 W 220 V AC silicone heater through SSR |
| Nozzle service | Purge bucket and Bambu A1 silicone pad at negative Y |
| Camera | MF-500 USB camera through Crowsnest/camera-streamer |
| Interfaces | Mainsail and Vietnamese KlipperScreen |
| Slicer | OrcaSlicer multi-tool profiles tracked under `Orca Config/` |

## Component ownership

| Component | Owner/source of truth | Repository responsibility |
| --- | --- | --- |
| KTC core macros | `~/klipper-toolchanger-easy` | Verify and preserve six readonly symlinks |
| Machine KTC paths/tools | All-Config | `toolchanger-config.cfg` and `tools/T0.cfg`…`T4.cfg` |
| Cartographer plugin | Cartographer Update Manager entry | Machine geometry and mesh settings only |
| ToolVision runtime | `~/Tool-Vision`, Moonraker updater | Machine pin, UI wrapper and generated-data paths |
| Klipper/Moonraker/Crowsnest | Their upstream updaters | Machine-specific `.cfg`/`.conf` payload |
| Generated results | Printer runtime | Preserve locally; never overwrite via `rsync --delete` |

The most important boundary is KTC-Easy ownership. All-Config refuses to deploy
when any expected readonly entry is missing, is not a symlink or has a broken
target.

## Hardware and pin reference

### Mainboard, sensors and outputs

Values come from `config/Printer-Setup/hardware.cfg` and `fans-leds.cfg`.

| Function | Active assignment |
| --- | --- |
| Main MCU CAN UUID | `19b203d75137` |
| Cartographer CAN UUID | `da13d909ce34` |
| X step/direction/enable/endstop | `PE6` / `PE5` / `!PC14` / `PF0` |
| Y step/direction/enable/endstop | `PE2` / `PE1` / `!PE4` / `PF1` |
| Z0 step pin | `PG9` |
| Z1 step pin | `PB4` |
| Z2 step pin | `PG13` |
| Z3 step pin | `PB8` |
| ToolVision switch | `^PF2` plus GND |
| Bed SSR / bed thermistor | `PA1` / `PB0` |
| Chamber thermistor | Generic 3950 on `PB1` |
| TMC fan / CM4 fan / enclosure fan / bed fan | `PF9` / `PF6` / `PF7` / `PF8` |
| Chamber WS2812 strip | `PD15`, 40 LEDs, GRB order |

All X/Y/Z stepper drivers use configured run current `0.8 A`. The bed is capped
at 120 °C. `[verify_heater heater_bed]` uses `check_gain_time: 240` because the
machine previously experienced false heat-rate shutdowns associated with noisy
bed thermistor readings.

### Toolboard common layout

Each EBB board uses the same logical pin layout with its own `EBBn` prefix:

| Function | EBB pin |
| --- | --- |
| Extruder step/direction/enable | `PD0` / `!PD1` / `!PD2` |
| Heater / thermistor | `PB13` / `PA3` |
| Hotend fan / part fan | `PA0` / `PA1` |
| TMC2209 UART / run current | `PA15` / `0.6 A` |
| Tool-presence detection | `^!PB6` |
| Filament switch | `^PB9` |
| Three-pixel tool LED | `PD3` |
| ADXL345 chip-select | `PB12` |

Every tool uses a 0.4 mm nozzle, 1.75 mm filament, 50:10 gear ratio and maximum
extrude-only distance 101 mm. Hotend maximum temperature is 290 °C. Pressure
Advance remains commented pending per-tool/material calibration.

## Tool map

### Identity, docks and extrusion calibration

Dock coordinates are nozzle coordinates and must match the real rear dock
alignment. They are not safe defaults for another machine.

| Tool | MCU | CAN UUID | Dock X/Y/Z (mm) | Rotation distance |
| --- | --- | --- | --- | ---: |
| T0 | EBB0 | `441e1484ac41` | `30.20 / 1.30 / 343` | `22.321` |
| T1 | EBB1 | `6475b5b9e028` | `104.00 / 1.10 / 343` | `22.500` |
| T2 | EBB2 | `4ad9d622a836` | `176.00 / 1.60 / 343` | `22.277` |
| T3 | EBB3 | `c2465b7c36f8` | `249.50 / 2.50 / 343` | `22.727` |
| T4 | EBB4 | `28650279df58` | `321.50 / 2.60 / 343` | `22.059` |

KTC motion parameters in `toolchanger-config.cfg` use `safe_y: 120`,
`close_y: 30`, fast travel `15000 mm/min` and dock path speed `900 mm/min`.
Every parked tool has a standby target of 150 °C.

### Print-tested production offsets

The operator reported a visually good first layer with the following
`SAVE_CONFIG` values. T0 is the reference datum.

| Tool | X offset (mm) | Y offset (mm) | Z offset (mm) |
| --- | ---: | ---: | ---: |
| T0 | `0.000` | `0.000` | `0.000` |
| T1 | `-0.243` | `-0.252` | `+0.228` |
| T2 | `+0.746` | `+0.086` | `-0.295` |
| T3 | `+0.304` | `+0.449` | `-0.268` |
| T4 | `+0.041` | `+0.352` | `-0.014` |

Run `CHECK_OFFSETS` to read the values currently loaded by Klipper without
moving the machine. The authoritative stored values are in the `SAVE_CONFIG`
block at the end of `config/printer.cfg`.

### Per-tool Input Shaper

KTC applies a measured profile after each tool change. `_ACTIVE_INPUT_SHAPER`
avoids sending the same profile repeatedly, which also reduces console noise.

| Tool | X profile | Y profile |
| --- | --- | --- |
| T0 | `3hump_ei`, 98.6 Hz, damping 0.081 | `mzv`, 35.0 Hz, damping 0.076 |
| T1 | `mzv`, 54.2 Hz, damping 0.057 | `mzv`, 35.4 Hz, damping 0.090 |
| T2 | `ei`, 67.0 Hz, damping 0.068 | `ei`, 45.8 Hz, damping 0.151 |
| T3 | `mzv`, 53.0 Hz, damping 0.078 | `mzv`, 35.2 Hz, damping 0.073 |
| T4 | `mzv`, 54.0 Hz, damping 0.080 | `mzv`, 35.2 Hz, damping 0.108 |

The global `[input_shaper]` section is the T0 fallback so Klipper loads the
module. `resonance_tester` currently targets `adxl345 T4`; change that source to
the mounted tool only during an attended calibration. ShakeTune stores at most
five results under `Generated-Data/ShakeTune/`.

## Motion, QGL and Cartographer

### Motion limits

| Parameter | Value |
| --- | ---: |
| Maximum XY velocity | `300 mm/s` |
| Maximum XY acceleration | `4000 mm/s²` |
| Maximum Z velocity | `60 mm/s` |
| Maximum Z acceleration | `700 mm/s²` |
| Square-corner velocity | `5 mm/s` |

### Quad Gantry Level

The QGL points are `(20,0)`, `(20,280)`, `(330,280)` and `(330,0)`, with speed
200 mm/s, five retries and final retry tolerance `0.0075`. On an unapplied
gantry, the wrapper performs a coarse high-clearance pass first, then the normal
pass and a final Z home. `G32` clears the mesh, homes, runs QGL and parks at
`X180 Y180 Z30`.

### Cartographer Touch and Scan

| Setting | Active value |
| --- | --- |
| Probe offset | X `0`, Y `35` |
| Mesh range | X `20..320`, Y `45..325` |
| Probe count | `55 × 55` |
| Mesh speed / horizontal Z | `600 mm/s` / `3 mm` |
| Adaptive margin | `10 mm` |
| Zero reference position | nozzle coordinate `174,168` |
| Saved Touch threshold / speed / Z offset | `1819` / `2` / `-0.05` |
| Saved Cartographer versions | software `1.8.0`, MCU `CARTOGRAPHER V3 6.1.0` |

Cartographer is fixed to the shuttle and remains the production Z-home and bed
mesh probe. ToolVision measures relative tool offsets; it does not replace
Cartographer for normal print homing.

## Repository and configuration layout

```text
Voron 5 Tool/
├── README.md / README.vi.md       # Main English/Vietnamese reference
├── config/                        # Active payload deployed to the printer
│   ├── printer.cfg                # Entry point, kinematics, SAVE_CONFIG
│   ├── mainsail.cfg               # Mainsail macro bundle
│   ├── moonraker.conf             # API and Update Manager entries
│   ├── crowsnest.conf             # MF-500 camera streamer
│   ├── KlipperScreen.conf         # Touchscreen, Vietnamese language
│   ├── Printer-Setup/
│   │   ├── calibration-probe.cfg  # Cartographer and calibration routing
│   │   ├── tool-vision.cfg        # Machine ToolVision settings and panel
│   │   ├── hardware.cfg           # MCU, steppers, bed and sensors
│   │   ├── fans-leds.cfg          # Fans, LEDs and RESUME override
│   │   ├── input-shaper.cfg       # Fallback shaper, resonance, ShakeTune
│   │   ├── nozzle-clean.cfg       # Bucket/pad cleaning
│   │   ├── prime-lines.cfg        # Multi-tool prime lines
│   │   ├── print-macros.cfg       # Print lifecycle and dryer
│   │   └── tool-crash.cfg         # Active-tool crash protection
│   ├── toolchanger/
│   │   ├── toolchanger-config.cfg # Machine paths and KTC overrides
│   │   ├── tools/T0.cfg ... T4.cfg
│   │   └── readonly-configs/      # KTC-Easy-owned symlinks; never edit
│   └── scripts/
│       ├── install.sh             # Preflight, backup and protected deploy
│       ├── update.sh              # Temporary main-branch archive updater
│       ├── cleanup-voron.sh       # Strict legacy-path cleaner
│       └── patches/               # Reviewed downstream runtime patch
├── Orca Config/                   # Machine/process/filament profiles + sync
└── extras/
    ├── docs/                      # Current bilingual guides
    ├── Nhat-ky-chinh-sua/         # Append-only daily engineering journal
    ├── backups/                   # Immutable tracked rollback snapshots
    ├── retired-configs/           # Files no longer included
    └── Config download/           # Downloaded historical snapshots
```

### Active include order

`config/printer.cfg` loads in this order:

1. `mainsail.cfg`
2. KTC-Easy `toolchanger-include.cfg`
3. `Printer-Setup/calibration-probe.cfg`
4. `Printer-Setup/tool-vision.cfg`
5. `hardware.cfg`, `fans-leds.cfg`, `input-shaper.cfg`
6. `nozzle-clean.cfg`, `prime-lines.cfg`, `print-macros.cfg`
7. `tool-crash.cfg`

The order is intentional. `tool-crash.cfg` loads after KTC tool objects.
Axiscope and `[tools_calibrate]` are commented/disabled rollback material; their
legacy public commands raise explicit errors instead of invoking a missing
probe owner.

### Printer-local generated data

The installer preserves these paths across `rsync --delete`:

```text
Generated-Data/ToolVision/state.json
Generated-Data/ToolVision/results.json
Generated-Data/ShakeTune/
```

Markdown, downloaded archives, local diagnostics, legacy ToolVision JSON and
KTC readonly symlinks are also excluded from configuration synchronization.

## Normal print workflow

### OrcaSlicer start G-code contract

The tracked machine profiles call:

```gcode
PRINT_START TOOL_TEMP={first_layer_temperature[initial_tool]} \
  T0_TEMP=... T1_TEMP=... T2_TEMP=... T3_TEMP=... T4_TEMP=... \
  BED_TEMP=[first_layer_bed_temperature] \
  TOOL=[initial_tool] MATERIAL={filament_type[initial_tool]}
```

Only used extruders emit a positive `Tn_TEMP`. `PRINT_START` rejects an invalid
tool, a non-positive initial-tool temperature or a non-positive bed target.

Optional parameters:

| Parameter | Meaning |
| --- | --- |
| `SOAK=<seconds>` | Explicit heat-soak duration |
| `AUTO_SOAK=0` | Disable material/temperature-based automatic soak |
| `FULL_BED=1` | Signal a full-bed job to the soak helper |
| `MATERIAL=<name>` | PLA/TPU/PETG/ABS/ASA/PC/NYLON/PA grouping |

### `PRINT_START` sequence

1. Validate tool and temperature inputs.
2. Cancel stale delayed fan shutdown and transfer an active dryer's bed/fan
   ownership without briefly switching them off.
3. Clear pause/mesh/offset state, initialize KTC and stop crash detection.
4. Start bed and slicer-used tool heating asynchronously. T0 stays at the
   150 °C Cartographer probing temperature at this stage.
5. Perform full `G28` before any tool change, then raise Z safely.
6. Select T0 and run `CLEAN_NOZZLE TEMP=150 WIPES=5` while the bed heats.
7. Wait for the bed, enable the bed circulation fan and run heat soak.
8. Run stable-temperature QGL.
9. Clean T0 again immediately before `CARTOGRAPHER_TOUCH_HOME`.
10. Build an adaptive bed mesh.
11. Prime every slicer-used tool; non-initial tools first, initial tool last.
12. Enable crash detection, set printing LEDs and release the sliced job.

Automatic cold-bed soak defaults:

| Material | Full cold soak |
| --- | ---: |
| PLA/TPU | 30 s |
| PETG | 60 s |
| ABS/ASA/PC/NYLON/PA | 90 s |

A bed within 5 °C of target skips automatic soak. A 5–15 °C difference uses
20% of the full duration. `SOAK=` always overrides the computed duration.

### `PRINT_END` sequence

1. Mark the print state idle and reset speed, flow and Pressure Advance.
2. Stop crash detection.
3. If XYZ is homed and the active extruder can extrude, retract 10 mm in two
   stages and lift Z.
4. Raise to at least Z 50 mm (bounded by the machine maximum).
5. Set all tool heater targets to zero and drop the active tool.
6. Park the empty shuttle at the rear, centered in X and 20 mm below Y maximum.
7. Reset G-code offsets; stop part fans and bed heat, then disable extruder
   steppers.
8. Delay bed-fan shutdown by 180 seconds, clear mesh/pause and show Complete.

`PRINT_END` intentionally leaves the shuttle empty; it does not finish with T0
mounted. If XYZ is not homed, it skips retract/lift/toolchange/park and still
performs non-motion cleanup.

### Filament runout and tool crash

Each tool has a 0.5-second delayed filament-switch filter. Runout only pauses an
active print when the affected tool is the active KTC tool; a parked-tool edge
is reported but does not pause. The custom `RESUME` path reinitializes KTC,
checks that a tool is present and re-enables crash detection before resuming.

The installed `tool_crash.py` receives an idempotent All-Config patch that
checks active-tool state before treating a detection-pin edge as a crash. The
installer backs up a matching unpatched runtime before applying it and refuses
an incompatible upstream source.

## Operator macro reference

| Macro | Purpose | Motion/heat |
| --- | --- | --- |
| `G32` | Home all axes, run QGL and park at X180 Y180 Z30 | Yes |
| `QUAD_GANTRY_LEVEL` | Wrapped coarse/fine QGL and final Z home | Yes |
| `PRINT_START ...` | Complete slicer-driven preparation | Yes, heats |
| `PRINT_END` | Retract, drop tool, park empty shuttle and cool down | Yes |
| `CLEAN_NOZZLE [TEMP=150] [WIPES=5]` | Heat if needed, flick and scrub active nozzle | Yes, may heat |
| `PURGE_AND_CLEAN [PURGE=15] [PURGE_TEMP=200]` | Purge into bucket, cool and scrub | Yes, heats |
| `PRIME_LINES INITIAL_TOOL=n Tn_TEMP=...` | Prime all listed tools, initial tool last | Yes, heats |
| `START_DRYER` | Open material prompt | Prompt only until selection |
| `START_DRYER MATERIAL=PETG ...` | Start bed/chamber drying cycle | Yes, heats/may home |
| `STOP_DRYER` | Stop dryer and turn off owned heat/fan state | No XY move |
| `DRYER_STATUS` | Print current cycle/thermal status | No |
| `CALIBRATION_STATUS` | Report active calibration backend/method | No |
| `CHECK_OFFSETS` | Report loaded T0–T4 XYZ offsets | No |
| `TOOL_VISION` | Open ToolVision panel | Prompt only until action |
| `TOOL_VISION_STATUS` | Report ToolVision readiness/error state | No |
| `QUERY_ENDSTOPS` | Read endstop/switch states | No |
| `BED_FAN_ON [SPEED=0.5]` / `BED_FAN_OFF` | Manual chamber circulation control | Fan only |
| `LIGHTS_ON` / `LIGHTS_OFF` | Chamber lighting at configured safe level | LEDs only |
| `START_CRASH_DETECTION` / `STOP_CRASH_DETECTION` | Control active-tool watchdog | No motion |

Advanced dock alignment commands `TOOL_ALIGN_START`, `TOOL_ALIGN_TEST` and
`TOOL_ALIGN_DONE` can move the printer and permanently save dock coordinates.
Use them only during an explicit attended alignment procedure with a backup.

Legacy `CALIBRATE_MOVE_OVER_PROBE`, `CALIBRATE_ALL_OFFSETS` and
`CALIBRATE_NOZZLE_PROBE_OFFSET` are deliberately disabled by
`calibration-probe.cfg` and raise instructions to use ToolVision instead.

## Nozzle cleaning and prime lines

### Physical cleaning geometry

| Item | Coordinate/setting |
| --- | --- |
| Purge bucket | X `320`, Y `-8` |
| Brush center Y | `-8` |
| Flick start X | `307` |
| Scrub X range | `277..309` |
| Clean Z / safe Z | `1.2` / `15` mm |
| Circular scrub radius | `1.5` mm |

`CLEAN_NOZZLE` requires a real active KTC tool. It may home XYZ if needed,
raises Z before traveling, optionally purges, makes the configured number of
flicks, performs clockwise/counter-clockwise circular scrubs and returns to the
bucket at safe Z.

Examples:

```gcode
CLEAN_NOZZLE
CLEAN_NOZZLE WIPES=8 TEMP=230
PURGE_AND_CLEAN
PURGE_AND_CLEAN PURGE=20 PURGE_TEMP=250 TEMP=150 WIPES=6
```

For `PURGE>0`, the actual purge temperature is at least 200 °C and at least the
requested purge/clean temperatures. The macro then cools to cleaning
temperature with the part fan before scrubbing.

### Prime-line behavior

The prime-line controller uses up to 52 mm per tool, three passes at Z `0.28`,
13.33 mm extrusion per full-length pass, a 6 mm tool-slot gap and 3 mm pass
spacing. It scales length/extrusion when several tools must fit, retracts
non-final tools 1.8 mm and the final tool 0.6 mm, and leaves the initial printing
tool mounted.

## Heated-bed filament dryer

Calling `START_DRYER` without parameters opens one Mainsail material prompt.
Calling it with parameters starts directly. The controller rejects a starting,
printing or paused printer before motion or heat.

| Material | Bed | Chamber target | Duration | Base bed fan |
| --- | ---: | ---: | ---: | ---: |
| PLA/PLA+ | 50 °C | 40 °C | 240 min | 40% |
| TPU/TPE | 60 °C | 45 °C | 300 min | 40% |
| PETG | 70 °C | 55 °C | 240 min | 50% |
| ABS | 90 °C | 65 °C | 240 min | 60% |
| ASA | 90 °C | 65 °C | 240 min | 60% |
| NYLON/PA | 100 °C | 70 °C | 360 min | 70% |
| PC | 105 °C | 75 °C | 360 min | 70% |
| CUSTOM | 55 °C | disabled | 240 min | 40% |

Advanced overrides:

```gcode
START_DRYER MATERIAL=PETG BED=70 CHAMBER=55 TIME=240 FAN=0.50 PARK=1
START_DRYER MATERIAL=CUSTOM BED=60 TIME_HOURS=6 FAN=0.45 PARK=0
```

Supported overrides are `BED`, `CHAMBER`, `TIME`, `TIME_HOURS`, `FAN`, `PARK`,
`HUMIDITY` and `TARGET_HUMIDITY`. Humidity is used only when an installed
sensor extension exposes `.humidity`; the configured Generic 3950 chamber
thermistor provides temperature only.

With `PARK=1`, the dryer may home, lift to at least Z 200, dock an active tool
and park at X175 Y310 before heating. Airflow boosts while the chamber is cold,
uses a 30-second moisture flush every 20 minutes and reduces bed/fan output when
the chamber is too hot. `PRINT_START` safely takes ownership from an active
dryer timer.

## ToolVision report-only calibration

### Deployed machine integration

| Item | Current value |
| --- | --- |
| Runtime checkout | `~/Tool-Vision` |
| Python environment | `~/tool-vision-env` |
| Host service/API | `tool-vision.service`, loopback port `8085` |
| Machine config | `Printer-Setup/tool-vision.cfg` |
| Physical switch | Manta `^PF2` |
| Learned state | `Generated-Data/ToolVision/state.json` |
| Latest result | `Generated-Data/ToolVision/results.json` |
| Production runtime evidence | ToolVision `204ae4c`, reported `3.4.0-rc2` |

ToolVision is the active report-only tool-offset backend. Axiscope and
`[tools_calibrate]` remain disabled. The compact panel exposes explicit
`Physical switch` and `Cartographer Touch` Z actions, `Latest results`, and an
`Advanced setup` page. UI-generated Z runs always pass an explicit `METHOD=`
and `VERBOSITY=QUIET`; teaching a station can still change the stored default,
but it cannot silently change the method of either named measurement button.

This machine opts into `INITIALIZE_TOOLCHANGER` as ToolVision's post-error KTC
recovery hook. The hook initializes from the physically detected tool and
ToolVision verifies active state before attempting to restore T0. It is a
reviewed machine-specific setting, not a portable ToolVision default.

Camera XY exists in ToolVision but was not ready in the last recorded printer
status and no camera source/name is configured here. Do not treat camera XY as
an active production calibration path.

### Result meaning

For Z, the implemented sign is:

```text
measured Z(tool) = raw contact Z(tool) - raw contact Z(reference T0)
```

This is a candidate absolute tool value relative to T0. It is not a residual
delta to add to the configured production offset. ToolVision never writes the
T0–T4 production files.

Three attended 150 °C runs per method on 2026-08-25 produced these means:

| Tool | Production Z | PF2 mean (range) | Cartographer Touch mean (range) |
| --- | ---: | ---: | ---: |
| T0 | +0.000 | +0.000 | +0.000 |
| T1 | +0.228 | +0.121 (+0.114..+0.130) | +0.243 (+0.238..+0.248) |
| T2 | -0.295 | -0.385 (-0.386..-0.384) | -0.268 (-0.270..-0.266) |
| T3 | -0.268 | -0.179 (-0.186..-0.164) | -0.186 (-0.196..-0.178) |
| T4 | -0.014 | +0.093 (+0.090..+0.096) | +0.105 (+0.102..+0.108) |

Mean T0 return drift was `+0.033 mm` for PF2 and `+0.011 mm` for Cartographer
Touch. Cartographer minus PF2 differed by `+0.121 mm` on T1, `+0.117 mm` on T2,
`-0.007 mm` on T3 and `+0.011 mm` on T4. The disagreement is diagnostic, not a
request to average or apply the methods. Dated immutable history preserves all
runs; the print-tested production offsets above were not changed.

Five additional Cartographer Touch runs were completed after a separate full
`G28` before each run, with the bed held at the PETG production target of
`70 °C` and every nozzle measured at `150 °C`. Their means (ranges) were T1
`+0.2464` (`0.024`), T2 `-0.2688` (`0.026`), T3 `-0.1896` (`0.010`) and T4
`+0.1028 mm` (`0.020`). Each mean moved by less than `0.004 mm` from the earlier
room-temperature-bed Cartographer mean. T0 return drift ranged `0.000..0.020
mm`; all five sessions had empty cleanup errors and did not apply or change
configuration. This supports Touch homing after the bed reaches its print
temperature, while showing no material thermal correction to the relative tool
offsets on this pilot.

### Canary UI and console evidence

The canary branch `codex/compact-mainsail-output` at `204ae4c` passed the GitHub
Security Gate and attended HIL. Every prompt entry point now fails closed while
the printer is printing or paused, and Close uses a dedicated helper instead of
a nested `RESPOND`. A client-cached KlipperScreen dialog still belongs to that
client and may require a frontend refresh after the print. Opening
`TOOL_VISION` emits eight prompt responses instead of eleven. A quiet
calibration emits exactly three ToolVision-owned messages, but KTC toolchange,
heater-wait, physical probe and Cartographer messages remain visible. Do not
hide `action:prompt_*`, warnings or errors with a Mainsail regex filter.

Read the [integration guide](extras/docs/toolvision-integration-guide.en.md) and
[2026-08-25 journal](extras/Nhat-ky-chinh-sua/2026-08-25-session-updates.md)
before changing the runtime, station or panel.

## Camera and user interfaces

`crowsnest.conf` configures the MF-500 at 1280×720, requested 30 fps, MJPEG
camera input and camera-streamer/WebRTC output. The device is selected by its
stable `/dev/v4l/by-id/...` path. Power-line frequency is set to 50 Hz for the
local mains frequency.

The machine previously observed only 15–20 fps in MJPEG view under host load;
WebRTC `/webcam/webrtc` is the recorded workaround. 1080p/1440p previously
produced a black view, so 1280×720 remains the documented stable setting.

Mainsail is the main web UI. KlipperScreen is configured in Vietnamese.
ToolVision, dryer and other complex operations expose one visible macro that
opens a prompt; helpers whose names begin with `_` remain internal.

## OrcaSlicer profiles

`Orca Config/` contains three machine, four process and 15 filament profile
JSON files. The exact inventory and restore instructions are in
[`Orca Config/README.md`](Orca%20Config/README.md).

Two synchronization paths are intentionally different:

```powershell
# Review-only by default: no diagnostics, commit or push unless requested.
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File ".\Orca Config\Sync-OrcaProfiles.ps1"

# Double-click wrapper: diagnostics + scoped commit + push.
.\Orca Config\Sync-OrcaProfiles.cmd
```

The PowerShell script selects the most recently edited Orca user profile unless
`-ProfileId` is supplied, validates every selected JSON, rejects duplicate flat
names, copies only changes, backs up replaced destination files, writes the
daily journal and stages only synchronization-owned paths when `-Commit` is
used. `-Push` implies `-Commit`.

## Install and update

### Preconditions

1. Printer is idle, not paused and not calibrating.
2. KTC-Easy is installed and its six readonly symlinks are valid.
3. ToolVision checkout, venv, service and five Klipper extension symlinks exist
   because the active config includes ToolVision.
4. Current configuration and generated calibration data have a usable backup.
5. The operator is prepared to review output and restart services manually.

### First All-Config install without a persistent clone

```bash
tmp_dir="$(mktemp -d /tmp/all-config-voron.XXXXXX)"
curl -fsSL https://github.com/IDcrazy123/All-Config-Voron/archive/refs/heads/main.tar.gz \
  | tar -xz -C "${tmp_dir}" --strip-components=1
bash "${tmp_dir}/config/scripts/install.sh"
rm -rf -- "${tmp_dir}"
sudo systemctl restart moonraker klipper
```

The All-Config Git checkout is not kept on the CM4. The ToolVision and KTC-Easy
runtime checkouts are separate and remain present because their services,
symlinks and Update Manager entries use them directly.

### Routine All-Config update

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

`update.sh` creates a temporary directory, downloads the `main` archive with
`curl` or `wget`, validates that it contains `config/printer.cfg`, calls
`install.sh` and removes the temporary source through a trap.

`install.sh` then:

1. Validates KTC-Easy readonly ownership.
2. Validates ToolVision runtime/service/module links.
3. Dry-runs or recognizes the reviewed `tool_crash.py` patch.
4. Copies the entire current printer config to
   `~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/`.
5. Runs protected `rsync --delete` with runtime/generated/readonly exclusions.
6. Backs up and applies the tool-crash runtime patch only when needed.
7. Prints the backup path and asks the operator to review before restart.

Neither script restarts Moonraker or Klipper automatically. After reviewing a
successful deploy:

```bash
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

### Post-update checks without intentional motion

Host:

```bash
systemctl is-active klipper moonraker crowsnest tool-vision
curl --fail --silent http://127.0.0.1:8085/api/v2/health
```

Mainsail console:

```text
CALIBRATION_STATUS
CHECK_OFFSETS
QUERY_ENDSTOPS
TOOL_VISION_STATUS
DRYER_STATUS
```

Expected: Klipper ready, printer idle, ToolVision not busy, PF2 normally open,
heater targets zero and no unexplained last error. These checks do not
intentionally home, probe or select a tool.

## Backups, rollback and cleanup

### Backup locations

| Backup type | Location |
| --- | --- |
| Repository task snapshot | `extras/backups/pre-<task>-YYYYMMDD-HHMMSS/` |
| Automatic printer config snapshot | `~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/` |
| ToolVision state/result | `Generated-Data/ToolVision/` plus a separate off-device copy before runtime/schema work |

Tracked backup snapshots and daily journals are immutable evidence. Do not edit
old backup READMEs to describe a newer system. The bilingual documentation
index links three recent tracked rollback points without changing them.

### Rollback principles

1. Stop while the printer is idle and create another backup of the current
   state.
2. Identify the matching config, runtime revision and generated-data schema.
3. Restore only the intended files; do not blindly replace
   `Generated-Data/ToolVision/` during a config-only rollback.
4. Validate config/JSON, restart services in a controlled order and run
   non-motion checks first.
5. Record the rollback in the daily journal.

### Cleanup script scope

`config/scripts/cleanup-voron.sh` is dry-run by default:

```bash
bash ~/printer_data/config/scripts/cleanup-voron.sh
bash ~/printer_data/config/scripts/cleanup-voron.sh --apply
```

It only lists/removes strictly validated legacy paths matching
`printer_data/config.update-backup-*`, `printer_data/config.backup-*` and
`~/axiscope.bak`. It does not implement automatic retention for normal
`config_backups/`. Review every printed path before `--apply`.

## Troubleshooting

| Symptom | Check first | Safe response |
| --- | --- | --- |
| Klipper says `Unknown section 'tool_vision'` | Five `tool_vision*.py` symlinks and ToolVision checkout | Repair the runtime installation, then restart Klipper while idle |
| All-Config deploy refuses KTC readonly files | Six entries under `toolchanger/readonly-configs/` | Run `bash ~/klipper-toolchanger-easy/install.sh` while idle; do not copy regular files there |
| `ToolVision switch` is triggered while untouched | PF2 wiring, pull-up/inversion and physical switch | Stop calibration; inspect with `QUERY_ENDSTOPS` before motion |
| ToolVision setup/result appears missing | `Generated-Data/ToolVision/state.json` and `results.json` | Preserve files/logs; do not create placeholder JSON or immediately re-teach |
| PF2 result disappeared after Cartographer run | Current runtime stores one latest `results.json` | Use dated console/journal evidence; history is only in the un-deployed UX branch |
| Cartographer fails after restart | `klippy.log`, Cartographer temperature and `can0` state | Capture evidence before power-cycling; do not assume the old CAN hypothesis is proven |
| Bed reports heat-rate failure | Bed thermistor/SSR wiring and actual temperature rise | Stop if heating is abnormal; do not weaken `[verify_heater]` further without evidence |
| Tool-presence edge pauses incorrectly | Active KTC tool, detection pins and installed patch marker | Preserve logs; verify installer patch compatibility instead of disabling protection |
| Camera is black at 1080p/1440p | Crowsnest resolution/service | Return to documented 1280×720 WebRTC configuration |
| Dryer will not start | Print/pause state and override ranges | Finish/cancel the print safely; correct parameters rather than bypassing the guard |
| `CLEAN_NOZZLE` says no active tool | `printer.toolchanger.tool_number` | Initialize/select the intended tool only after safe homing/clearance checks |
| Mainsail Config Files shows stale duplicates | Actual filesystem and browser cache | Refresh/hard-refresh Mainsail; do not delete a file based only on a ghost UI row |

Useful log commands on the host:

```bash
journalctl -u klipper -n 100 --no-pager
journalctl -u moonraker -n 100 --no-pager
journalctl -u tool-vision -n 100 --no-pager
journalctl -u crowsnest -n 100 --no-pager
```

Do not paste private camera URLs, credentials or complete unredacted private
configuration into public issues.

## Current limitations and pending work

- ToolVision remains a monitored report-only development canary. Its improved
  method-specific/history UI is implemented upstream on a feature branch but
  not deployed/HIL-tested here.
- ToolVision camera XY is not an active production calibration path.
- Pressure Advance is not yet calibrated per tool/material.
- Per-tool cooling behavior still has a pending review task.
- Additional Cartographer temperature warning/monitoring remains pending.
- `cleanup-voron.sh` has no “keep newest N” policy for normal installer backups.
- The current ToolVision runtime keeps only the latest result file.
- The MF-500 documented stable mode is 1280×720 WebRTC, not its highest nominal
  resolution.

See the parent workspace `.agents/TODO.md` and `.agents/KNOWN_ISSUES.md` for the
maintained task and incident lists.

## Documentation map

| Document | English | Vietnamese |
| --- | --- | --- |
| Main system reference | [README](README.md) | [README](README.vi.md) |
| Active config payload | [Config README](config/README.md) | [Config README](config/README.vi.md) |
| StealthChanger operation | [Guide](extras/docs/huong-dan-he-thong-stealthchanger.en.md) | [Guide](extras/docs/huong-dan-he-thong-stealthchanger.md) |
| ToolVision integration | [Guide](extras/docs/toolvision-integration-guide.en.md) | [Guide](extras/docs/toolvision-integration-guide.vi.md) |
| ToolVision UX evidence/status | [Report](extras/docs/toolvision-z-calibration-ux-proposal.md) | [Report](extras/docs/toolvision-z-calibration-ux-proposal.vi.md) |
| OrcaSlicer profiles | [README](Orca%20Config/README.md) | [README](Orca%20Config/README.vi.md) |
| Documentation/history policy | [Index](extras/docs/README.md) | [Index](extras/docs/README.vi.md) |

Historical journals, retired files, downloaded snapshots and backup contents
remain evidence from their own dates. Use the current documents above to
understand present behavior.

## Safe contribution workflow

1. Read the active file and applicable project rules before editing.
2. Preserve unrelated user changes and printer-local generated data.
3. Back up every `.cfg`, `.conf` or `.sh` that will change.
4. Make the smallest source-backed change; never guess hardware values.
5. Validate Klipper syntax, shell syntax and relevant include/path contracts.
6. Update both English and Vietnamese current documentation when behavior or a
   path changes.
7. Append the dated engineering journal.
8. Stage only task-related files, commit with an English message and push
   `main` when authorized.

The repository is production infrastructure. A change is complete only when
its source, documentation, backup, validation and rollback story agree.

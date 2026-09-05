# Five-tool StealthChanger operating guide

[English](huong-dan-he-thong-stealthchanger.en.md) | [Tiếng Việt](huong-dan-he-thong-stealthchanger.md)

This guide was refreshed on 2026-08-31 after reading the full Markdown corpus,
active configuration, kTAMV source and deployment scripts. Historical journals
are not rewritten as current state.

## 1. Ownership boundaries

- KTC-Easy owns `toolchanger/readonly-configs/` and its six installer-created
  symlinks. Do not edit them in All-Config.
- All-Config owns `toolchanger-config.cfg`, `tools/T0.cfg`…`T4.cfg` and the
  overrides under `Printer-Setup/`.
- Cartographer is active for Z homing and bed mesh.
- kTAMV is active for supervised camera-based X/Y comparison only.
- Axiscope and `[tools_calibrate]` are disabled, commented rollback material.
- There is no active tool-offset Z backend; PF2 remains physically present but
  unused by kTAMV.

## 2. Include and override order

The active load order in `printer.cfg` is:

```text
mainsail.cfg
KTC-Easy readonly toolchanger include
calibration-probe.cfg
ktamv.cfg
hardware.cfg
fans-leds.cfg
input-shaper.cfg
nozzle-clean.cfg
prime-lines.cfg
print-macros.cfg
filament-dryer.cfg
test-speed.cfg
tool-crash.cfg
```

`tool-crash.cfg` follows tool definitions so it can hook the active-tool
detection objects. Do not reorder includes only for appearance without checking
Klipper override and parser behavior.

## 3. Tools and toolchange

T0–T4 use EBB36 boards, detection pin `^!EBBn:PB6`, `0.6 A` extruder run
current and Generic 3950 thermistors. Docks are at Z `343 mm`:

| Tool | Dock X | Dock Y | Rotation distance |
| --- | ---: | ---: | ---: |
| T0 | 30.20 | 1.30 | 22.321 |
| T1 | 104.00 | 1.10 | 22.500 |
| T2 | 176.00 | 1.60 | 22.277 |
| T3 | 249.50 | 2.50 | 22.727 |
| T4 | 321.50 | 2.60 | 22.059 |

`toolchanger-config.cfg` uses `safe_y: 120`, `close_y: 30`, fast speed
`15000 mm/min` and path speed `900 mm/min`. `require_tool_present` is `False`,
while `tool-crash.cfg` still checks detection pins, routes through KTC and
pauses safely during a print. Safe pause does not add an XYZ move.

Input shaper is sent only when the target differs from the active profile,
tracked by `_ACTIVE_INPUT_SHAPER`; this reduces repeated console output. M109
uses a default 4 °C deadband (±2 °C).

## 4. Homing, QGL and Cartographer

Main motion limits:

- X `0..348`, endstop `PF0`.
- Y `-10..336`, endstop `PF1`.
- Configured Z range `-5..347`; maximum Z velocity `70 mm/s`, Z acceleration
  `900 mm/s²`.
- Maximum XY velocity `350 mm/s`, acceleration `7000 mm/s²`.

Cartographer offsets are X `0`, Y `35`. Bed mesh spans X `20..320`,
Y `45..325` at 55 × 55 samples. Touch uses
`bed_mesh.zero_reference_position`; kTAMV does not participate in production Z.

`G32` runs the current homing/QGL macro. Before manual maintenance motion,
verify carriage, mounted tool, docks and clearance.

## 5. `PRINT_START`

The implemented order in `print-macros.cfg` is:

1. Parse and validate slicer tool and temperature parameters.
2. Cancel stale dryer callbacks, reset state and stop crash detection.
3. Start bed and required-tool heating asynchronously.
4. Home all axes before any toolchange.
5. Select T0, reach cleaning temperature and run `CLEAN_NOZZLE`.
6. Wait for the bed and run automatic or explicitly overridden heat soak.
7. Run QGL, clean T0 again and perform Cartographer Touch homing.
8. Build an adaptive bed mesh.
9. Prime every slicer-used tool, with the initial tool last.
10. Enable crash detection and begin printing.

Cold-bed automatic soak defaults are 30 seconds for PLA/TPU, 60 seconds for
PETG and 90 seconds for ABS/ASA/PC/NYLON/PA. A difference no greater than 5 °C
skips the soak; 5–15 °C uses 20% duration. `AUTO_SOAK=0` disables the automatic
calculation.

## 6. Prime, cleaning and shutdown

`PRIME_LINES` uses 52 mm lines, three passes and 13.33 mm extrusion per full
52 mm pass, Z `0.28`, retract `1.8` and final retract `0.6`. It primes tools at separate
positions; a purge tower is not required by this macro.

`CLEAN_NOZZLE` requires an active KTC tool, can home when needed and uses the
configured bucket/pad in negative Y. `PURGE_AND_CLEAN` purges into the bucket,
then cools for scrubbing. Do not run them when the physical bucket/pad or path
is obstructed.

`PRINT_END` stops crash detection, turns off job-owned heaters/fans, drops the
active tool and parks an empty shuttle. `CANCEL_PRINT` uses the matching cleanup
path. Do not build slicer logic on an assumption that T0 remains mounted.

## 7. Dryer

`START_DRYER` rejects an active print. With `PARK=1`, it can home, dock and park
before heating. Code presets are:

| Material | Bed | Chamber | Time | Fan |
| --- | ---: | ---: | ---: | ---: |
| PLA | 50 °C | 40 °C | 240 min | 40% |
| TPU | 60 °C | 45 °C | 300 min | 40% |
| PETG | 70 °C | 55 °C | 240 min | 50% |
| ABS/ASA | 90 °C | 65 °C | 240 min | 60% |
| NYLON | 100 °C | 70 °C | 360 min | 70% |
| PC | 105 °C | 75 °C | 360 min | 70% |

Public commands are `START_DRYER`, `STOP_DRYER` and `DRYER_STATUS`. The macro
handles print handoff, but covers and material must still be cleared from the
motion envelope before printing.

## 8. Calibration and offsets

Production offsets in `printer.cfg` are:

| Tool | X | Y | Z |
| --- | ---: | ---: | ---: |
| T0 | 0.000 | 0.000 | 0.000 |
| T1 | -0.159 | -0.195 | +0.236 |
| T2 | +0.820 | +0.240 | -0.316 |
| T3 | +0.326 | +0.524 | -0.1896 |
| T4 | +0.168 | +0.268 | +0.120 |

The operator considers the baseline first layer visually good. Two retired
ToolVision runs on 2026-08-23 remain diagnostic evidence:

| Tool | Production | PF2 switch | Cartographer Touch |
| --- | ---: | ---: | ---: |
| T0 | +0.000 | +0.000 | +0.000 |
| T1 | +0.228 | +0.098 | +0.242 |
| T2 | -0.295 | -0.384 | -0.256 |
| T3 | -0.268 | -0.154 | -0.160 |
| T4 | -0.014 | +0.078 | +0.102 |

The retired ToolVision integration calculated Z as `raw(tool) - raw(reference)`.
It is a candidate
absolute value relative to T0, not a delta to add to the configured offset. PF2
return drift was `+0.028 mm`; Cartographer return drift was `-0.008 mm`. One
run cannot replace a print-tested baseline; repeat the same method/temperature
and validate independently.

The active kTAMV backend does not measure Z. It reports X/Y only, keeps camera
calibration/origin in RAM and does not save tool offsets. See the
[kTAMV usage and method comparison](ktamv-usage-comparison.en.md).

## 9. Input shaper

The system operates on a Unified Global Input Shaper tuned from the Cartographer
onboard ADXL345 on the carriage shuttle: X `mzv` 43.6 Hz/damping 0.124 and
Y `mzv` 33.4 Hz/damping 0.080. Per-tool overrides in T0–T4 are commented out to eliminate
toolchange stalls and latency. The resonance tester targets `accel_chip: adxl345`;
ShakeTune writes under `Generated-Data/ShakeTune` and keeps 10 results, tracked in Git.
For benchmark details, see [TEST_SPEED & Input Shaper Evaluation](danh-gia-input-shaper-va-test-speed-2026-09-04.md).

## 10. Update and verification

Update only while idle:

### Method 1: 1-Click Update directly in Mainsail UI (Recommended)
After pushing code to GitHub:
- Navigate to **Settings > Machine / Update Manager** in Mainsail web UI.
- Locate **All-Config-Voron** and click **Update**: Moonraker will pull the repository, run safety preflights, create a backup, rsync configs, and restart Klipper automatically.
- See [Mainsail 1-Click Update Guide & Cross-Check](danh-sach-doi-chieu-va-huong-dan-update-mainsail.md).

### Method 2: Manual Update via SSH
```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart moonraker klipper
```

`update.sh` downloads a temporary `main` archive and calls the installer. The
installer preflights KTC, pinned kTAMV and the two reviewed runtime patches, then creates a
backup before `rsync`. It does not restart services.

Non-motion checks after deployment:

```text
CALIBRATION_STATUS
QUERY_ENDSTOPS
KTAMV_STATUS
```

Only home, toolchange or probe after the operator confirms an empty motion
path, correct docks and an available emergency stop.

## 11. Safe editing rules

- Back up before changing `.cfg`, `.conf` or `.sh`.
- Never edit `readonly-configs/`.
- Never replace production offsets from one measurement.
- Never deploy while printing, paused or calibrating.
- Keep retired ToolVision archives immutable; do not restore them into active
  config unless performing an explicit rollback.
- Do not rewrite old journals/backups; create new evidence.

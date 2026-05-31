# 2026-05-18 Session Summary

## Purpose

Preserve the working context from the latest configuration session so future sessions can quickly understand what changed and why.

## Main Direction

- Paused the Axiscope Cartographer Z-offset path.
- Returned tool offset calibration to the official StealthChanger/KTC-Easy SexBolt/SexBall workflow using `tools_calibrate`.
- Kept Cartographer as the main Z probe for homing, touch home, and bed mesh.
- Used SexBolt/SexBall only for tool-to-tool XYZ offset calibration.

## SexBolt/SexBall Setup

- Sensor connected to Manta M8P V2.0 `M1-STOP`, pin `PF4`.
- Configured in `toolchanger/toolchanger-config.cfg`:

```ini
[_CALIBRATION_SWITCH]
variable_x: 257
variable_y: 327
variable_z: 60

[tools_calibrate]
pin: ^PF4
trigger_to_bottom_z: 0.9
```

- `Z55` from the physical measurement is the approximate contact height on the ball.
- `Z60` is used as the safe approach height.

## Saved Tool Offsets From SexBolt

The current saved offsets in `printer.cfg` are:

```ini
T1: X ~0,       Y 0.215625,  Z 0.05
T2: X -0.11875, Y -0.1125,   Z -0.210
T3: X -0.16875, Y -0.096875, Z -0.328
T4: X 0.100,    Y 0.003125,  Z -0.278
```

The T1 X value shown as scientific notation, for example `7.548e-11`, is effectively zero.

## Comment Translation

- Active configuration comments were translated to English.
- Backup before the translation pass:

```text
C:\Users\batca\OneDrive\Desktop\All\config_full_backup_before_english_comments_20260517-163340
```

- Backup folders and old config copies were intentionally not translated.

## Dock Y Alignment

Because the physical Y endstop / dock relation changed, all `params_park_y` values were reduced by a total of `0.5 mm`.

Current values:

```ini
T0 params_park_y: 1.8
T1 params_park_y: 2.3
T2 params_park_y: 2.5
T3 params_park_y: 2.5
T4 params_park_y: 2.8
```

Relevant backup folders:

```text
config/_backups/park-y-minus-0.3-20260517-171800
config/_backups/park-y-minus-0.2-more-20260517-211156
```

## Toolchange Speed Tuning

Updated values:

```ini
params_fast_speed: 15000  # ~250mm/s
max_z_velocity: 60
max_z_accel: 700
```

Backup before speed tuning:

```text
config/_backups/speed-tuning-20260518-155957
```

## OrcaSlicer / G-code Findings

The checked G-code file contains real toolchanges even though OrcaSlicer preview shows `0` filament changes.

Observed counts:

```text
T command count: 451
Toolchange comments: 450
```

Reason: Orca's "filament changes" counter is for single-extruder/MMU style swaps. It does not represent physical `T1/T2/T3/T4` toolchanger commands.

## PETG Ooze / Small Plastic Bits

Observed behavior:

- The tool goes to the wipe tower first.
- After wiping, PETG sometimes remains curled or attached to the nozzle and drops later.

Recommended tuning ideas:

```text
PETG nozzle temperature: 220 -> 215C
Retraction: 2.0 -> 1.0-1.2mm
Enable wipe while retracting
Wipe distance: 1 -> 2mm
Wipe tower speed: 90 -> 60-70mm/s
Rib width: 8 -> 10/12
Temporarily disable ramming for testing
```

## Mobileraker + Tailscale

Remote access direction:

- Use Tailscale instead of opening router ports.
- Use Mobileraker with Moonraker URL:

```text
http://<printer-tailscale-ip>:7125
```

Moonraker must trust the phone/laptop Tailscale IP or the Tailscale CGNAT range:

```ini
[authorization]
trusted_clients:
    127.0.0.1
    192.168.1.0/24
    100.64.0.0/10
```

For stricter security, trust only the exact Tailscale IPs of personal devices.

## GitHub Config Repository

Created and pushed the active config repository:

```text
https://github.com/Batcandoionline/Stealth-changer-config
```

The `config` directory itself is now the Git repository.

Added:

```text
README.md
scripts/install.sh
scripts/update.sh
.gitignore
.gitattributes
```

Ignored from Git:

```text
_backups/
*.zip
*backup*
*.log
*.gcode
```

Moonraker Update Manager entry added:

```ini
[update_manager stealth-changer-config]
type: git_repo
path: ~/printer_data/config
origin: https://github.com/Batcandoionline/Stealth-changer-config.git
primary_branch: main
managed_services: klipper
```

First install on the printer:

```bash
cd /tmp
git clone https://github.com/Batcandoionline/Stealth-changer-config.git
cd Stealth-changer-config
bash scripts/install.sh
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

Later update:

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

## Tool Crash Detection Review

Checked upstream:

```text
https://github.com/cekim-git/tool_crash
```

Findings:

- Plugin is alpha/WIP upstream.
- It loaded in the current Klipper log without import/config errors.
- It parses each tool's `detection_pin`; it does not use Cartographer and does not use SexBolt/PF4.
- Cartographer remains independent as the Z probe.
- The current system uses Klipper `v0.13.0-650-gca8230d50-dirty`, Cartographer V3 `6.1.0`, and `klipper-toolchanger-easy`.

Important fix made:

- `STOP_CRASH_DETECTION` is called during `dropoff_gcode`.
- Before the fix, crash detection could remain disabled after the first toolchange during a print.
- Added restart logic in `after_change_gcode`: if `_PRINT_STATE == "printing"`, run `START_CRASH_DETECTION` after the toolchange completes.

Commit pushed:

```text
cb985bc Fix tool crash detection after toolchange
```

## Recommended Smoke Test

After pulling this config to the printer:

```gcode
FIRMWARE_RESTART
INITIALIZE_TOOLCHANGER
T0
T1
T2
T3
T4
T0
START_TOOL_CRASH_DETECTION
STOP_TOOL_CRASH_DETECTION
```

Expected console response:

```text
tool_crash: enabled
tool_crash: disabled
```

During a real print, after every toolchange the console should show `tool_crash: enabled` again.

## LED Control Review

Reviewed LED-related configuration and hooks:

```text
Printer-Setup/fans-leds.cfg
toolchanger/toolchanger-config.cfg
Printer-Setup/print-macros.cfg
Printer-Setup/nozzle-clean.cfg
mainsail.cfg
toolchanger/tools/T0.cfg ... T4.cfg
```

Findings and fixes:

- All five toolheads define `T0_LED` through `T4_LED` as 3-LED GRB neopixel chains.
- All LED state names used by macros are defined in `_SET_TOOL_LED`.
- Fixed cancel cleanup order: `_CUSTOM_CANCEL_CLEANUP` now sets `_PRINT_STATE` to `idle` before any possible `T0` toolchange, so `after_change_gcode` cannot restore printing LEDs or restart crash detection during cancel cleanup.
- Added an extra `STOP_CRASH_DETECTION` after the cancel-time `T0` switch as a safety net.
- Reviewed `calibrating` LED integration for `CALIBRATE_ALL_OFFSETS` and `CALIBRATE_NOZZLE_PROBE_OFFSET`, then intentionally left the calibration macros on the upstream/readonly workflow. Copying the full SexBolt calibration macro only to add LED color was judged too risky for a real machine because it duplicates high-stakes toolchange/probe/save-offset logic.

Static checks run:

```text
LED macro reference check: no missing LED macros
LED state check: all used states are defined
Toolhead LED check: T0-T4 all have chain_count=3 and color_order=GRB
git diff --check: clean
Line endings: LF per .gitattributes
```

## Vietnamese Comment Cleanup

Backup created before editing:

```text
config/_backups/vietnamese-to-english-20260518-165324
```

Translated remaining Vietnamese or Vietnamese-without-diacritics text in active Klipper/Voron configuration comments and operator-facing messages:

```text
Printer-Setup/print-macros.cfg
Printer-Setup/fans-leds.cfg
```

Also cleaned the ignored root backup copy:

```text
printer.cfgbackup
```

Notes:

- Did not change behavior-setting values such as `KlipperScreen.conf` `language = vi`; that is a UI setting, not a comment or message.
- Did not edit `_backups/`, `.git/`, zipped archives, or historical session notes except for this session summary.

## Hardware Overview README Fix

Updated the README hardware overview to describe hardware only, not software tuning values.

Changes:

- Removed software/config tuning details from the README `Current Machine` section, such as toolchanger speed, Z motion limits, input shaper workflow, and SexBolt input pin.
- Replaced the old short machine summary with a hardware overview: printer, toolchanger, motion system, Manta M8P V2.0 + CM4, Cartographer V3, EBB toolhead boards, hotends/extruders, sensors, bed/chamber hardware, fans, and lighting.
- Corrected the toolhead controller description after rechecking the active config and user-confirmed hardware: all five toolheads use BIGTREETECH EBB36 V1.2. The previous README line incorrectly listed T4 as EBB46 V1.2.
- Corrected `toolchanger/tools/T4.cfg` comments from EBB46 V1.2 to EBB36 V1.2. No T4 pin or runtime config values were changed.

Confirmed hardware details:

- Base frame is Voron 2.4 350 mm.
- The StealthChanger build adds a top extension / raised roof with an additional 250 mm of height.
- All five toolheads use TZ V6 2.0 hotends with WW BMG extruders.

## Runtime Logic Review and Safety Guards

Reviewed active StealthChanger/KTC-Easy config as a running-printer state machine:

```text
PRINT_START
PRINT_END
CANCEL_PRINT cleanup hook
CLEAN_NOZZLE
toolchanger pickup/dropoff hooks
crash detection override
```

Fixes made:

- Removed the duplicate direct include of `toolchanger/toolchanger-config.cfg` from `printer.cfg`; it is already included by `toolchanger/readonly-configs/toolchanger-include.cfg`.
- Kept `toolchanger/readonly-configs` untouched; all behavior changes are in custom override files.
- Fixed `START_CRASH_DETECTION` / `STOP_CRASH_DETECTION` selection to check configured `[tool_crash]` instead of looking for plugin commands as gcode macros.
- Added a custom `M109` override in `toolchanger/toolchanger-config.cfg` so `M109 S...` without `T` does not fail when KTC's upstream macro sees no `T` parameter.
- Added guards for empty active extruder in `CLEAN_NOZZLE` and `PRINT_END`, preventing `printer[""]` lookups and unsafe heat/purge/retract behavior.
- Updated `PRINT_END` and cancel cleanup to only call `T0` when an actual nonzero tool is active; if toolchanger state is `-1`, they skip T0 pickup and report it.
- Made `_PRINT_START_SELECT_T0` explicit: `T1..T4` means switch back to T0, `-1` means pick up T0 after full homing for clean/touch-home.
- Added explicit `t_command_restore_axis: Z` in the custom `[toolchanger]` override to pin the intended KTC-Easy toolchange restore behavior.
- Switched LED/fan existence checks to `printer["..."] is defined`.

Reference checks:

- Compared against StealthChanger/KTC-Easy docs and examples: toolchange config belongs in custom override files, print start should home and use T0 for pre-print calibration, and `safe_y`/`close_y` must be treated as calibrated mechanical values.
- Kept current `safe_y`, `close_y`, park positions, speeds, and SexBolt/Cartographer calibration values unchanged.

Static checks run:

```text
Include graph: 23 active files / 23 unique files
Missing includes: none
Repeated active file loads: none
toolchanger/readonly-configs diff: none
git diff --check: clean
```

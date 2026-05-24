# Change Log - 2026-05-16

## Current Goal

Pause the Axiscope Cartographer direction and return to the official StealthChanger/KTC-Easy workflow using the SexBolt/SexBall probe and `tools_calibrate`.

## Backups Created

Backup before switching back to the official SexBolt workflow:

`config/_backups/sexbolt-official-20260516-210825/`

Backup for the later M1-STOP/PF4 wiring change:

`config/_backups/sexbolt-m1-stop-20260517-155108/`

Backup before converting comments and guide text to English:

`config/_backups/english-comments-20260517-155728/`

Backed up files:

- `Printer-Setup/probe-mesh.cfg`
- `toolchanger/toolchanger-config.cfg`
- `Printer-Setup/calibration.cfg`

## Current Configuration Changes

- Commented out the whole `[axiscope]` block in `Printer-Setup/probe-mesh.cfg`.
- Re-enabled `[tools_calibrate]` in `toolchanger/toolchanger-config.cfg`.
- Kept the active SexBolt/SexBall probe settings:
  - `pin: ^PF4` on M1-STOP of the Manta M8P V2.0
  - `trigger_to_bottom_z: 0.9`
  - `samples: 5`
  - `samples_result: median`
  - `probe: probe`
- Updated the SexBolt/SexBall coordinates:
  - `_CALIBRATION_SWITCH.variable_x: 257`
  - `_CALIBRATION_SWITCH.variable_y: 327`
  - `_CALIBRATION_SWITCH.variable_z: 60`
  - `Z55` is the estimated contact/top-of-ball height and must not be used as the safe approach Z.
- Updated `Printer-Setup/calibration.cfg` to document the `CALIBRATE_ALL_OFFSETS` XYZ-offset workflow.
- Added public macro `CHECK_OFFSETS`, which calls `_CHECK_OFFSETS`, so the guide command exists.
- Converted comments, descriptions, and guide text in the touched config files to English/ASCII where practical.

## Earlier Work Summary

- Read and analyzed `Axiscope-cartographer-main/klippy/extras/axiscope.py`.
- Found that the original Axiscope Cartographer path read the wrong touch-probe result and returned `2.000` instead of `cartographer.touch.last_z_result`.
- Updated `axiscope.py` to read `cartographer.touch.last_z_result` and removed the incorrect fallback to current toolhead Z.
- Tested with printer logs: Axiscope returned real contact Z values such as T1/T2/T3/T4 near `0.022`, `-0.114`, `-0.314`, and `-0.324`.
- Compared those values with Ellis3DP first-layer offsets and concluded that Cartographer touch values do not directly match the offsets that produce a good printed first layer.
- Created GitHub repo `https://github.com/Batcandoionline/Axiscope-cartographer` for the Axiscope Cartographer fork, including `README.md`, `FORK_INFO.md`, installer/uninstaller scripts, and Moonraker Update Manager configuration.
- Then paused Axiscope work and returned to the official StealthChanger SexBolt/SexBall workflow.

## Recommended Workflow After Loading This Config

1. Restart Klipper.
2. Run:

   ```gcode
   G28
   QUAD_GANTRY_LEVEL
   G28 Z
   CALIBRATE_ALL_OFFSETS
   ```

3. After the macro saves offsets with `SAVE_TOOL_PARAMETER`, run `FIRMWARE_RESTART`.
4. Check results:

   ```gcode
   CHECK_OFFSETS
   ```

## Notes

- Do not enable `[axiscope]` and `[tools_calibrate]` at the same time because both use the `probe_multi_axis` helper.
- If the SexBolt/SexBall state is wrong, check `^PF4` with `QUERY_ENDSTOPS`; if the logic is inverted, change it to `^!PF4`.
- If SexBolt Z offsets differ from Ellis/first-layer results, use Ellis/first-layer testing as the final print-quality confirmation.

## 2026-05-17 Update - SexBolt Wiring Moved to M1-STOP/PF4

- According to the Manta M8P V2.0 pinout: `M1-STOP = PF4`, `M3-STOP = PF2`, and `M5-STOP = PF0`.
- Kept `stepper_x.endstop_pin: PF0` because that is M5-STOP and does not conflict with M1-STOP.
- Changed `[tools_calibrate] pin` from `^PF2` to `^PF4`.
- Changed the `CALIBRATE_MOVE_OVER_PROBE` / `_CALIBRATION_SWITCH` ball center to `X257 Y327`.
- Kept safe approach Z at `60`; `Z55` is only the estimated ball contact/top height used when re-measuring `trigger_to_bottom_z`.

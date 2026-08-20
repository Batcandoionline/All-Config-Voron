# Tool Vision integration plan

Goal: replace the active Axiscope calibration backend with Tool Vision for
relative X/Y camera measurement and PF2 switch Z measurement, without changing
the existing production offsets until results are mechanically validated.

## Current boundary

- Axiscope is active and its service is running.
- Tool Vision is not included in Klipper and its service is not installed.
- The MF-500 normally monitors the print chamber through crowsnest at
  1280x720/30 MJPEG.
- The same camera is manually moved to a keyed magnetic bed mount for nozzle
  calibration. There is no second camera.
- The switch currently uses `^PF2` at measured X=68, Y=-10, Z=7.
- Tool Vision remains report-only and never writes production offsets.

## Configuration contract

Every printer supplies its own `.cfg` values. The user manually measures them;
Tool Vision never estimates or copies station positions from another machine.

1. Seat the camera on the magnetic calibration mount.
2. Confirm the mount is fully keyed, cannot rock or slide, and the stream shows
   a stable upward nozzle view.
3. Select T0, jog to optical focus, and record `camera_x_pos`, `camera_y_pos`,
   `camera_z_pos`, and a collision-safe `camera_safe_z`.
4. Jog T0 to the switch center/contact and record `pin`, `zswitch_x_pos`,
   `zswitch_y_pos`, `zswitch_z_pos`, and `zswitch_safe_z`.
5. Set resolution/FPS to `0` unless a direct device requires an explicit mode;
   Tool Vision consumes the camera's actual frame size and does not resize it.

Re-measure after changing the camera mount, switch, bed location, tool carriage,
or any relevant mechanical component.

## Phase 1 — Stage software without changing production Klipper

1. Confirm printer state: `ready`, `standby`, not paused, no active tool, heater
   targets at zero.
2. Make local and printer-side backups.
3. Install Tool Vision from its official standalone installer with
   `--no-restart`. The installer stores only runtime files under
   `~/printer_data/tool-vision`; it does not clone Axiscope or kTAMV to the Pi.
4. Edit `~/printer_data/config/Tool-Vision/tool_vision.cfg` with the manually
   measured values.
5. Do not edit `printer.cfg` yet. Verify the service health independently.

Exit criterion: service responds, the config is preserved on the Pi, and
production Klipper remains unchanged.

## Phase 2 — Controlled backend cutover

Only one backend may allocate `probe_multi_axis`.

1. Comment the complete active `[axiscope]` section in
   `Printer-Setup/calibration.cfg`.
2. Uncomment `[include Tool-Vision/tool_vision.cfg]` in `printer.cfg`.
3. Restart Klipper while idle; do not home automatically.
4. Confirm `TV_STATUS`, `TV_PREFLIGHT`, and `TV_SERVER_CONFIGURE`.
5. Run `TV_CAMERA_CHECK` with T0 manually visible. This command does not move.
6. Confirm Axiscope commands are absent and Tool Vision commands are present.

Exit criterion: Klipper is `ready`, Tool Vision reports five dynamic tools, and
there are no duplicate-chip/config errors.

## Phase 3 — Supervised commissioning

No full five-tool run is allowed initially.

1. Recheck both manually measured station coordinate sets.
2. Run `TV_ARM CAMERA=1 SWITCH=1`. This confirms physical inspection for the
   current Klipper session and invalidates any previous camera transform.
3. At conservative speed, run `TV_MOVE_TO_CAMERA`; verify safe-Z-before-XY and
   optical focus.
4. Run `TV_CALIBRATE_CAMERA TOOL=0`; accept only stable detection with RMS below
   the configured limit.
5. Measure T0 XY twice as reference and compare repeatability.
6. Run `TV_MOVE_TO_ZSWITCH` and stop before probing if approach geometry is not
   visibly correct.
7. Measure T0 Z reference repeatedly.
8. Measure one non-reference tool and compare sign/delta with known offsets.
9. Only after those checks, run `TV_CALIBRATE_ALL MODE=XYZ`.
10. Save the report, run `TV_DISARM`, then remove the camera from the bed mount
    and return it to chamber monitoring.

Because the camera is removable, each new calibration session starts with
physical mounting, manual station verification, `TV_ARM`, and
`TV_CALIBRATE_CAMERA`. A transform from a previous installation is not reused.

## Phase 4 — Validate results before application

1. Repeat all T0 and one secondary-tool measurements at least three times.
2. Compare Tool Vision results with current production offsets and explain any
   systematic difference.
3. Apply candidate offsets only through explicit reviewed commands; never let
   Tool Vision write `printer.cfg` automatically.
4. Validate on a controlled first-layer print at the actual bed/nozzle thermal
   condition.
5. Keep the existing offset set if the mechanical measurements are repeatable
   but print quality is worse.

## Rollback

1. Run `TV_DISARM` and stop the Tool Vision service.
2. Comment the Tool Vision include.
3. Restore the backed-up `[axiscope]` section.
4. Restart Klipper while idle and verify Axiscope commands return.
5. Production offsets in SAVE_CONFIG remain unchanged throughout the rollback.

## Work still requiring the owner at the printer

- Mount the MF-500 on the magnetic bed fixture.
- Manually measure camera station coordinates.
- Confirm the already recorded switch station or re-measure it if the switch
  has moved.
- Supervise every initial motion, probe, toolchange, and first-layer test.

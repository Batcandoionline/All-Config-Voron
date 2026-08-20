# Five-tool StealthChanger operating guide

This is the concise operating map for the production Voron 2.4 350. Exact
hardware values are maintained in [hardware-invariants.md](hardware-invariants.md).

## Configuration flow

`printer.cfg` loads KTC-Easy first, then user-owned compatibility/configuration
layers. Never edit `toolchanger/readonly-configs`; the official KTC installer
owns that directory.

```text
printer.cfg
├── mainsail.cfg
├── KTC-Easy readonly include
│   ├── homing and toolchanger macros
│   ├── tools/T0.cfg ... T4.cfg
│   └── toolchanger-config.cfg (user overrides)
├── crash_detection_override.cfg
├── calibration.cfg and hardware.cfg
├── probe/fan/input-shaper/clean/prime/print modules
└── tool_crash_cartographer.cfg
```

The deployment scripts preserve KTC readonly links and machine-local Tool
Vision files. A warning about regular readonly files must be repaired by the
official KTC-Easy installer, not by copying snapshots.

## Five tools

All five tools are real independent EBB36 V1.2 CAN nodes. T0 is the offset
reference. Each tool owns its MCU, extruder, heater, fans, LED, presence input,
dock coordinates, and input-shaper candidates in `toolchanger/tools/T*.cfg`.

KTC-Easy performs tool selection through `T0`..`T4`. The user override:

1. raises Z before travel;
2. moves to the rear safe Y zone;
3. stops crash detection during intentional docking transitions;
4. follows the measured pickup/dropoff path at the configured path speed;
5. validates presence pins where the path requests verification;
6. restores LED and input-shaper state for the selected tool.

Do not edit dock coordinates or paths without direct mechanical supervision.

## Homing, leveling, and print start

Cartographer is fixed to the shuttle. It is not a tool presence sensor and does
not need a per-tool probe offset transform.

Typical production start sequence:

1. stop crash detection;
2. select and heat the requested initial tool as defined by print macros;
3. home safely;
4. clean the nozzle;
5. run QGL when required;
6. use Cartographer Touch for the Z reference;
7. create/load bed mesh according to the configured workflow;
8. prime the selected tools;
9. start crash detection only after a printing tool is mounted.

The machine uses QGL retry tolerance 0.0075 and Cartographer bed-mesh zero
reference at nozzle X=174/Y=168. Those measured choices must remain unchanged
during software cleanup.

## Print end, pause, and crash recovery

Normal PAUSE/RESUME follows the Mainsail/KTC workflow. Tool crash recovery is
deliberately different: `_TOOL_CRASH_SAFE_PAUSE` calls `PAUSE_BASE`, saves the
active heater target, retracts E when possible, and makes no X/Y/Z park move.

After a crash pause:

1. do not immediately press Resume;
2. inspect whether the tool is physically attached and aligned;
3. inspect dock, wiring, CAN cable, nozzle, bed, and printed part;
4. rescue/secure the tool manually;
5. choose Resume only when the existing coordinate state is trustworthy;
6. otherwise use Cancel and re-home after clearing the machine.

The custom pause cannot cancel motion already queued inside Klipper and is not
a hardware emergency stop.

## Tool offsets

The currently printed production offsets live in the SAVE_CONFIG block of
`printer.cfg`. `CHECK_OFFSETS` reports X/Y/Z for all five tools without motion.

Axiscope remains the active temporary backend. Legacy KTC
`CALIBRATE_ALL_OFFSETS` is intentionally blocked because `tools_calibrate` is
not configured. The replacement plan is Tool Vision:

- camera XY from the MF-500 on its keyed magnetic bed mount;
- switch Z from the manually measured PF2 station;
- dynamic discovery of T0..T4;
- native camera frames, no forced 640x480 resize;
- report-only results, never automatic SAVE_CONFIG changes.

Only one `[axiscope]`, `[tools_calibrate]`, or `[tool_vision]` section may be
loaded. Follow [toolvision-integration-plan.md](toolvision-integration-plan.md)
for staging, arming, commissioning, first-layer validation, and rollback.

## Read-only checks

These commands do not home, heat, or move:

```gcode
CALIBRATION_STATUS
CHECK_OFFSETS
```

After Tool Vision is installed and selected, these are also no-motion checks:

```gcode
TV_STATUS
TV_PREFLIGHT
TV_SERVER_CONFIGURE
TV_CAMERA_CHECK
```

`TV_ARM` changes only the Tool Vision session lock, but it is a human assertion
that the physical stations have been inspected. Movement still requires the
separate `TV_MOVE_*`/measurement commands.

## Update and recovery

Run updates only while Klipper is ready/standby, no tool is active, and heater
targets are zero.

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

The script backs up the current payload first. After deployment:

1. inspect the diff/backup path and any KTC warning;
2. restart Klipper without issuing automatic movement;
3. confirm all seven CAN MCU objects (main, Cartographer, EBB0..EBB4);
4. run the read-only checks;
5. test one homing/toolchange/probe sequence under direct supervision;
6. run a controlled first-layer print before declaring production-ready.

## Official sources

- [Klipper configuration reference](https://www.klipper3d.org/Config_Reference.html)
- [KTC-Easy](https://github.com/jwellman80/klipper-toolchanger-easy)
- [Cartographer configuration reference](https://docs.cartographer3d.com/cartographer-probe/reference/configuration-reference)
- [crowsnest camera configuration](https://github.com/mainsail-crew/gb-crowsnest/blob/main/configuration/cam-section.md)
- [tool_crash](https://github.com/cekim-git/tool_crash)

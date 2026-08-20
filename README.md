# Voron 2.4 350 — Five-Tool StealthChanger

Production Klipper configuration for one Voron 2.4 350 with five automatic
StealthChanger tools. Hardware values in this repository are measured machine
data: do not copy them to another printer without re-measuring, and do not
change them during a software cleanup.

## Current production state

| Area | Active implementation |
|---|---|
| Host/controller | Manta M8P V2 + CM4, Debian 12/MainsailOS |
| Motion | Klipper `v0.13.0-740`, CoreXY, five EBB36 V1.2 CAN toolheads |
| Toolchanger | KTC-Easy `v0.0.0-258` |
| Bed probe | Fixed Cartographer V3, Touch + Scan |
| Tool XYZ calibration | Axiscope is the temporary production backend |
| Future calibration | Tool Vision camera XY + PF2 switch Z, staged only |
| Crash handling | `tool_crash` detection pins; safe pause without XYZ park |
| Camera | One MF-500 at 1280x720/30 MJPEG through crowsnest |

Tool Vision is developed separately at
[IDcrazy123/Tool-Vision](https://github.com/IDcrazy123/Tool-Vision). Axiscope and
kTAMV are reference-only dependencies in that PC repository; they are not
copied to the printer as Tool Vision runtime.

## Locked hardware inventory

| Device | Measured production value |
|---|---|
| Main MCU | `19b203d75137` |
| Cartographer | `da13d909ce34`, firmware 6.1.0 |
| T0 EBB36 | `441e1484ac41` |
| T1 EBB36 | `6475b5b9e028` |
| T2 EBB36 | `4ad9d622a836` |
| T3 EBB36 | `c2465b7c36f8` |
| T4 EBB36 | `28650279df58` |
| Hotends/extruders | 5x TZ V6 2.0 + 5x WW BMG |
| Bed | 1000 W AC pad, SSR control `PA1`, MGB18 NTC on `PB0` |
| Chamber | Generic 3950 100K NTC on `PB1` |
| Tool calibration switch | `^PF2`; current measured station X=68, Y=-10, Z=7 |

The full preservation contract is in
[hardware-invariants.md](extras/docs/hardware-invariants.md).

## Tool map

| Tool | Dock X/Y/Z (mm) | Production X/Y/Z offset (mm) |
|---|---|---|
| T0 | `30.20 / 1.30 / 343` | `0 / 0 / 0` reference |
| T1 | `104.00 / 1.10 / 343` | `-0.243 / -0.252 / +0.228` |
| T2 | `176.00 / 1.60 / 343` | `+0.746 / +0.086 / -0.295` |
| T3 | `249.50 / 2.50 / 343` | `+0.304 / +0.449 / -0.268` |
| T4 | `321.50 / 2.60 / 343` | `+0.041 / +0.352 / -0.014` |

Offsets in `printer.cfg` are production values validated by first-layer
results. A camera/switch measurement is a new candidate, not permission to
overwrite these values automatically.

## Calibration architecture

Cartographer is fixed to the shuttle and remains responsible for Z homing,
gantry leveling, and bed mesh. Relative tool offsets use a separate backend.
Only one of the following may exist in a loaded Klipper configuration because
each can allocate `probe_multi_axis`:

```ini
[axiscope]        # active today
[tool_vision]     # planned replacement
[tools_calibrate] # inactive legacy SexBolt backend
```

The MF-500 normally monitors the chamber. When offset calibration is required,
the user removes it and seats it on the keyed magnetic bed mount as an
upward-facing nozzle camera. The magnetic mount controls position and vibration,
but the user must still manually determine the camera station and confirm the
image each time. Switch coordinates are measured and configured the same way.
Neither project code nor an image estimate may invent station coordinates.

The controlled Tool Vision cutover and rollback sequence is documented in
[toolvision-integration-plan.md](extras/docs/toolvision-integration-plan.md).

## Crash behavior

Each `[tool]` supplies a `detection_pin`. The `tool_crash` plugin watches those
pins while printing. On a failure it calls `_TOOL_CRASH_SAFE_PAUSE`:

- the virtual-SD print is paused;
- no automatic X/Y/Z park move is requested;
- a normal resume/cancel decision remains available after manual inspection;
- outside an active print, the handler reports the event without shutdown or
  motion.

`crash_detection_override.cfg` is required. It routes KTC-Easy's generic
`START_CRASH_DETECTION`/`STOP_CRASH_DETECTION` macros to `tool_crash`.
`tool_crash_cartographer.cfg` configures the detector and pause handler. Despite
its historical filename, Cartographer is not a crash-detector input.

Custom crash G-code is processed behind motion already queued by Klipper; it is
not equivalent to an immediate hardware emergency stop.

## Repository layout

```text
Voron 5 Tool/
├── config/                         Deployed Klipper/Moonraker payload
│   ├── printer.cfg                 Main include graph and SAVE_CONFIG
│   ├── Printer-Setup/              Hardware, probe, safety, print macros
│   ├── toolchanger/
│   │   ├── tools/T0.cfg ... T4.cfg User-owned tool definitions
│   │   ├── toolchanger-config.cfg  User-owned KTC overrides and motion paths
│   │   └── readonly-configs/       KTC-Easy installer-managed; never edit
│   └── scripts/                    Backup/install/update scripts
├── Orca Config/                    Slicer profiles
└── extras/
    ├── backups/                    Timestamped recovery snapshots
    ├── docs/                       Hardware and integration documents
    └── Nhat-ky-chinh-sua/          Daily engineering log
```

## Deployment

Both scripts create a timestamped backup before changing the printer payload.
They preserve machine-local Tool Vision files, Codex backups, Moonraker-generated
files, Markdown, and KTC-Easy `readonly-configs`.

```bash
# First installation from a checked-out repository
bash "Voron 5 Tool/config/scripts/install.sh"

# Update an existing printer checkout
cd ~/printer_data/config
bash scripts/update.sh
```

If the script warns that KTC readonly files are not installer-managed symlinks,
run the official KTC-Easy installer during a supervised maintenance window:

```bash
bash ~/klipper-toolchanger-easy/install.sh
```

Do not copy or edit files in `toolchanger/readonly-configs` to silence the
warning. User-owned compatibility guards keep the current machine safe until
the official installer can restore those links.

## Safe validation order

1. Confirm Klipper is `ready`, print state is `standby`, heaters are off, and no
   tool is active.
2. Parse/restart Klipper without homing or moving.
3. Run `CALIBRATION_STATUS` and `CHECK_OFFSETS` (read-only).
4. Test homing and one tool pickup/dropoff under direct supervision.
5. Test Cartographer Touch/QGL and a small calibration print.
6. Commission Tool Vision only through the separate staged plan.

Official references used for the current logic:

- [Klipper configuration reference](https://www.klipper3d.org/Config_Reference.html)
- [KTC-Easy](https://github.com/jwellman80/klipper-toolchanger-easy)
- [Cartographer Klipper setup](https://docs.cartographer3d.com/cartographer-probe/installation-and-setup/software-configuration/klipper-setup)
- [crowsnest camera configuration](https://github.com/mainsail-crew/gb-crowsnest/blob/main/configuration/cam-section.md)
- [tool_crash](https://github.com/cekim-git/tool_crash)

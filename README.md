# Voron 2.4 StealthChanger — five-tool production configuration

[English](README.md) | [Tiếng Việt](README.vi.md) | [Documentation index](extras/docs/README.md)

This repository is the reviewed configuration and deployment payload for one
Voron 2.4 350 mm CoreXY printer with five StealthChanger tools. It is not a
generic configuration template. Hardware identifiers, motion limits, dock
positions and offsets below are read from the tracked configuration at commit
`9d848f04` on 2026-08-24.

Status labels used in this document:

- **Active:** loaded by `config/printer.cfg`.
- **Observed:** confirmed in a recorded printer session, but not a universal
  hardware claim.
- **Development:** implemented in another branch/project but not deployed to
  this printer unless explicitly stated.

## Active system

| Area | Tracked configuration |
| --- | --- |
| Printer | Voron 2.4, CoreXY, X `0..348`, Y `-10..336`, maximum velocity `300 mm/s`, maximum acceleration `4000 mm/s²` |
| Controller | BTT Manta M8P V2.0 with CM4; main CAN UUID `19b203d75137` |
| Toolchanger | KTC-Easy StealthChanger, T0–T4; rear docks at Z `343 mm` |
| Tool boards | Five BTT EBB36 boards on CAN, one extruder/heater/fan/filament sensor per tool |
| Z and mesh | Cartographer V3, CAN UUID `da13d909ce34`; Touch Z reference plus adaptive scan mesh |
| Tool-offset measurement | ToolVision development canary, report-only; physical switch on Manta `^PF2` |
| Bed/chamber | 1000 W AC bed through SSR `PA1`, bed sensor `PB0`, chamber sensor `PB1` |
| Nozzle service | Purge bucket and Bambu A1 silicone cleaning pad |
| UI/slicer | Mainsail, KlipperScreen in Vietnamese, OrcaSlicer toolchanger profiles |

KTC-Easy is the sole owner of
`config/toolchanger/readonly-configs/`. This repository owns the editable
KTC override and T0–T4 definition files. Deployment deliberately refuses to
continue when the six installer-managed readonly symlinks are missing or
broken.

## Tool map and print-tested offsets

The operator reported the current first layer as visually good. These values
are therefore the production baseline, not values to be overwritten from one
diagnostic run.

| Tool | CAN UUID | Dock XY at Z 343 | X offset | Y offset | Z offset |
| --- | --- | --- | ---: | ---: | ---: |
| T0 | `441e1484ac41` | `30.20, 1.30` | `0.000` | `0.000` | `0.000` |
| T1 | `6475b5b9e028` | `104.00, 1.10` | `-0.243` | `-0.252` | `+0.228` |
| T2 | `4ad9d622a836` | `176.00, 1.60` | `+0.746` | `+0.086` | `-0.295` |
| T3 | `c2465b7c36f8` | `249.50, 2.50` | `+0.304` | `+0.449` | `-0.268` |
| T4 | `28650279df58` | `321.50, 2.60` | `+0.041` | `+0.352` | `-0.014` |

The offset source is the `SAVE_CONFIG` block in `config/printer.cfg`. Per-tool
CAN pins, rotation distance, dock paths and input-shaper profiles are defined
in `config/toolchanger/tools/T0.cfg` through `T4.cfg`.

## Loaded configuration order

`config/printer.cfg` loads, in order:

1. Mainsail and KTC-Easy's managed include.
2. Cartographer/calibration routing and ToolVision.
3. Hardware, fans/LEDs, input shaper, nozzle cleaning, prime lines and print
   macros.
4. Tool-crash handling after the tool definitions supplied by KTC-Easy.

Axiscope and `[tools_calibrate]` are retained only as commented rollback
material in `calibration-probe.cfg`; neither section is active. Cartographer is
the production Z/mesh probe. ToolVision owns PF2 for attended diagnostic
tool-offset measurement.

## Print workflow implemented in code

`PRINT_START` validates slicer parameters, stops stale dryer/crash state,
starts bed and tool heating asynchronously, homes all axes before selecting a
tool, cleans T0, waits for the bed, performs an optional temperature-dependent
heat soak, runs QGL, cleans T0 again, performs Cartographer Touch homing, builds
an adaptive mesh and primes every slicer-used tool. The requested initial tool
is primed last and tool-crash detection is enabled only after preparation.

Automatic heat-soak defaults are read from `print-macros.cfg`:

| Material group | Cold-bed soak |
| --- | ---: |
| PLA/TPU | 30 s |
| PETG | 60 s |
| ABS/ASA/PC/NYLON/PA | 90 s |

When the bed is within 5 °C of target, the automatic soak is skipped. A
5–15 °C difference uses 20% of the duration. `SOAK=` overrides the duration;
`AUTO_SOAK=0` disables the automatic calculation.

`PRINT_END` stops crash detection, turns off print-owned heaters/fans, drops
the active tool and parks the shuttle empty. It does **not** promise to finish
with T0 mounted.

Public maintenance macros include `CLEAN_NOZZLE`, `PURGE_AND_CLEAN`,
`PRIME_LINES`, `CALIBRATION_STATUS`, `CHECK_OFFSETS`, `START_DRYER`,
`STOP_DRYER` and `DRYER_STATUS`.

## ToolVision on this printer

The deployed integration is a monitored development canary:

- Runtime checkout: `~/Tool-Vision`
- Isolated Python environment: `~/tool-vision-env`
- Host service: `tool-vision.service`, loopback API on port `8085`
- Machine configuration: `config/Printer-Setup/tool-vision.cfg`
- Learned state: `~/printer_data/config/Generated-Data/ToolVision/state.json`
- Latest result: `~/printer_data/config/Generated-Data/ToolVision/results.json`

The tracked machine panel currently uses the generic Setup/Calibrate layout.
PF2 switch Z and Cartographer Touch Z were both observed on real hardware on
2026-08-23. Camera XY is available in ToolVision but has not been taught for
this repository deployment. Every result is diagnostic: ToolVision does not
write the production T0–T4 offsets.

The newer ToolVision branch `codex/z-calibration-ux` at `2d936f3` implements
method-specific Z buttons, `VERBOSITY=QUIET`, unambiguous `NOT APPLIED` labels
and a bounded 20-record history. ToolVision's own test documentation states
that this branch has component/fake evidence only and has not been deployed or
HIL-tested on the production printer. See the
[implementation status](extras/docs/toolvision-z-calibration-ux-proposal.md).

For the current machine integration and safe non-motion checks, use the
[English guide](extras/docs/toolvision-integration-guide.en.md) or the
[Vietnamese guide](extras/docs/toolvision-integration-guide.vi.md).

## Bed dryer presets

`START_DRYER` rejects an active print and can optionally home/dock/park before
heating. Presets in `print-macros.cfg` are:

| Material | Bed | Chamber | Duration | Base fan |
| --- | ---: | ---: | ---: | ---: |
| PLA | 50 °C | 40 °C | 240 min | 40% |
| TPU | 60 °C | 45 °C | 300 min | 40% |
| PETG | 70 °C | 55 °C | 240 min | 50% |
| ABS/ASA | 90 °C | 65 °C | 240 min | 60% |
| NYLON | 100 °C | 70 °C | 360 min | 70% |
| PC | 105 °C | 75 °C | 360 min | 70% |

Explicit parameters can override a preset. `CUSTOM` defaults to 55 °C bed,
240 minutes and 40% fan; it has no chamber target unless supplied.

## Repository layout

```text
Voron 5 Tool/
├── README.md / README.vi.md
├── config/
│   ├── printer.cfg
│   ├── Printer-Setup/
│   ├── toolchanger/
│   └── scripts/
├── Orca Config/
└── extras/
    ├── docs/
    ├── Nhat-ky-chinh-sua/
    ├── backups/
    └── retired-configs/
```

Current documentation and translations are indexed in
[`extras/docs/README.md`](extras/docs/README.md). Historical journals and
backup snapshots remain immutable evidence; they are not rewritten to look
like the current system.

## Install and update

Install KTC-Easy first while the printer is idle. For a first All-Config
deployment without keeping another Git checkout on the CM4:

```bash
tmp_dir="$(mktemp -d /tmp/all-config-voron.XXXXXX)"
curl -fsSL https://github.com/IDcrazy123/All-Config-Voron/archive/refs/heads/main.tar.gz \
  | tar -xz -C "${tmp_dir}" --strip-components=1
bash "${tmp_dir}/config/scripts/install.sh"
rm -rf -- "${tmp_dir}"
sudo systemctl restart moonraker klipper
```

For later updates:

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart moonraker klipper
```

`update.sh` downloads a temporary `main` archive and calls `install.sh`.
`install.sh` preflights KTC-Easy, ToolVision and the reviewed tool-crash patch,
creates a timestamped copy under `~/printer_data/config_backups/`, then deploys
repository-owned files. It excludes Markdown, `Generated-Data/`, local
diagnostics and KTC-Easy's readonly directory. Neither script restarts services
automatically.

`cleanup-voron.sh` is only a reviewed dry-run/apply cleaner for legacy
`config.update-backup-*`, `config.backup-*` and `~/axiscope.bak` paths. It does
not implement general retention for `config_backups/`.

## Safety and contribution rules

- Never edit `config/toolchanger/readonly-configs/` in this repository.
- Do not run deploy, homing, toolchange, probing or calibration during a print.
- Back up tracked configuration before changing `.cfg`, `.conf` or `.sh`.
- Keep generated printer data and credentials out of Git.
- Treat ToolVision measurements as report-only candidates until repeated under
  matching conditions and validated independently by a print or another
  approved method.
- Preserve historical journals and backup snapshots; add new evidence instead
  of rewriting old evidence.

# ToolVision Integration Guide — Private Voron Installation

[English](toolvision-integration-guide.en.md) | [Tiếng Việt](toolvision-integration-guide.vi.md)

## Scope

This guide documents the machine-specific ToolVision integration used by this
five-tool Voron 2.4. ToolVision is an independent runtime; this repository owns
only the printer-specific Klipper configuration, deployment checks, and data
placement rules.

ToolVision is report-only. It measures candidate XYZ offsets and reference
drift but never writes production tool offsets automatically.

## Owned paths

| Path | Owner | Purpose |
| --- | --- | --- |
| `~/Tool-Vision/` | ToolVision Git checkout | Host service and Klipper extension source |
| `~/tool-vision-env/` | ToolVision installer | Isolated Python environment |
| `/etc/systemd/system/tool-vision.service` | ToolVision installer | Loopback host API service |
| `~/printer_data/config/Printer-Setup/tool-vision.cfg` | All-Config | Machine pin, JSON paths, and Mainsail panel |
| `~/printer_data/config/Generated-Data/ToolVision/state.json` | ToolVision runtime | Learned station and selected-method state |
| `~/printer_data/config/Generated-Data/ToolVision/results.json` | ToolVision runtime | Latest completed measurement report |

All future ToolVision-generated JSON for this printer must remain under
`Generated-Data/ToolVision/`. Do not place generated data beside `printer.cfg`
or inside `Printer-Setup/`.

The complete `Generated-Data/` tree is ignored by Git and excluded from the
configuration deployer's `rsync --delete`. Updating All-Config therefore does
not delete the learned state or measurement result.

## Required integration

The active include in `printer.cfg` is:

```ini
[include Printer-Setup/tool-vision.cfg]
```

The machine configuration pins ToolVision's physical switch to Manta M8P
`^PF2` and routes runtime files explicitly:

```ini
[tool_vision]
pin: ^PF2
state_file: ~/printer_data/config/Generated-Data/ToolVision/state.json
result_file: ~/printer_data/config/Generated-Data/ToolVision/results.json
```

Before deploying that include, `config/scripts/install.sh` verifies the
ToolVision Git checkout, isolated Python interpreter, systemd unit, and all five
Klipper extension symlinks. It also preserves KTC-Easy's installer-managed
`toolchanger/readonly-configs/` directory.

## Safe update procedure

Perform updates only while the printer is idle. Do not run this procedure during
a print, a pause, a ToolVision job, or an attended calibration.

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

The updater downloads the reviewed `main` archive, executes the backup-first
installer, deploys repository-owned files, and removes its temporary archive.
It does not restart services automatically.

After reviewing the installer output, restart Moonraker first and Klipper
second:

```bash
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

No homing, probing, toolchange, or heater command is required for this layout
update.

## Non-motion verification

Confirm the services and Klipper state:

```bash
systemctl is-active tool-vision.service moonraker klipper
```

From the Mainsail console, run:

```text
TOOL_VISION_STATUS
QUERY_ENDSTOPS
```

Expected results:

- Klipper is `ready` and the printer is `standby`.
- ToolVision reports `busy=false` and no last error.
- `ToolVision switch` is normally `open` when nothing presses PF2.
- All heater targets remain `0` unless the operator intentionally starts a
  calibration.
- `state.json` and `results.json` remain under
  `Generated-Data/ToolVision/`.

Opening the `TOOL_VISION` Mainsail macro only displays the panel. Setup and
calibration actions can move the printer and must still be attended.

## Z-method note

ToolVision may store `switch` or `cartographer_touch` as the selected Z method.
Teaching one method can replace the selected method in `state.json`. Always
confirm the displayed method before starting a Z run.

Reported Z is measured relative to the reference tool. Treat it as a candidate
absolute relative value, not as a correction delta to add to the current
production offset. Repeat the same method and temperature at least three times
before evaluating a manual `0.01 mm` print adjustment.

## Backup and rollback

Every deployment creates a timestamped snapshot under:

```text
~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/
```

To roll back this layout change, restore `printer.cfg`, the former root
`tool_vision.cfg`, and `scripts/install.sh` from the matching snapshot, then
restart Moonraker and Klipper while the printer is idle. Do not restore or erase
`Generated-Data/ToolVision/` unless the learned state itself is the intended
rollback target.

## Troubleshooting

- **Unknown section `tool_vision`:** verify all five Klipper extension symlinks
  and restart Klipper after installing the runtime.
- **Include file not found:** confirm the exact case-sensitive path
  `Printer-Setup/tool-vision.cfg`.
- **Setup appears lost:** verify `Generated-Data/ToolVision/state.json` exists
  and is readable by the `voron` user before teaching again.
- **No latest result:** inspect
  `Generated-Data/ToolVision/results.json` and `TOOL_VISION_STATUS`; do not
  create placeholder JSON manually.
- **Update preflight refuses deployment:** fix the named runtime, symlink, or
  KTC-Easy ownership problem first. Do not bypass the check.

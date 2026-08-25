# ToolVision integration — private five-tool Voron

[English](toolvision-integration-guide.en.md) | [Tiếng Việt](toolvision-integration-guide.vi.md)

## Verified scope

This guide describes the All-Config integration, not every capability in the
independent ToolVision repository. Source and printer evidence were refreshed
through 2026-08-25 against:

- the current All-Config worktree and its backed-up live configuration;
- ToolVision branch `codex/compact-mainsail-output` at `dd645103`, version
  `3.4.0-rc2`;
- GitHub Security Gate, real Mainsail prompt rendering and attended dual-method
  HIL on the private five-tool printer.

ToolVision remains report-only. It measures candidate relative offsets and
never calls `SAVE_CONFIG` or writes T0–T4 production offsets.

## Runtime and data ownership

| Path | Owner | Current purpose |
| --- | --- | --- |
| `~/Tool-Vision/` | ToolVision/Moonraker Git updater | Host and Klipper extension source |
| `~/tool-vision-env/` | ToolVision installer | Isolated host Python environment |
| `/etc/systemd/system/tool-vision.service` | ToolVision installer | Loopback-only host API |
| `Printer-Setup/tool-vision.cfg` | All-Config | PF2, JSON paths and current Mainsail panel |
| `Generated-Data/ToolVision/state.json` | ToolVision runtime | Learned station/method state |
| `Generated-Data/ToolVision/results.json` | ToolVision runtime | Backward-compatible latest successful result |

`Generated-Data/` is excluded from Git and All-Config's `rsync --delete`, so a
configuration update does not remove learned state or results.

The deployed immutable history directory follows the parent of the configured
result file:

```text
Generated-Data/ToolVision/tool-vision-history/
```

`results.json` remains the backward-compatible latest result; each completed or
failed session also writes a dated, method-labelled history record.

## Active machine configuration

`printer.cfg` loads:

```ini
[include Printer-Setup/tool-vision.cfg]
```

The machine-specific section is:

```ini
[tool_vision]
pin: ^PF2
state_file: ~/printer_data/config/Generated-Data/ToolVision/state.json
result_file: ~/printer_data/config/Generated-Data/ToolVision/results.json
toolchanger_recovery_gcode:
  INITIALIZE_TOOLCHANGER
```

The recovery hook is reviewed for this KTC Easy machine. It is not a portable
default and must not be copied to another toolchanger without verifying its
initialization behavior at calibration failure positions.

The physical-switch method depends on `tools_calibrate.py` being installed by
KTC-Easy, but its `[tools_calibrate]` section must remain disabled while
`[tool_vision]` is active. Axiscope is also disabled. Cartographer remains the
production Z/mesh probe.

Camera discovery exists in ToolVision, but this All-Config file does not set a
camera source/name and the recorded printer status said camera setup was not
ready. Do not document camera XY as active until an attended setup and evidence
are recorded.

## Current deployed UI

The canary runtime at `dd645103` and the All-Config panel were deployed and
attended-HIL tested on 2026-08-25. The main page now contains only:

- `Measure Z - Physical switch`;
- `Measure Z - Cartographer Touch`;
- `Latest results`;
- `Advanced setup` and `Close`.

Each Z action passes an explicit `METHOD=` and `VERBOSITY=QUIET`. Teaching a
station can change the stored default, but it cannot silently change either
named Z action. `Latest results` labels the method and mode from the immutable
last-session record, preserves an exact `0.0` drift, and always states
`NOT APPLIED`.

Opening the panel now produces eight prompt responses instead of eleven. Quiet
mode limits ToolVision itself to three messages per successful calibration;
heater waits, KTC toolchanges, physical probe contacts and Cartographer output
are owned by those components and remain visible. Do not regex-hide
`action:prompt_*`, warnings or errors.

## Safe update procedure

All-Config update, while the printer is idle:

```bash
cd ~/printer_data/config
bash scripts/update.sh
```

The installer verifies the ToolVision checkout, isolated interpreter, systemd
unit and five exact Klipper extension symlinks before it deploys the include.
It also verifies KTC-Easy's six readonly symlinks and creates a configuration
snapshot. The script does not restart services.

After reviewing output:

```bash
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

The current canary follows `codex/compact-mainsail-output`. Refresh Moonraker's
update metadata before updating so its cached remote hash includes the reviewed
commit. Do not use `git pull` directly and do not move another printer to this
development channel without its own backup and attended HIL plan.

## Non-motion verification

On the host:

```bash
systemctl is-active tool-vision moonraker klipper
curl --fail --silent http://127.0.0.1:8085/api/v2/health
```

In Mainsail:

```text
CALIBRATION_STATUS
QUERY_ENDSTOPS
TOOL_VISION_STATUS
```

Expected before a measurement:

- Klipper is ready and printer is idle.
- ToolVision is not busy and has no unexplained last error.
- `ToolVision switch` is normally open when PF2 is not pressed.
- Heater targets are 0.
- State/result remain under `Generated-Data/ToolVision/`.

These checks do not intentionally home, heat, probe or change tools. Opening
the `TOOL_VISION` macro only opens a prompt; Setup/Calibrate actions can move
and heat the printer.

## Reading Z results

The implemented sign is:

```text
measured Z(tool) = raw contact Z(tool) - raw contact Z(reference)
```

Treat the value as a candidate absolute offset relative to T0, not a correction
to add to the configured offset. Match method and temperature when comparing
runs. Review T0 return drift as diagnostic evidence; ToolVision does not define
a universal drift pass/fail threshold.

On 2026-08-25, three valid 150 °C runs per method completed after a full `G28`
before every run. Mean candidate values for T1–T4 were:

| Method | T1 | T2 | T3 | T4 | Mean T0 return drift |
| --- | ---: | ---: | ---: | ---: | ---: |
| PF2 physical switch | +0.121 | -0.385 | -0.179 | +0.093 | +0.033 |
| Cartographer Touch | +0.243 | -0.268 | -0.186 | +0.105 | +0.011 |

Cartographer minus PF2 was `+0.121`, `+0.117`, `-0.007` and `+0.011 mm` for
T1–T4. Both methods were repeatable internally, but the systematic T1/T2
disagreement means the values must not be averaged or applied without further
mechanical investigation. All runs remained report-only and are retained in
dated history; production offsets were not changed.

## Backup and rollback

All-Config deployment snapshots use:

```text
~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/
```

The three printer backups explicitly retained after the 2026-08-23 cleanup are
recorded in that day's immutable journal. The scripts do not enforce a general
“keep N newest” policy.

Before changing the ToolVision runtime/schema or teaching a station, separately
back up:

- `Printer-Setup/tool-vision.cfg`;
- `Generated-Data/ToolVision/state.json`;
- `Generated-Data/ToolVision/results.json`;
- future `Generated-Data/ToolVision/tool-vision-history/`, if it exists;
- the ToolVision commit hash and service status.

Do not erase generated data when rolling back only an All-Config file layout.
Restore state/results only when that data is the intended rollback target and
its schema is compatible with the selected runtime.

## Troubleshooting

- **Unknown section `tool_vision`:** verify all five extension symlinks, then
  restart Klipper while idle.
- **Include not found:** verify exact case
  `Printer-Setup/tool-vision.cfg`.
- **Setup appears lost:** check `Generated-Data/ToolVision/state.json` before
  teaching again.
- **Latest result shows the wrong method or `0.0` drift as `n/a`:** update to
  `dd645103` or later, sync the matching panel, restart Klipper and repeat the
  non-motion `Latest results` check.
- **Too much console output:** confirm the UI action passes
  `VERBOSITY=QUIET`. ToolVision then owns only three calibration messages;
  KTC, heater, probe and Cartographer output is intentionally not hidden.
- **KTC becomes uninitialized after a nested command error:** this machine uses
  the reviewed `INITIALIZE_TOOLCHANGER` recovery hook. Confirm the physically
  detected tool before enabling the same hook on another machine.
- **Deployment preflight fails:** fix the named runtime/symlink/KTC ownership
  issue; do not bypass it.

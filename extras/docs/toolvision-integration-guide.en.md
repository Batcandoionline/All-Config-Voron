# ToolVision integration — private five-tool Voron

[English](toolvision-integration-guide.en.md) | [Tiếng Việt](toolvision-integration-guide.vi.md)

## Verified scope

This guide describes the All-Config integration, not every capability in the
independent ToolVision repository. Source review was refreshed on 2026-08-24
against:

- deployed machine configuration commit `9d848f04`;
- the development-canary runtime recorded on the printer at ToolVision commit
  `2b3bf2c6`, version `3.4.0-rc1`;
- the newer, not-yet-deployed UX branch `codex/z-calibration-ux` at `2d936f3`.

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

When the newer history implementation is eventually reviewed and deployed,
its default history directory follows the parent of the configured result file:

```text
Generated-Data/ToolVision/tool-vision-history/
```

That directory is **not** evidence that the current production runtime already
has history. The recorded runtime at `2b3bf2c6` keeps only `results.json`.

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
```

The physical-switch method depends on `tools_calibrate.py` being installed by
KTC-Easy, but its `[tools_calibrate]` section must remain disabled while
`[tool_vision]` is active. Axiscope is also disabled. Cartographer remains the
production Z/mesh probe.

Camera discovery exists in ToolVision, but this All-Config file does not set a
camera source/name and the recorded printer status said camera setup was not
ready. Do not document camera XY as active until an attended setup and evidence
are recorded.

## Current UI versus development UI

The deployed All-Config panel groups Setup and Calibrate and uses generic Z/XYZ
run buttons. Teaching Switch or Cartographer changes the stored default method;
the generic `MODE=Z` action then uses that state. Always read the method shown
in the panel before motion.

The ToolVision branch at `2d936f3` implements but has not production-deployed:

- method-specific `Measure Z - Physical switch` and `Measure Z - Cartographer
  Touch` actions;
- Advanced Setup separated from routine measurement;
- explicit `METHOD=` on UI-generated Z runs;
- `VERBOSITY=QUIET` for fewer ToolVision-owned console messages;
- immutable method-labelled history with fixed retention 20;
- final `NOT APPLIED` and `Configuration changed: No` metadata.

Its tests are L0–L2/component/fake evidence. ToolVision's own documentation says
Mainsail, simulator and printer HIL are still outstanding. See
[the implementation-status report](toolvision-z-calibration-ux-proposal.md).

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

Do not update the ToolVision Git runtime to `2d936f3` merely because these docs
describe it. Its feature branch is not the `main` updater channel, and deploying
it changes Klipper orchestration and result storage; that requires its own
backup, review and attended HIL plan.

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

On 2026-08-23, one 150 °C PF2 run and one 150 °C Cartographer Touch run
completed. Both returned the printer to a safe idle state with heater targets
at 0, but the second run replaced the first `results.json`. The print-tested
production offsets were not changed. Values and comparison are preserved in
[the UX status report](toolvision-z-calibration-ux-proposal.md).

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
- **Latest PF2 run disappeared after Cartographer:** this is expected behavior
  of the recorded `2b3bf2c6` runtime; recover evidence from the original log,
  not by fabricating JSON.
- **Too much console output:** current production UI does not pass quiet mode.
  The reduction exists only on the un-deployed `2d936f3` branch.
- **Deployment preflight fails:** fix the named runtime/symlink/KTC ownership
  issue; do not bypass it.

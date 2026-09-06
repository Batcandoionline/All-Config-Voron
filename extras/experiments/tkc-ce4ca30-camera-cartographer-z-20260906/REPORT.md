# TKC `ce4ca303` clean reinstall, final camera test, and Cartographer Z trial

## Scope and outcome

The previous TKC installation was removed from the physical printer, the clean state was verified, and upstream `main` was installed again from a fresh clone. The final camera validation passed. The supervised Cartographer Z trial then exposed a release-blocking TKC status bug that shut down Klippy while T1 was being probed.

- **Upstream:** [Tool-Klipper-Calibration at `ce4ca303`](https://github.com/IDcrazy123/Tool-Klipper-Calibration/tree/ce4ca3030e7d3c8d11c3aa1b54daf9242d997624)
- **Revision:** `ce4ca3030e7d3c8d11c3aa1b54daf9242d997624`
- **Reported version:** `v0.8.19`
- **Printer:** `voron-local`, `192.168.1.43`
- **Installed source:** `/home/voron/Tool-Klipper-Calibration`, clean `main`
- **Service:** enabled user unit `tool_calibrator.service`, loopback `127.0.0.1:8090`
- **Machine config:** `~/printer_data/config/Printer-Setup/`
- **Safety controls:** cold test, all heater targets zero, Z raised to 40 mm before tool changes, `SAVE_CONFIG=0`

The final machine state is healthy and ready. T0 is active and detected, XYZ is homed, the carriage is at `X175.8 Y168.0 Z40.0`, all heater targets are zero, TKC vision is fully synchronized, and TKC Z actions are disabled again. No production offset or `printer.cfg` value changed.

## Backup and complete removal checkpoint

Backups were created before any active configuration change.

- Local backup: `extras/backups/pre-tkc-ce4ca30-camera-z-20260906-212025/`
- Printer backup: `/home/voron/printer_data/config_backups/tkc-ce4ca30-camera-z-20260906-212025/`

The live printer configuration, Moonraker configuration, machine TKC config, station data, macro links, service definition, source state, health, printer status, and recent daemon log were preserved. Machine-owned `.cfg` files and `.cfg` symlinks were moved to backup before removal where required by this repository's preservation rules.

The updated upstream uninstaller was run with `--config-subdir Printer-Setup`. It stopped and removed the user unit, removed owned extras links, removed the Moonraker updater block and ASVC entry, archived `tool_offsets.cfg`, and restarted Klipper and Moonraker through their API. The remaining source checkout and generated `.cfg`/`.conf` backups were then moved into the timestamped backup to establish a full removal checkpoint.

The clean checkpoint confirmed:

- `/home/voron/Tool-Klipper-Calibration` absent;
- user unit absent and inactive;
- no TKC process and port 8090 closed;
- no TKC-owned Klipper extras or macro symlink;
- no active TKC include, `[tool_calibrator]` object, `tool_offsets` object, or TKC G-code command;
- no active TKC config artifact outside the timestamped backup;
- Klipper ready after reload;
- kTAMV still running independently on port 8086.

`CALIBRATION_STATUS` remained registered because it is the machine-owned read-only macro in `Printer-Setup/calibration-probe.cfg`; it is not a TKC residue.

Evidence: [uninstaller output](03-uninstall.txt) and [clean-state inventory](04-clean-state.txt).

## Upstream preflight and installation result

The exact upstream revision was cloned into an isolated virtualenv on the Raspberry Pi. **107/107 tests passed in 8.43 seconds** before installation.

The final installation used:

```text
./scripts/install.sh --user-service --config-subdir Printer-Setup
```

The `Printer-Setup` argument was byte-checked as `5072696e7465722d5365747570` before execution. The official installer then completed all six stages:

- created a fresh runtime virtualenv using the published constraints;
- created owned Klipper extras and `z_backends` symlinks;
- placed macro links and the placeholder offset file under `Printer-Setup`;
- configured Moonraker Update Manager and ASVC;
- installed, enabled, and started the user service;
- restarted Klipper and Moonraker through the API;
- reported daemon commit `ce4ca30`.

The machine-owned `Printer-Setup/tool-calibrator.cfg` and station-only `tool_offsets.cfg` were restored after the official installer created its placeholder. `printer.cfg` was restored from the pre-uninstall copy, and a full Klipper service restart loaded the new extras. The source remained clean and Update Manager reported current hash equal to remote hash, zero commits behind, and no TKC warning or anomaly.

Evidence: [preflight tests](02-upstream-preflight.txt), [final clean install](07-install-correct.txt), [post-install verification](08-post-install-verify.txt), and [Update Manager result](24-update-manager-tool-calibrator.json).

### Installer input-validation incident

An earlier invocation received a carriage-return byte at the end of `Printer-Setup` from the PowerShell-to-SSH transport. The installer accepted that control character and created a literal `Printer-Setup\r` directory. The malformed install was inactive because the production TKC includes were still disabled. It was immediately uninstalled, preserved as evidence, and the clean installation above was rerun with byte validation.

This was caused by the calling transport, but it exposed an upstream validation gap: `--config-subdir` accepts control characters, absolute paths, and traversal components without rejecting them. The installer should only accept a normalized relative path made of safe components.

Evidence: [malformed invocation](05-install.txt) and [safe cleanup](06-malformed-cleanup.txt).

## Final camera validation

A normal `G28` completed and initialized T0 correctly. Z was raised to 40 mm before moving near the camera.

At the safe approach point `X171.456 Y43.920 Z40`, a five-frame negative test returned **0/5 valid frames**. It did not raise a G-code error and did not invalidate toolchanger state. This verifies the new confidence/radius gate against the earlier off-camera false positive.

At `X170.910 Y18.917 Z40`, five consecutive stationary tests requested five frames each. All **25/25 frames** passed.

| Run | Valid frames | Center UV (px) | Radius | Confidence | Dispersion |
|---:|---:|---:|---:|---:|---:|
| 1 | 5/5 | 639.95, 355.95 | 22.40 px | 99.0% | 0.05 px |
| 2 | 5/5 | 639.95, 355.95 | 22.40 px | 99.0% | 0.10 px |
| 3 | 5/5 | 639.95, 355.95 | 22.40 px | 99.0% | 0.05 px |
| 4 | 5/5 | 639.95, 355.95 | 22.40 px | 99.0% | 0.05 px |
| 5 | 5/5 | 639.95, 355.95 | 22.40 px | 99.0% | 0.10 px |

The camera portion of `ce4ca303` is acceptable for supervised stationary inspection on this machine. This trial did not run automatic centering or save XY offsets.

Evidence: [G28 result](10-home.txt), [negative camera test](11-camera-negative.txt), and [25-frame positive test](12-camera-positive.txt).

## Cartographer Z trial

### Test setup

The machine normally blocks TKC Z actions with `_TKC_Z_DISABLED`. For this supervised trial only, the two hooks were changed to:

```text
touch_home_gcode: CARTOGRAPHER_TOUCH_HOME
touch_probe_gcode: CARTOGRAPHER_TOUCH_PROBE
```

Klipper was restarted, a normal `G28` completed, Z was raised to 40 mm, active T0 matched detected T0, print state was standby, and every hotend and bed target was zero. The core command was invoked with:

```text
CALIBRATE_TOOL_OFFSETS TOOLS=0,1,2,3,4 CALIBRATE_XY=0 CALIBRATE_Z=1 SAVE_CONFIG=0 DRY_RUN=0 CLEAN_NOZZLE=0
```

### Observed sequence

T0 completed `CARTOGRAPHER_TOUCH_HOME` at `X174.000 Y168.000`. Cartographer reported that Z home was adjusted by `0.335 mm`. TKC established T0 as the zero reference and moved on; this number is a coordinate-origin adjustment, not a measured T0 nozzle offset.

TKC then dropped T0, picked up T1 successfully, moved to the Z station, and started `CARTOGRAPHER_TOUCH_PROBE`. Before T1 returned a measurement, a status query requested the live `tool_calibrator` object. Klippy raised an unhandled exception and shut down. T2 through T4 were never attempted.

No T1 Z result was produced. The only valid result from the interrupted run is that the T0 reference operation executed and was normalized to `0.000 mm` by TKC. It is not sufficient to calculate or validate any per-tool Z offset.

Evidence: [temporary Z enable and preflight](14-z-enable-preflight.txt), [G-code sequence](17-z-gcode-output.txt), and [compact root-cause trace](22-root-cause-trace.txt).

## Confirmed Klippy shutdown defect

The failure is a deterministic TKC Python defect in `klippy/extras/tool_calibrator.py` at upstream commit `ce4ca303`.

`get_status()` executes this branch while a run is active:

```python
rec["elapsed_sec"] = round(time.time() - rec["start_time"], 1)
```

The module does not import `time`. A Mainsail subscription, Moonraker object query, or dashboard poll during any active calibration therefore raises:

```text
NameError: name 'time' is not defined
Transition to shutdown state: Unhandled exception during run
```

`cmd_CALIBRATION_STATUS()` contains the same missing-import path and can trigger the same failure while a run is active. The 107-test suite passed because it does not call either status path with `run_record.state == "RUNNING"` and a populated `start_time`.

This is a release-blocking safety defect because an ordinary read-only UI/API action can shut down the printer during physical probing. No additional Z run was attempted.

Evidence: [upstream source lines](25-upstream-source-defect.txt) and [Klippy trace](22-root-cause-trace.txt).

## Cartographer method limitation on this machine

Cartographer is fixed to the shuttle. The installed Cartographer adapter explicitly treats the probe as contactless, and `CARTOGRAPHER_TOUCH_PROBE` returns the Cartographer probe trigger height. The sensed geometry follows the fixed shuttle-to-bed relationship; changing T0 to T1 does not by itself make the sensor observe the nozzle tip length.

For that reason, a successful TKC Cartographer sequence on this hardware would primarily compare repeated fixed-probe measurements across tool changes. It cannot establish the physical nozzle-to-nozzle Z difference required for tool offsets without an additional nozzle-referenced mechanism or a validated model that couples the tool tip to the measurement. The machine already has a PF2 mechanical calibration switch/Axiscope path intended for nozzle-referenced Z measurements.

The Cartographer backend should remain blocked for production tool Z offsets on this machine. Use Cartographer for shuttle Z home, scan, mesh, and probe repeatability; use a nozzle-contact switch for multi-tool nozzle length.

Evidence: [installed Cartographer touch implementation](26-cartographer-contactless-source.txt) and the machine description in `config/Printer-Setup/calibration-probe.cfg`.

## Recovery and persistence verification

The printer was emergency-stopped as soon as the operator reported the error. TKC service was stopped, the two temporary Z hooks were restored to `_TKC_Z_DISABLED`, and `FIRMWARE_RESTART` cleared the shutdown. The detection input reported physical T1, so a normal `G28` initialized T1 correctly. Z was raised to 40 mm before changing back to T0. The carriage was then parked at the safe center position.

The pre-run and post-run SHA-256 hashes matched exactly:

| File | SHA-256 |
|---|---|
| `Printer-Setup/tool_offsets.cfg` | `9952738361e3150d0742248fb888089cec4b171a9a1f96dfe753666b3ea29a49` |
| `printer.cfg` | `959dfa72d4e981fd8691e092e44d8bf3cc55ce3097c50752aa672e14d9aaede4` |

This proves `SAVE_CONFIG=0` and the interrupted sequence did not change production offsets or the saved printer configuration.

Evidence: [recovery and checksums](18-recovery-stage1.txt), [G28 and Z40 with T1](19-recovery-home-z40.txt), [T0 recovery state](20-final-recovery-state.txt), and [final audit](23-final-audit.txt).

## Defects and proposed improvements

### P0 — Import and harden active-run status reporting

- Import `time` at module scope or use the provided reactor/event time consistently.
- Add tests for `get_status()` and `CALIBRATION_STATUS` while `state=RUNNING`.
- Make every `get_status()` implementation exception-safe; a status read must never terminate Klippy.
- Add a live Moonraker subscription test during XY and Z calibration, because dashboards continuously poll status.

### P0 — Do not advertise fixed-shuttle Cartographer as nozzle Z calibration

- Add an explicit hardware capability such as `measurement_reference: nozzle|shuttle`.
- Reject per-tool Z calibration when the backend only observes a fixed shuttle probe.
- Document that contactless Cartographer results are probe/shuttle measurements unless a nozzle-referenced mechanism is proven.
- Recommend the PF2 switch/Axiscope backend for this printer's tool-tip Z offsets.

### P1 — Fix single-tool Z semantics

`CALIBRATE_TOOL_Z TOOL=1` builds an ordered list containing only T1. It does not first measure the configured reference tool, so `reference_z_result` is empty and T1 is compared with an implicit zero. The command should automatically prepend the reference tool, require a fresh valid reference result, or reject the request.

### P1 — Make failure recovery physically explicit

- Preserve the last confirmed physical tool and probe phase in a crash-safe record.
- On recoverable failures, lift to safe Z and restore the reference tool only after active/detected agreement.
- On Klippy shutdown, report the last confirmed tool and prohibit automatic continuation.
- Default hardware commissioning commands to `SAVE_CONFIG=0`; require a separate explicit apply step.

### P1 — Avoid long monolithic G-code execution

The calibration request held a single synchronous G-code operation for more than 60 seconds, causing Moonraker request timeouts and making status/abort handling fragile. Convert the sequence to scheduled reactor callbacks or a state machine with short steps, and keep the out-of-band abort endpoint independent of the G-code queue.

### P1 — Validate installer paths

Reject control characters, absolute paths, `..`, empty components, and paths that resolve outside the printer config directory. Resolve and print the final canonical target before any mutation.

### P1 — Extend uninstaller ownership coverage

The uninstaller's include regex recognizes `tool_calibrator` but not this machine's hyphenated `tool-calibrator.cfg`, so that include had to be disabled before removal. The script also leaves the source checkout and archived config backups in place. Use the persistent manifest to enumerate the machine integration file, all active includes, generated backups, and optionally the source checkout; verify object and command absence before claiming complete removal.

### P1 — Repair installer rollback execution

The error cleanup uses `tac journal || cat journal | while ...`. On systems where `tac` succeeds, its output is not consumed by the rollback loop, so recorded rollback actions are skipped. Feed either reversed output or the fallback output into the same loop and add a forced-failure integration test.

### P2 — Make installation health reflect the final machine state

The installer reported success while health still said camera `PENDING/OFFLINE`, scale `NOT_SET`, and matrix `NOT_SET`. It also stored that transient string in the persistent manifest. After Klipper reload, verify the `tool_calibrator` object, real snapshot, MPP, matrix, source commit, and running daemon commit; update the manifest with final readiness.

## Final state

- Klipper: `ready`, print state `standby`, XYZ homed.
- Position: `X175.8 Y168.0 Z40.0`.
- Toolchanger: `ready`, T0 active, T0 detected.
- Heaters: T0–T4 and bed targets all `0.0`.
- TKC service: enabled and active, `127.0.0.1:8090`.
- TKC source: clean `main`, exact commit `ce4ca303`.
- Vision health: real camera ready, MPP `0.023`, matrix loaded, session unlocked.
- kTAMV: retained as independent `ktamv-server.service`, port 8086.
- TKC Z hooks: both restored to `_TKC_Z_DISABLED`.
- Production offsets: unchanged.

No upstream TKC code was modified in this work.

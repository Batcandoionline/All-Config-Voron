# Installation and report audit — 2026-09-06

**TKC is installed on the real printer host and loaded by the real Klipper process. It was installed manually for supervised hardware XY trials, rather than by running the upstream installer. The deployment is not a complete reference installation of the published guide.** A Python virtual environment is part of TKC's normal server architecture; its presence does not mean simulated motion.

This audit is read-only with respect to printer configuration, services and motion. It compares the installed revision **b6c332862a87043238b068dd55b5f5ee433efdb6** against that revision's [installation guide](https://github.com/IDcrazy123/Tool-Klipper-Calibration/blob/b6c332862a87043238b068dd55b5f5ee433efdb6/docs/HUONG_DAN_CAI_DAT_VA_CAP_NHAT.md), [installer](https://github.com/IDcrazy123/Tool-Klipper-Calibration/blob/b6c332862a87043238b068dd55b5f5ee433efdb6/scripts/install.sh), [service template](https://github.com/IDcrazy123/Tool-Klipper-Calibration/blob/b6c332862a87043238b068dd55b5f5ee433efdb6/scripts/tool_calibrator.service), [requirements](https://github.com/IDcrazy123/Tool-Klipper-Calibration/blob/b6c332862a87043238b068dd55b5f5ee433efdb6/server/requirements.txt), and [operating procedure](https://github.com/IDcrazy123/Tool-Klipper-Calibration/blob/b6c332862a87043238b068dd55b5f5ee433efdb6/docs/QUY_TRINH_VAN_HANH.md). It does not certify a different or later revision.

## Direct evidence from 192.168.1.43

- Host `voron-local` runs PID **7088** with `/home/voron/tkc-env/bin/python -m server.tool_calibrator_server --host 127.0.0.1 --port 8090 --threads 2 --camera-url http://127.0.0.1:8080/snapshot.jpg`.
- `tool-calibrator-experiment.service` is **active/running and enabled** as a user unit. `Linger=yes` is configured. Boot persistence is configured, but a physical reboot was not performed in this audit.
- The actual Klipper process runs `/home/voron/klipper/klippy/klippy.py` with `/home/voron/printer_data/config/printer.cfg`. That file includes `/home/voron/printer_data/tkc-experiment/tool-calibrator.cfg`.
- Five extras files and the `z_backends` directory resolve through symlinks to `/home/voron/Tool-Klipper-Calibration/klippy/extras/`.
- Moonraker's real `gcode/help` contains `CALIBRATE_TOOL_OFFSETS`, `CALIBRATE_CAMERA_SCALE`, `CALIBRATION_ABORT`, `TKC_STATUS` and `TKC_TEST_XY`. Runtime config contains the actual guarded wrapper, whose G-code calls TKC's native calibration command.
- The real `tool_calibrator` object retains run `run_1788696733`, SUCCESS, completed tools `[0,1,2,3,4]`, and exactly the third-cycle offsets in the report. `/health` reports `b6c3328`, version0.8.18, matrix solved and MPP0.023.

The workstation Python helper only submits HTTP G-code requests and records observations. Real Klipper executes the tool changes and carriage moves; the real vision service processes camera snapshots. The separate dummy-printer tests are explicitly identified below.

Evidence: [installation-audit.json](evidence/installation-audit.json). The read-only collector is [audit_installation.py](audit_installation.py).

## Comparison with the published installation

| Component | Published installer/guide | Installed on this printer | Assessment |
|---|---|---|---|
| Source | Home-directory clone, `main` updater | Same source location, pinned b6c3328 plus typing-import patch | Real source installed; intentionally pinned and locally patched |
| Vision environment | `~/Tool-Klipper-Calibration/env`, plain venv, `pip install -r` | `~/tkc-env`, `--system-site-packages` | Custom environment; not the installer's exact dependency isolation |
| OpenCV | `opencv-python-headless>=4.5.5` Python distribution | Debian `python3-opencv:arm64` 4.6.0+dfsg-12; cv2 4.6.0 | cv2 version exceeds the numeric minimum, but the required pip distribution is absent; build equivalence is not established |
| Other packages | Declared version ranges | Flask3.0.3, Waitress3.0.2, NumPy1.24.2, requests2.28.1, urllib3 1.26.12 | All observed versions fall within the declared ranges |
| Service | System unit `tool_calibrator.service` under `/etc/systemd/system` | User unit `tool-calibrator-experiment.service`; enabled, linger enabled | Functional custom service; upstream service-control commands do not address it |
| Workers/camera | Template passes only port8090; server defaults to 8 workers | Explicit 2 workers and the verified camera snapshot URL | Custom runtime tuning; performance conclusions apply to this setup |
| Klipper extras | File symlinks, including each Z backend file | Same five file modules; whole Z backend directory symlinked | Actual modules available and core loaded; equivalent source resolution for this revision |
| Macro includes | `tool_calibrator_macros.cfg` and `safe_staging_macros.cfg` | Native Python commands plus local `TKC_TEST_XY` and safety/lighting hooks | The upstream convenience macro bundle was not installed |
| User-facing aliases | `CALIBRATE_ALL_TOOLS`, `CALIBRATE_TOOLS_XY`, `CALIBRATE_TOOL_XY`, `CALIBRATE_CAMERA`, `GOTO_CAMERA_TARGET` | Absent from actual `gcode/help` | Do not use the guide's convenience commands on this deployment |
| Saved offsets | Includes generated tool-offset data; supports saving/applying | Isolated station file; not included; no `[tool_offsets]` runtime object configured for application | Measurement only; persistent tool-offset application was not validated |
| Moonraker integration | ASVC entry and `[update_manager tool_calibrator]` | Neither configured | No upstream one-click update/service management integration |
| Supported test scope | Full workflow described in guide | Cold XY, no Z probing, no offset apply, no print test | Hardware trial is narrower than complete XYZ commissioning |

The expected system unit `tool_calibrator.service` reports `LoadState=not-found`. This is consistent with the custom unit name, not evidence that the running TKC instance is absent. Use the following read-only checks for the installed instance:

```sh
systemctl --user status tool-calibrator-experiment.service --no-pager
curl -sS http://127.0.0.1:8090/health
```

## Defects in the guide and installer that affect a fresh install

1. **The installation guide's config example uses obsolete options.** Its `[tool_calibrator]` includes `default_station` and `lift_z_safe`; current code reads `safe_z` and has no corresponding reads for those two keys. The example station uses `camera_url`, `center_x/y`, `matrix_xx/yy/xy/yx`, `z_backend` and `z_switch_pin`, while the current station object reads `target_*`, `approach_*`, `mpp`, `matrix_a/b/c/d/tx/ty` and `safe_z`. The installed Klipper validates unused options and rejects unrecognized names. This is a source/config-validation finding; the invalid block was not loaded into the running printer. Use one maintained schema/example, tested against the installed Klipper parser. [Guide example](https://github.com/IDcrazy123/Tool-Klipper-Calibration/blob/b6c332862a87043238b068dd55b5f5ee433efdb6/docs/HUONG_DAN_CAI_DAT_VA_CAP_NHAT.md#L95).

2. **Tilde includes fail with this Klipper parser.** The guide's `[include ~/Tool-Klipper-Calibration/macros/tool_calibrator_macros.cfg]` is joined literally to the directory of printer.cfg. Calling the installed reader offline reproduced `Include file '/home/voron/printer_data/config/~/Tool-Klipper-Calibration/macros/tool_calibrator_macros.cfg' does not exist`. Use an absolute path or create a correct relative file/symlink. The installer prints `macros/tool_calibrator_macros.cfg` but does not place that macro directory under the printer config folder. Both paths need explicit deployment instructions. [Guide include](https://github.com/IDcrazy123/Tool-Klipper-Calibration/blob/b6c332862a87043238b068dd55b5f5ee433efdb6/docs/HUONG_DAN_CAI_DAT_VA_CAP_NHAT.md#L90).

3. **The documented first-use order predates the removal of fallback centering.** SOP step3 calls `AUTO_TEACH_CAMERA` with its default `AUTO_CENTER=1`, before step5 solves the camera matrix. A fresh b6c3328 installation rejects uncalibrated centering with `ERR_CV_203`. First establish a visible nozzle and safe waypoints using `AUTO_CENTER=0`, then solve scale/orientation and center, then optionally refine teaching. The prior hardware trial cleared the matrix but retained already measured safe waypoints; it did not validate discovery of those waypoints from an empty installation. [SOP](https://github.com/IDcrazy123/Tool-Klipper-Calibration/blob/b6c332862a87043238b068dd55b5f5ee433efdb6/docs/QUY_TRINH_VAN_HANH.md#L72).

4. **The health example and installer health test are weak.** The guide expects `status=healthy`; actual b6c3328 returns `status=ok`. `curl -s ... >/dev/null` in the installer tests neither an HTTP success status nor response identity/version, and the script prints completion even after a warning. Use `curl --fail` plus JSON validation against the expected service and revision; make startup failure stop installation. The separate missing-import bug in b6c3328 must also be fixed. [Installer check](https://github.com/IDcrazy123/Tool-Klipper-Calibration/blob/b6c332862a87043238b068dd55b5f5ee433efdb6/scripts/install.sh#L176).

5. **The installer does not perform all commissioning steps.** It prints macro inclusion and Klipper restart as subsequent actions; it does not copy the macro bundle into the shown relative location or execute a Klipper restart in that section. Documentation should distinguish package deployment, printer configuration, process restart, camera commissioning and offset activation. Its fixed `.bak` backup can overwrite an earlier backup on repeated configuration edits; timestamped non-overwriting backups are required by this printer project.

These findings explain why copying the guide verbatim is not a reliable correction. They are separate from the manually installed instance's successful XY measurements.

## Verification level of the earlier report

| Earlier finding | Evidence actually obtained | What it does not prove |
|---|---|---|
| Native camera scale and 3/3 XY cycles | Real printer motion, real camera, actual Klipper/Moonraker records | Empty-install setup, absolute accuracy, offset application, Z, print quality |
| Abort waits until completion | One real concurrent Moonraker abort request, 156.027 s, plus installed G-code mutex source | A general emergency-stop mechanism or behavior on every Klipper variant |
| Missing imports and 91 tests | Unmodified source fails import in a separate host worktree; patched source passes 91 software tests | A full reference-installer acceptance test or 91 physical measurements |
| Reversed XY compensation toward Z | Source geometry, dummy-printer reproduction and actual KTC sign convention | A physical probe failure; Z was blocked throughout |
| Session cleanup/lock and false scale SUCCESS | Injected offline faults in upstream dummy fixtures | A lock-loss event during the real three cycles |
| 5px burst acceptance | Offline burst reproduction; arithmetic using measured MPP | A 5px noisy burst occurred in the new real cycles |
| `print_stall`, output `BlockingIOError` | Real host log observations during the trial | A proven TKC-specific root cause or behavior with the reference worker count/OpenCV build |

The hardware data remain valid as observations of this exact configuration. Statements about all TKC installations, the official installer, full dependency equivalence or production XYZ readiness would exceed the evidence. The report has been amended to make these boundaries visible near its opening.

## Changes needed before claiming a complete reference installation

Fix and test the upstream import, documentation schema/paths and bootstrap sequence first. Then validate a literal requirements environment, standard service lifecycle, installed convenience macros and Moonraker integration as one deployment. On this printer, preserve the approved Z40 clearance and existing production configuration backups throughout that work. Resolve cancellation and Z-compensation defects before physical XYZ commissioning. A complete install should end with explicit checks for core commands, expected macro aliases, service ownership, dependency versions, persistence and measured axes, rather than a single health ping.

No such reinstall or new motion was performed during this audit. The existing real-printer XY deployment remains in place.

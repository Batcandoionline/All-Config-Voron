# TKC b6c3328 supervised hardware trial

See [REPORT.md](REPORT.md) for measurements, confirmed defects, and development priorities. This directory is an experimental payload; it is not deployed by the production configuration installer.

## Installed revision

- Upstream: `b6c332862a87043238b068dd55b5f5ee433efdb6` (reported version 0.8.18).
- Local correction: [startup-imports.patch](startup-imports.patch), adding `Tuple` and `Optional` imports. The unmodified daemon raises `NameError` at import; it was tested in a separate worktree before changing the live installation.
- Printer: `192.168.1.43`, source `/home/voron/Tool-Klipper-Calibration`, isolated environment `/home/voron/tkc-env`.
- User service: [tool-calibrator-experiment.service](tool-calibrator-experiment.service), bound to `127.0.0.1:8090`, camera `http://127.0.0.1:8080/snapshot.jpg`.
- Live configuration: `/home/voron/printer_data/tkc-experiment/tool-calibrator.cfg`, included from `printer.cfg` immediately before SAVE_CONFIG. The include was already present from the earlier trial.
- Learned camera data: [station-data.cfg](station-data.cfg), read by TKC but not included into `printer.cfg`.
- The Python extras symlinks from the previous trial remain in place. Both vision and the Klipper service process were restarted to load the new source.

No production offset was applied. The wrapper `TKC_TEST_XY` uses cold tools, `CALIBRATE_XY=1 CALIBRATE_Z=0 SAVE_CONFIG=0 DRY_RUN=0 CLEAN_NOZZLE=0 SAMPLES=3 WIGGLE=0`. Z backend hooks still raise an explicit error. The safe tool-change hook verifies homing and active/detected tool agreement and raises the raw carriage to at least Z40 before handing control to the existing KTC dock paths.

## Backup and recovery

Original files and station auto-backup history are preserved in:

- Host: `/home/voron/printer_data/config_backups/pre-tkc-b6c3328-20260906-190126/`.
- Repository: `extras/backups/pre-tkc-b6c3328-20260906-190133/printer/`.

To return to the prior experiment, stop its vision service, restore its backed-up configuration and service files, remove only the tracked startup import modification after verifying the saved patch, select source `780a492bad45399698491a355ab62db6954da9d7`, reload user systemd, and restart the vision and Klipper **processes**. Do not restore production offset files from measured results. A restart clears homing; use the operator-approved G28 and Z40 procedure before motion.

kTAMV has a separate service, environment and port (8086). It was stopped during the measurements to isolate camera/CPU use. Its source, configuration, include and environment were preserved; no demonstrated namespace or port conflict required uninstalling it. Final service state is recorded in the report.

## Reproduction

The following are offline checks and do not control the printer:

```sh
cd /home/voron/Tool-Klipper-Calibration
/home/voron/tkc-env/bin/python -m unittest discover -s tests -v
/home/voron/tkc-env/bin/python /path/to/reproduce_remaining.py /home/voron/Tool-Klipper-Calibration
```

The second script uses upstream dummy printer objects to demonstrate remaining sign, cleanup, lock, success-reporting and dispersion issues. Its observed output is saved in [offline-reproductions.json](evidence/offline-reproductions.json).

Hardware measurements were submitted once per cycle to Moonraker port 7125 with a 240-second client timeout. Five-second read-only state snapshots tracked progress. An intentional abort probe was issued once in the third planned XY cycle; see the report for its actual behavior. Never infer that an HTTP timeout stopped motion, and never use `DRY_RUN=1` as a no-motion check.

The workstation clock was approximately nine seconds ahead of the printer clock during this session. Request/timeline records use workstation time; TKC run records and printer logs use printer time. Compare durations within the same clock and use run IDs to correlate cycles.

Raw system logs are retained locally under `extras/logs/tkc-b6c3328-20260906/`. Selected console messages, states, images, regression output and statistics are versioned here. No automatic update manager was added; an upstream update must preserve or supersede the startup patch deliberately.

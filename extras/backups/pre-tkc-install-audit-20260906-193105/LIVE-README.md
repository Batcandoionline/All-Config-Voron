# TKC supervised experiment on 192.168.1.43

Installed 2026-09-06: b6c332862a87043238b068dd55b5f5ee433efdb6 plus startup-imports.patch (missing Tuple/Optional typing imports).

- Source: /home/voron/Tool-Klipper-Calibration; isolated venv: /home/voron/tkc-env.
- User service: tool-calibrator-experiment.service, loopback 127.0.0.1:8090.
- Configuration: tool-calibrator.cfg; saved station data: station-data.cfg (do not include station data in printer.cfg).
- Native bootstrap MPP 0.023000, target X170.910 Y18.917 Z40.
- TKC_TEST_XY is the supervised cold XY-only wrapper. No offset writes or runtime application; Z probing is guarded.
- Three complete five-tool XY cycles measured; no production offsets changed.
- CALIBRATION_ABORT through Moonraker queues until the cycle finishes. It is not an operational stop control.
- Remaining issues include reversed XY compensation toward the Z station, session cleanup, and camera-scale success reporting.
- kTAMV was temporarily stopped for measurements and restarted. No uninstall was needed.
- Backup: /home/voron/printer_data/config_backups/pre-tkc-b6c3328-20260906-190126/.

Full report and evidence: https://github.com/IDcrazy123/All-Config-Voron/tree/main/extras/experiments/tkc-b6c3328-20260906

Restart the Klipper service process after Python source changes. A soft G-code RESTART can retain cached Python modules. Do not lose the local startup patch during an upstream update; first confirm the fix is present in the new source.

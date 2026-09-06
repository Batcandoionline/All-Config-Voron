# TKC supervised XY trial backup

- Date: 2026-09-06T18:11:34.244387+07:00
- Task: Install pinned TKC 780a492 as an optional live experiment at safe Z=40.
- Production files: local/printer.cfg, local/calibration-probe.cfg; byte-identical live copies in live/.
- Original live tool definitions: live/tools/T0.cfg through T4.cfg.
- Initial experiment draft: initial-experiment-draft.cfg (before coordinate-frame clearance correction).
- Learned station before scale: station-before-scale.cfg.
- Remote recovery directory: `/home/voron/printer_data/config_backups/pre-tkc-hil-20260906-180420`.
- Daily log: extras/Nhat-ky-chinh-sua/2026-09-06-session-updates.md, section 6.

The live printer.cfg receives one absolute include before SAVE_CONFIG. The production Git payload remains unchanged. Restore the exact live/printer.cfg bytes to remove the experiment, stop/disable the user service `tool-calibrator-experiment.service`, and restart the Klipper service. Keep all TKC files and data for recovery; no configuration file deletion is needed.

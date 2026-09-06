# Backup record

- **Date:** 2026-09-06 19:52:59 ICT
- **Task:** Remove the manual TKC trial, verify a clean state, and install the latest upstream revision on the physical printer.
- **Printer backup:** `/home/voron/printer_data/config_backups/tkc-clean-reinstall-20260906-195259/`
- **Related log:** `extras/Nhat-ky-chinh-sua/2026-09-06-session-updates.md`

## Files preserved

- `live/printer.cfg` — live configuration before removing the experimental TKC include.
- `live/moonraker.conf` — live Moonraker configuration before Update Manager integration.
- `live/moonraker.asvc` — live service allowlist before the reinstall.
- `repository/printer.cfg` — repository printer configuration before production TKC includes were added.
- `repository/moonraker.conf` — repository Moonraker configuration before the TKC updater block was added.
- `manual-install/tool-calibrator-experiment.service` — previous user service.
- `manual-install/tkc-experiment/` — previous machine-specific TKC configuration, station data, and generated history.
- `manual-install/source-dirty.patch` — the only source modification from the previous installation.
- `manual-install/source-head.txt` and `manual-install/source-status.txt` — previous revision and worktree state.
- `manual-install/health.json`, `manual-install/moonraker-objects.json`, and `manual-install/service-status.txt` — previous runtime evidence.
- `manual-install/klipper-symlinks.txt` — previous Klipper extras links.

The remote backup also contains the clean-uninstall proof, both official-installer attempts, the isolated-environment test output, intermediate service units, and final deployment evidence. Configuration files removed from active paths were moved into the remote backup rather than deleted.

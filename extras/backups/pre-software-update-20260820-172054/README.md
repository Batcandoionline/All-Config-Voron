# Pre-software-update backup

- Created: 2026-08-20 17:20:54 (Asia/Saigon)
- Printer: `192.168.1.43`
- Purpose: preserve the user toolchanger configuration, KTC-Easy readonly
  configuration snapshot, and tool_crash configuration before updating
  Klipper, klipper-toolchanger-easy, KlipperScreen, and Mainsail.
- Versions before update:
  - Klipper: `v0.13.0-700` (`d6ea62542d3f14a1faf55305c85ed0cbe361a233`)
  - klipper-toolchanger-easy: `v0.0.0-252`
    (`bc2b5c4c466d2f57233ac844371936b290eb4b9a`)
  - KlipperScreen: `v0.4.7-124`
  - Mainsail: `v2.18.0`
- A matching live backup is stored under
  `config/.codex-backups/pre-software-update-20260820-172054/` on the printer.
- Restore user configuration files to their original paths. Readonly files are
  managed by KTC-Easy and should normally be restored by rolling that component
  back through Moonraker rather than editing them in place.

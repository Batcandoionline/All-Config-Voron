# Backup record

- Created: 2026-08-27 09:00:14 +07:00
- Task: apply the clean Cartographer aggregate Z offsets for a controlled
  multi-tool print test.
- Files:
  - `printer.cfg.repo-before`: repository production configuration before the
    live-only test change.
  - `printer.cfg.live-before`: exact live printer configuration before the
    test change.
- Live host backup:
  `/home/voron/printer_data/config_backups/manual-before-clean-cartographer-mean-print-test-20260827-090014/printer.cfg`
- Rollback offsets: T1 `+0.2464`, T2 `-0.2688`, T3 `-0.1896`, T4 `+0.1028 mm`.
- Candidate test offsets: T1 `+0.21217`, T2 `-0.27609`, T3 `-0.18409`,
  T4 `+0.10522 mm`.
- Related journal:
  `extras/Nhat-ky-chinh-sua/2026-08-27-session-updates.md`.

# Retired configuration files — 2026-08-20

These files are preserved for rollback and historical comparison. They are no
longer included by `config/printer.cfg`.

- `calibration.cfg` and `probe-mesh.cfg` were consolidated into
  `config/Printer-Setup/calibration-probe.cfg`.
- `crash_detection_override.cfg` and `tool_crash_cartographer.cfg` were
  consolidated into `config/Printer-Setup/tool-crash.cfg`.

The consolidation preserves production hardware values. Stale PF4/SexBolt
instructions and unused thermal-calibration storage macros were not carried
into the active files.

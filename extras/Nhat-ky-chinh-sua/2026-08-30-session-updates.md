# Session log — 2026-08-30

## Temporary pre-ToolVision Z-offset print-test set

- The operator requested applying the Z-offset values that were active before
  ToolVision was installed for Z measurement.
- Before touching the live configuration, the complete active
  `/home/voron/printer_data/config/printer.cfg` was backed up locally and on
  the printer. Local backup SHA-256:
  `A17B7CCC07FB90934FAFA8A44D45B2E749D8F3DDC21C70B5CEF6325441BAC765`.
- The live file was derived into a candidate and only the generated offsets
  were changed to T1 `+0.228`, T2 `-0.295`, T3 `-0.268`, T4 `-0.014`.
  Unrelated printer settings and ToolVision state were preserved.
- The candidate was installed atomically on `192.168.1.43`, followed by
  `FIRMWARE_RESTART`.
- Verification passed: Klipper `ready`, print state `standby`, ToolVision
  `busy=false` with no last error, and all bed/nozzle heater targets `0 C`.
- The repository production baseline remains the later print-tested set
  (`T1 +0.2464`, `T2 -0.2688`, `T3 -0.1896`, `T4 +0.1028`) until the operator
  reports the result of this temporary print test.
- Backup record:
  `extras/backups/pre-apply-pre-toolvision-offsets-20260830-003000/`.

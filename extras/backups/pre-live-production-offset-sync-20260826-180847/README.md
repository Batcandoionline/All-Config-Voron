# Backup before live production-offset sync

- Created: 2026-08-26 18:08:47 +07:00
- Source: `config/printer.cfg`
- SHA-256: `916c9d8c695b9af1902793e0550ce502b109622786ccc9e57ed1234610806964`
- Scope of the following sync: copy only the four live, print-tested
  `gcode_z_offset` values for T1-T4 into Git. No ToolVision measurement was
  applied and no mesh, PID, Cartographer model or axis-twist data was copied.
- Live values: T1 `+0.2464`, T2 `-0.2688`, T3 `-0.1896`, T4 `+0.1028` mm.

# 2026-05-31 - Multi-tool prime lines

## Summary

- Added `Printer-Setup/prime-lines.cfg`.
- Included it from `printer.cfg`.
- Updated `PRINT_START` to call `PRIME_LINES` instead of the single-tool `_PRIME_LINE`.

## Behavior

- Only tools with slicer-provided `Tn_TEMP` values are primed.
- Non-initial tools are primed first.
- The initial printing tool is primed last and remains mounted for layer 1.
- Prime-line X length clamps to the current bed limits.
- Prime-line Y spacing shrinks automatically if the configured tool count would exceed the bed depth.

## Thermal flow

- T0 stays limited to `PROBE_TEMP` until Cartographer touch-home is complete.
- Non-T0 tools used by the slicer are warmed to up to 170 C during startup.
- `PRIME_LINES` waits each used tool to its slicer first-layer temperature immediately before purging that tool.

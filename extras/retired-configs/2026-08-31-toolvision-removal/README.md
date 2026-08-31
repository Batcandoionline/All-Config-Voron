# Retired ToolVision configuration

`tool-vision.cfg` was removed from the active production include tree on
2026-08-31 when the printer switched to a pinned kTAMV XY method-comparison
integration.

The file is retained byte-for-byte for rollback and historical comparison. It
is not deployed to `~/printer_data/config` and must not be included together
with the active `Printer-Setup/ktamv.cfg`.

The complete pre-removal runtime, generated data, service metadata and printer
state are preserved in the matching dated backup
`pre-replace-toolvision-with-ktamv-20260831-113047`.

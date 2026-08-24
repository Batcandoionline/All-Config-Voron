# ToolVision Z-calibration UX — evidence and implementation status

[English](toolvision-z-calibration-ux-proposal.md) | [Tiếng Việt](toolvision-z-calibration-ux-proposal.vi.md)

## Status on 2026-08-24

This document began as a proposal from a real five-tool printer session. Source
review now confirms that the requested vertical slice is implemented in the
independent ToolVision branch `codex/z-calibration-ux`, commit `2d936f3`
(`feat: make Z runs explicit and preserve history`). It is **not yet deployed
or HIL-validated on this production printer**.

The active All-Config panel still contains the older grouped Setup/Calibrate
flow. Production runtime evidence recorded ToolVision commit `2b3bf2c6`, version
`3.4.0-rc1`. Documentation must keep these two states separate.

## Printer evidence that motivated the change

The production Z offsets have a visually good print result. The two attended
150 °C ToolVision runs on 2026-08-23 were diagnostic and were not applied.
`Difference` below is `measured - production` only for comparison; it is not a
delta to add.

| Tool | Production Z | PF2 Z | PF2 difference | Cartographer Z | Cartographer difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| T0 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 |
| T1 | +0.228 | +0.098 | -0.130 | +0.242 | +0.014 |
| T2 | -0.295 | -0.384 | -0.089 | -0.256 | +0.039 |
| T3 | -0.268 | -0.154 | +0.114 | -0.160 | +0.108 |
| T4 | -0.014 | +0.078 | +0.092 | +0.102 | +0.116 |

- PF2 T0 return drift: `+0.028 mm`.
- Cartographer Touch T0 return drift: `-0.008 mm`.
- An older PF2 record had T1 `+0.092`, T2 `-0.376`, T3 `-0.054`, T4
  `+0.090 mm`; T3 changed most between PF2 observations.
- The Cartographer run replaced the PF2 `results.json`, forcing recovery of the
  first run from console evidence.
- Source calculates Z as `raw_contact_z(tool) - raw_contact_z(reference)`.
  The result is a candidate absolute value relative to T0, not an additive
  correction.

One run per method is insufficient to replace a print-tested baseline,
especially with T3/T4 differences above 0.10 mm. Production offsets remain
unchanged.

## Observed operator problems

1. Setup and routine calibration were grouped together. Teaching a different Z
   mechanism changed the default used by the generic `Z only` button without a
   sufficiently prominent final method label.
2. ToolVision progress, per-tool lines, heater/tool macros and repeated reports
   made the console difficult to scan.
3. A single latest result file lost the immediately preceding method result.
4. “Offset” could be misread as a delta to add to production configuration.

## Source-verified implementation at `2d936f3`

| Requested behavior | Evidence in source/tests | Status |
| --- | --- | --- |
| Explicit method in each Z UI action | UI calls `MODE=Z METHOD=SWITCH` or `METHOD=CARTOGRAPHER_TOUCH` | Implemented on branch |
| Separate routine measurement and setup | Main prompt has method-named measurements; teaching is under Advanced Setup | Implemented on branch |
| Method repeated before motion | Confirmation includes method, reference, tool list, temperature, readiness and report-only text | Implemented on branch |
| Quiet ToolVision progress | `VERBOSITY=QUIET|NORMAL|DEBUG`; `QUIET=1` compatibility alias; UI uses quiet | Implemented on branch |
| Preserve every successful run | Exclusive-create method-labelled JSON, atomic latest file, collision suffix | Implemented on branch |
| Bounded retention | Fixed 20 records; `TOOL_VISION_HISTORY LIMIT=` reads them | Implemented on branch |
| Unambiguous semantics | `applied=false`, `configuration_changed=false`, `NOT APPLIED`, candidate-relative semantics | Implemented on branch |
| Backward compatibility | Generic Z without `METHOD` uses learned default; one-run explicit method does not rewrite it | Implemented on branch |

The relevant runtime files are `tool_vision.cfg`,
`klippy/extras/tool_vision.py` and `tool_vision_state.py`. Regression tests cover
explicit method selection, invalid method/mode combinations, quiet parsing,
maximum ToolVision-owned messages in a fake five-tool heated run, history
collision/retention, method-labelled results and post-restart report/history.

ToolVision's `docs/TESTING.md` records 123 passing tests and 77% overall branch
coverage for this branch, but explicitly classifies the evidence as L0–L2/fake.
Mainsail, simulator and HIL were not run, and the repository was not deployed
to production for this change.

## Remaining limitations

- Quiet mode only reduces messages emitted by ToolVision. It cannot suppress
  Klipper, heater, KTC or other macro output, and warnings/errors stay visible.
- History retention is fixed at 20, not user-configurable.
- Last-two-run comparison, support bundle, run UUID/phase/duration and richer
  raw-sample evidence remain planned.
- Existing ToolVision safety risks remain: synchronous Klippy HTTP, incomplete
  whole-run preflight/recovery evidence and lack of multi-hardware HIL.
- The branch stays report-only and does not apply production offsets.

## Deployment acceptance gate for this printer

Before replacing the current runtime/panel:

1. Create matching backups of All-Config, ToolVision commit, state and result.
2. Confirm the intended feature commit has passed the ToolVision security gate
   and decide how it reaches the Moonraker updater branch; do not point
   production at an arbitrary working branch.
3. Review the custom `result_file` layout. New history should resolve to
   `Generated-Data/ToolVision/tool-vision-history/` and remain deployment-
   protected.
4. Deploy only while idle; verify service/API/Klipper versions without motion.
5. Open Mainsail and verify exactly one visible `TOOL_VISION` macro, Advanced
   Setup separation and method-named confirmation buttons.
6. Run an attended cold or approved-temperature PF2 test, then Cartographer
   Touch only if its model/path are confirmed. Check tool/heater/final state.
7. Confirm two method runs survive as separate history files, latest remains
   compatible, and no production offset/config file changed.
8. Repeat same-method measurements before drawing a calibration conclusion.

Until that gate passes, this is an implemented development feature, not a
production-machine capability.

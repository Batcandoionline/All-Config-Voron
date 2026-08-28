# Change Journal — 2026-08-29

## 1. Recover the interrupted PETG Z check and verify T1/T3/T4 after cleaning T3

### Goal

Recover safely after the power interruption, perform the requested single
attended Cartographer Touch check for T1/T3/T4 at PETG calibration temperature,
and retain production offsets unless the new result is supported by the wider
repeatability history and print evidence.

### Measurement conditions

- Printer was ready/standby before measurement; ToolVision was idle and
  report-only.
- Bed target: `70 C`; selected nozzle target: `150 C`.
- Command:
  `TOOL_VISION_CALIBRATE MODE=Z METHOD=CARTOGRAPHER_TOUCH TOOLS=0,1,3,4 BATCH=1 HOME=1 ASYNC=1 VERBOSITY=QUIET`.
- Every valid tool measurement used Cartographer Touch after full G28 and
  returned to T0 for the reference drift check.
- ToolVision never applied an offset and no production file was changed by the
  measurement.

### Invalid attempt and physical correction

- The first fresh attempt stopped fail-closed at T3 after 10 touches could not
  produce three samples with spread at or below `0.010 mm` inside the latest
  five-touch window.
- ToolVision did not retry automatically and did not loosen the tolerance. T4
  was not reached; the partial T1 value therefore was not accepted as a valid
  session result.
- The operator confirmed flattened plastic on the T3 nozzle and cleaned it.
- Invalid immutable record:
  `/home/voron/printer_data/config/Generated-Data/ToolVision/tool-vision-history/20260828-232205-551-z-cartographer_touch-01.json`.
- Local evidence SHA-256:
  `91C132CC579B81AE0B83776E173673692051DAA1BD15191CD84943BEE192C018`
  under
  `D:/Desktop/All-Config-Voron-main/.local-backups/toolvision-hil-20260829-062205/`.

### Valid attended retry

- Session: `915cb4fc02a4450289cf4a04b86fbf8a`.
- Classification: `COMPLETED_NO_THRESHOLDS`; status `WARNING` only because
  machine-specific comparison thresholds are not configured.
- Result: T1 `+0.18000`, T3 `-0.18400`, T4 `+0.06600` mm.
- T0 reference-return drift: `-0.00200 mm`.
- Persisted record:
  `/home/voron/printer_data/config/Generated-Data/ToolVision/tool-vision-history/20260828-233108-449-z-cartographer_touch-01.json`.
- Local evidence SHA-256:
  `2C7FCE7C14D394468C8D43D209F8E95ACCD2B4FB5C4470758252BEC593762145`
  under
  `D:/Desktop/All-Config-Voron-main/.local-backups/toolvision-hil-20260829-063108/`.

Compared with retained production values, the valid candidates differ by
`-0.03217 mm` for T1, `+0.00009 mm` for T3 and `-0.03922 mm` for T4.

### Combined completed PETG history

| Tool | n | Mean | Median | Range | Sample SD | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| T1 | 9 | +0.19000 | +0.18400 | 0.07200 | 0.02232 | Still regime-dependent; do not replace production from one new sample |
| T3 | 8 | -0.17275 | -0.18000 | 0.05400 | 0.01789 | Clean retry directly supports retained `-0.18409` |
| T4 | 12 | +0.07683 | +0.07700 | 0.02600 | 0.00820 | Repeatable measurement candidate near `+0.077`, but not print-validated |

The supplied `Khoi lap phuong_PETG_33m38s.gcode` never selects T4, so the eight
coupon photos cannot validate a T4 production offset. Retain all production Z
offsets unchanged:

```text
T1 Z=+0.21217
T2 Z=-0.2688
T3 Z=-0.18409
T4 Z=+0.10522
```

### Log review

- Klipper lines 4691–4692 retain the expected fail-closed T3 sampling failure
  before nozzle cleaning.
- The valid session was accepted at line 5024 and its final session/history
  summary appears at lines 5618–5621.
- No ToolVision failure, Klipper shutdown, lost MCU communication or CAN error
  was observed for the valid retry.
- Final MCU, EBB0–4 and Cartographer statistics were all `bus_state=active`
  with `rx_error=0`, `tx_error=0`, `tx_retries=0` and
  `bytes_retransmit=0`.

## 2. Deploy the five-manual-macro ToolVision surface and verify the BTT-sized UI

### Source release and scope

- Source branch: `codex/compact-mainsail-output`.
- Runtime commit: `8cb6809a3de185410cb68199238f0894074cb24c`.
- Documentation follow-up and deployed HEAD:
  `ba424a3dbec5af55d9c0e579a3b3c3fe3e187cdf`.
- Final CI PASS:
  `https://github.com/IDcrazy123/Tool-Vision/actions/runs/33221249321`.
- Source gate reported 234/234 tests, 83% coverage, Jinja validation for 33
  templates and five public macros, plus Ruff, pip-audit, compile, Bash, link,
  diff, Gitleaks and security PASS.
- Core measurement, report-only behavior, state schema and host service were
  unchanged; only the Klipper macro surface and its documentation were
  deployed.

### Backups

- [Repository backup record](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-toolvision-five-manual-macros-20260829-064113/README.md)
- [Exact previous repository config](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-toolvision-five-manual-macros-20260829-064113/tool-vision.cfg)
- Previous config SHA-256:
  `917AD2BC0F8B837EDA97E74F695C99184BAD5AABC46C13FA0577B96D09AB4FFE`.
- Remote backup:
  `/home/voron/printer_data/config_backups/tool-vision/pre-five-manual-macros-20260829-064113/`.
  It contains the previous active config, ToolVision state/results/history,
  pre-deploy metadata and SHA-256 manifest.

### Deployment

- Moonraker updater advanced `/home/voron/Tool-Vision` from
  `b7198e835e59a9b3fa246f5e36790b7393fa4614` to deployed HEAD `ba424a3`.
- The machine-specific `[tool_vision]` section was preserved exactly, including
  PF2, Generated-Data paths and the reviewed `INITIALIZE_TOOLCHANGER` recovery
  hook.
- Only the reviewed macro section was synchronized into
  `/home/voron/printer_data/config/Printer-Setup/tool-vision.cfg`.
- Repository and live config SHA-256 match:
  `051A61E5F52EAB16B840DC221C3AB0C59E8E99391FC1428F37C6350873C41F5B`.
- `FIRMWARE_RESTART` completed and Klipper returned ready.
- ToolVision state/results/history compare byte-for-byte with the pre-deploy
  backup; deployment did not rewrite measurement evidence.

### Public macro surface and live UI HIL

The Mainsail public surface now contains exactly five direct actions:

```text
TOOL_VISION_Z
TOOL_VISION_XY
TOOL_VISION_XYZ
TOOL_VISION_RESULTS
TOOL_VISION_SETUP
```

- The old aggregate `TOOL_VISION` launcher is absent; every helper is private
  with a leading underscore.
- Live Mainsail was exercised at exactly `800x480`, matching the BTT 5-inch
  viewport. Z, Results, Setup, XY and XYZ each exposed a visible content-area
  Close button, and every Close action dismissed its prompt.
- Every dialog remained `800x480` with `scrollWidth=clientWidth=800` and
  `scrollHeight=clientHeight=480`; no prompt-level horizontal or vertical
  scrolling was required.
- Results showed the compact latest-result summary and visible Close action.
- Setup showed Camera XY setup, Sensor setup, Readiness status, Advanced and
  Close in the viewport.
- With camera unavailable, XY and XYZ routed directly to Camera setup and both
  exposed working Close and Back actions.
- No provider, Start measurement or setup action was selected during this UI
  HIL, so it caused no homing, toolchange, heating or measurement.
- The live browser test validates the Mainsail payload and route at BTT-sized
  resolution. One physical tap on the actual BTT touchscreen remains the
  operator check for kiosk cache and touch mapping.

### Final verification and machine state

- Runtime HEAD, active config hash and public macro list: PASS.
- Production offsets remained T1 `+0.21217`, T2 `-0.2688`, T3 `-0.18409`,
  T4 `+0.10522`: PASS.
- ToolVision idle (`busy=false`), report-only and latest valid result retained:
  PASS.
- `INITIALIZE_TOOLCHANGER` restored logical state after restart; T0 is active
  and detected: PASS.
- Printer ready/standby; all five nozzle targets and bed target are `0 C`:
  PASS.

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

## 3. Restore the operator-selected print-tested Z offset set

### Reason and requested values

The operator reported that the GitHub offset set produced a less smooth coupon
than the earlier print-tested set, and that another coupon printed on the
morning of 2026-08-29 was worse than both previously reviewed coupons. The
operator explicitly selected the following earlier set as the production
baseline:

```text
T1 Z=+0.2464
T2 Z=-0.2688
T3 Z=-0.1896
T4 Z=+0.1028
```

These values were independently extracted from the supplied historical
`printer.cfg` text. Its remaining generated mesh and configuration content was
treated as evidence only and was not copied into the repository.

### Pre-change comparison

- Live Klipper already reported exactly the requested four offsets. No live
  offset write was necessary.
- The repository still contained T1 `+0.21217`, T2 `-0.2688`,
  T3 `-0.18409`, T4 `+0.10522`.
- The live file also had unrelated `max_z_velocity=70` and `max_z_accel=900`
  values while the repository retained its reviewed `60` and `700` values.
  Those unrelated live differences were deliberately not synchronized.
- Printer was ready/standby and ToolVision was idle. Bed target remained at the
  operator's current `70 C` setting; no heater, homing, toolchanger or
  measurement command was issued for this offset synchronization.

### Backup and repository change

- [Backup record](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-restore-print-tested-z-offsets-20260829-164546/README.md)
- [Previous repository printer.cfg](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-restore-print-tested-z-offsets-20260829-164546/printer.cfg)
- Previous repository SHA-256:
  `9F09A13D16198F08FF22B75C87CE05DFC8DA4F2CB8FFD958AC881DA2223B94A5`.
- Repository edit was limited to the three differing generated Z lines:
  T1 `+0.21217 -> +0.2464`, T3 `-0.18409 -> -0.1896`, and
  T4 `+0.10522 -> +0.1028`. T2 already matched.
- The repository and live printer now expose the same selected Z offset set.

## 4. Replace the public ToolVision prompt surface with direct console macros

### Source release

- Feature commit:
  `25fe4bec56fbbcb42d127d85e64d565255239f50`.
- ToolVision `main` merge and deployed HEAD:
  `374d5e22db393c74f91706791727771f9413547e`.
- Feature-branch CI PASS:
  `https://github.com/IDcrazy123/Tool-Vision/actions/runs/33246809720`.
- Main-branch CI PASS:
  `https://github.com/IDcrazy123/Tool-Vision/actions/runs/33247017779`.
- The main security gate passed on Python 3.10, 3.11, 3.12 and 3.13,
  including the required security job.
- Source work was performed in the ToolVision project. This repository only
  preserved machine-specific options, synchronized the reviewed macro section,
  deployed it and performed live HIL.

### Public macro contract

Only three macros remain public in Mainsail:

```text
TOOL_VISION_Z
TOOL_VISION_Z_X3
TOOL_VISION_RESULTS
```

- `TOOL_VISION_Z` directly starts Cartographer Touch Z x1 with `HOME=1`,
  `ASYNC=1` and quiet output.
- `TOOL_VISION_Z_X3` directly starts the same report-only measurement as a
  three-attempt batch.
- Both measurement descriptions explicitly state that clicking starts homing
  and motion immediately. They do not show a modal confirmation.
- `TOOL_VISION_RESULTS` directly runs `TOOL_VISION_REPORT` and writes the
  latest summary to the console.
- Public macros contain no `action:prompt_*` payload and do not call a UI
  helper. XY, XYZ, setup and all legacy prompt helpers remain hidden with `_`
  or available only through documented advanced console commands.
- Core report-only behavior, asynchronous fast ACK, print/paused/busy guards,
  cleanup, persisted evidence and the no-apply/no-save contract remain intact.

### Backup and deployment

- [Backup record](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-toolvision-console-only-main-20260829-170842/README.md)
- [Previous macro configuration](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-toolvision-console-only-main-20260829-170842/tool-vision.cfg)
- [Previous live Moonraker configuration](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-toolvision-console-only-main-20260829-170842/moonraker-live.conf)
- Remote backup:
  `/home/voron/printer_data/config_backups/tool-vision/pre-console-only-main-20260829-170842/`;
  it contains 26 files covering the prior macro config, Moonraker config and
  complete ToolVision state/results/history.
- The live Moonraker updater was changed only from
  `primary_branch: codex/compact-mainsail-output` to
  `primary_branch: main`, matching the repository configuration.
- The clean runtime checkout was switched without a reset and fast-forwarded
  to `origin/main`.
- Moonraker now reports branch `main`, local/remote SHA `374d5e2`, valid,
  pristine, zero commits behind, and no warnings or anomalies.
- The machine-specific `[tool_vision]` section remained byte-identical to its
  backup, including PF2, Generated-Data paths and the reviewed toolchanger
  recovery hook.
- The macro section is byte-identical to ToolVision main. Repository/live
  macro config SHA-256:
  `1D399C131B7BC70DACED70184BCD03CCABF8B8E0DF7CC6FA9585AAF1E55868CD`.
- `FIRMWARE_RESTART` completed and Klipper returned ready with no failed
  components or warnings.
- ToolVision state/results/history remained byte-identical to the pre-deploy
  backup.

### Live Mainsail HIL at 800x480

- The macro panel exposed exactly Results, Z x1 and Z x3. The previous Z, XY,
  XYZ, Results and Setup prompt surface was absent.
- `TOOL_VISION_RESULTS` was clicked once. Dialog count remained zero before and
  after the action, while the latest report appeared directly in the Mainsail
  console.
- The console result retained session
  `f04b6f3b3cd84c78afff68f9793f419d`, classification
  `COMPLETED_NO_THRESHOLDS`, and explicitly stated `NOT APPLIED` and
  `Configuration changed: No`.
- Z x1/x3 were intentionally not clicked during UI HIL because the requested
  direct-entry contract starts homing and motion immediately. Their exact
  commands were validated from the loaded config and source contract instead.

### Final state

- Printer ready/standby; ToolVision idle: PASS.
- All nozzle and bed targets `0 C`: PASS.
- No physical tool was mounted or detected after restart, so the toolchanger
  was deliberately left `uninitialized`; no recovery motion was attempted.
- Live and repository production offsets are T1 `+0.2464`, T2 `-0.2688`,
  T3 `-0.1896`, T4 `+0.1028`: PASS.

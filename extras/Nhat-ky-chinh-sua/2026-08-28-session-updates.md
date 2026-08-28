# Change Journal — 2026-08-28

## 1. Validate Cartographer tool Z offsets and retain only repeatable production evidence

### Goal

Re-run five independent Cartographer Touch Z measurements at the same PETG bed
condition used by the earlier coupon, investigate tools that disagree with the
proposed offsets using focused `T0,Tn` batches, and only apply values supported
by repeatable evidence.

### Files changed

- `config/printer.cfg` — synchronized the repository with the retained live
  T1/T3/T4 values; T2 was already `-0.2688` in the repository.
- Live `/home/voron/printer_data/config/printer.cfg` — changed only T2 from
  `-0.27609` to the validated `-0.2688` value.
- `extras/Nhat-ky-chinh-sua/2026-08-28-session-updates.md` — recorded the HIL,
  decision, live deployment and ToolVision UX findings.

### Backup

- [Repository printer.cfg backup](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-validate-cartographer-z-offsets-20260828-165617/printer.cfg)
- [Live printer.cfg backup](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-validate-cartographer-z-offsets-20260828-165617/printer-live.cfg)
- [Backup record](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-validate-cartographer-z-offsets-20260828-165617/README.md)

### Measurement conditions

- Printer: ready/standby and visibly clear through the Mainsail webcam.
- ToolVision: `3.4.0-rc2`, Cartographer Touch ready, report-only mode.
- Command for the five full runs:
  `TOOL_VISION_CALIBRATE MODE=Z METHOD=CARTOGRAPHER_TOUCH HOME=1 VERBOSITY=QUIET`.
- Focused investigation command:
  `TOOL_VISION_CALIBRATE MODE=Z METHOD=CARTOGRAPHER_TOUCH TOOLS=0,n BATCH=3 HOME=1 ASYNC=1 VERBOSITY=QUIET`.
- Bed target: `70 C`; recorded starts/ends remained `69.94..70.12 C`.
- Selected nozzles: `150 C`; each attempt used full G28 and a T0 return check.
- All 14 individual attempts completed with empty cleanup errors. Their WARNING
  classification only reports that `max_reference_z_drift` is not configured.
- Cartographer CAN remained active with `rx_error=0`, `tx_error=0` and
  `tx_retries=0`.
- Klipper evidence: `/home/voron/printer_data/logs/klippy.log`.
- Immutable session records:
  `/home/voron/printer_data/config/Generated-Data/ToolVision/tool-vision-history/`.

### Five full-run results

| Run | T1 | T2 | T3 | T4 | T0 return drift |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | +0.262 | -0.262 | -0.128 | +0.088 | +0.002 |
| 2 | +0.238 | -0.282 | -0.164 | +0.062 | -0.016 |
| 3 | +0.252 | -0.262 | -0.130 | +0.074 | +0.000 |
| 4 | +0.238 | -0.262 | -0.132 | +0.066 | -0.012 |
| 5 | +0.244 | -0.276 | -0.162 | +0.076 | +0.016 |
| **Mean** | **+0.2468** | **-0.2688** | **-0.1432** | **+0.0732** | **-0.0020** |
| **Range** | **0.024** | **0.020** | **0.036** | **0.026** | **0.032** |

Compared with the proposed values `T1 +0.21217`, `T2 -0.2688`,
`T3 -0.1896`, `T4 +0.1028`, only T2 matched without qualification.

### Focused three-attempt batches

| Tool | Attempts | Mean | Median | Range | Assessment |
| --- | --- | ---: | ---: | ---: | --- |
| T1 | +0.224, +0.248, +0.184 | +0.21867 | +0.224 | 0.064 | Near the proposal by mean, but not repeatable |
| T3 | -0.130, -0.076, -0.132 | -0.11267 | -0.130 | 0.056 | Far from proposal and not repeatable |
| T4 | +0.066, +0.082, +0.078 | +0.07533 | +0.078 | 0.016 | Repeatable subset, but far from proposal and not print-tested |

The subset evidence confirms that averaging alone is unsafe for T1/T3. T4 has
a tighter focused cluster but the supplied multicolor coupon never selected T4,
so the `+0.078` measurement remains diagnostic rather than production-ready.

### Applied decision

- T1 remains `+0.21217`: retained from the current live, directly print-tested
  set; conflicting Cartographer regimes require mechanical/contact review.
- T2 changed live from `-0.27609` to `-0.2688`: the five-run mean matched the
  proposal exactly and the earlier coupon print supported it.
- T3 remains `-0.18409`: direct print evidence takes precedence while the new
  Cartographer batches are unstable.
- T4 remains `+0.10522`: no supplied print selected T4, and the new `+0.078`
  measurement candidate requires a dedicated T4 print before use.

Final loaded offsets after `FIRMWARE_RESTART`:

```text
T1 Z=+0.21217
T2 Z=-0.2688
T3 Z=-0.18409
T4 Z=+0.10522
```

### Verification

- Backup created before either configuration was edited: PASS.
- Repository diff limited to the intended T1/T3/T4 source synchronization: PASS.
- Live staging diff limited to T2 `-0.27609 -> -0.2688`: PASS.
- Klipper restarted and returned `ready`: PASS.
- Moonraker `failed_components=[]`, `warnings=[]`: PASS.
- `CHECK_OFFSETS` reported the four final values above: PASS.
- ToolVision online, not busy, and no persisted/runtime error: PASS.
- Heater targets returned to `0 C`: PASS.

### ToolVision prompt UX observations

- The deployed main prompt exposes eight vertically stacked actions even when
  camera setup is unavailable. On a desktop viewport it requires scrolling;
  at `800x480` only the first five actions fit.
- Long XYZ labels overflow or are visually clipped in the desktop dialog.
- Secondary `Back` and `Close` footer actions have very low contrast and fall
  below the fold on the small viewport.
- The confirmation page is structurally better, but `Start measurement` uses
  an error-red style and the footer remains difficult to discover.
- Latest Results is too dense for `800x480`: small wrapped text, hidden footer,
  and a clipped `Console report/history` button.
- The newer source already reduces the main page to five actions, but its
  Z/XYZ provider pages still expose six x1/x3/x5 buttons and the result page
  remains text-heavy. The requested follow-up is progressive disclosure:
  provider first, attempt count second, compact result summary first, and
  diagnostics/details on separate pages. Unavailable camera actions should be
  replaced by one setup action instead of occupying routine calibration space.

### Remaining work

- Investigate Cartographer/contact or tool-seating repeatability for T1 and T3;
  do not tune by averaging the conflicting clusters.
- Print a dedicated T4 transition coupon before considering the focused
  `+0.078` candidate.
- Implement and HIL-test the compact ToolVision prompt hierarchy on both a
  desktop viewport and an `800x480` touch viewport.

## 2. Deploy the compact ToolVision UI, fix the BTT dismiss path, and extend PETG Z evidence

### Scope and backups

- Deployed the reviewed ToolVision progressive-disclosure source through the
  Moonraker updater, then deployed the inline-root-Close follow-up after the
  BTT 5-inch canary showed that the footer dismiss target was not usable.
- Runtime source commit:
  `b7198e835e59a9b3fa246f5e36790b7393fa4614` (`fix: keep BTT close action in prompt content`).
- Remote pre-follow-up backup with a verified SHA-256 manifest:
  `/home/voron/printer_data/config_backups/tool-vision/manual-20260828-182400-btt-inline-close`.
- Local ToolVision source/evidence backup:
  `D:/Desktop/Tool-Vision/.local-backups/pre-btt-inline-close-20260828-181322/`.
- Repository synchronization backup:
  [pre-toolvision-btt-close-sync-20260828-192320](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-toolvision-btt-close-sync-20260828-192320/README.md).
- The exact deployed and synchronized `tool-vision.cfg` SHA-256 is
  `917AD2BC0F8B837EDA97E74F695C99184BAD5AABC46C13FA0577B96D09AB4FFE`.

### UI fix and verification

- Root Close moved from the frontend-owned footer to the first normal content
  button. It still calls the same idempotent `_TOOL_VISION_UI_CLOSE` helper and
  only emits `action:prompt_end`.
- Z/XYZ now select provider, then x1/x3/x5 attempts; results are summary-first
  with separate tool, batch, diagnostic and history pages.
- Source gate: `232/232` tests, 87% branch coverage overall, 83%
  `tool_vision.py`, compile/Ruff/pip-audit/security/diff/link gates PASS.
- Remote CI PASS:
  `https://github.com/IDcrazy123/Tool-Vision/actions/runs/33166923126`.
- Deterministic source fixture passed all nine screens at 800x480 and 1200x800
  without horizontal clipping or fixture scroll.
- Live Mainsail canary was repeated at the actual `window.innerWidth=800` and
  `window.innerHeight=480`: the root rendered Close, Measure Z, Set up camera,
  Latest results and Setup; a click on the centered Close button removed the
  prompt immediately.
- This proves the deployed macro/client round trip at the BTT-sized viewport.
  Physical-touch HIL on the actual BTT panel remains an operator confirmation;
  a stale kiosk page or touch-map error is outside the macro payload.

### G-code and coupon interpretation

- An immutable copy of `Khoi lap phuong_PETG_33m38s.gcode` is retained under
  `D:/Desktop/Tool-Vision/.local-backups/pre-btt-inline-close-20260828-181322/petg-batch-8929051f/`.
- SHA-256:
  `5EBED2F23305CF4C8E249330E2AD8E2E549A29307A75AD89C793D4CB81AAB5D3`.
- OrcaSlicer 2.4.2, 100 layers, 20.04 mm, 0.20 mm normal layer, 0.24 mm first
  layer, 0.4 mm nozzles, four walls, PETG bed 70 C, first tool 230 C and later
  tools 220 C, inactive tools 150 C, outer/inner walls 120/200 mm/s.
- Exact activation order is T0, T1, T2, T3, T0, T1, T0, T2, T0, T3.
  **T4 is never selected**, so the supplied eight photos cannot validate T4.
- The second coupon appears more uniform on the clearest faces, but nearest-seam
  placement, high wall speed, and per-tool flow/pressure-advance differences
  also affect the visible bands. The photos do not isolate Z offset alone.

### Five-attempt PETG batch after deployment

Command:

```text
TOOL_VISION_CALIBRATE MODE=Z METHOD=CARTOGRAPHER_TOUCH TOOLS=0,1,3,4 BATCH=5 HOME=1 ASYNC=1 VERBOSITY=QUIET
```

- Session: `8929051f319e4a6e9019351ae1d16efc`.
- All 5/5 planned attempts completed; bed remained approximately
  `69.95..70.21 C`; selected nozzles were requested at 150 C; every attempt
  used full G28 and a T0 return check.
- Aggregate record:
  `/home/voron/printer_data/config/Generated-Data/ToolVision/tool-vision-history/20260828-115037-491-batch-z-cartographer_touch-01.json`.

| Attempt | T1 | T3 | T4 | T0 return drift |
| --- | ---: | ---: | ---: | ---: |
| 1 | +0.202 | -0.182 | +0.088 | +0.014 |
| 2 | +0.172 | -0.186 | +0.072 | -0.006 |
| 3 | +0.170 | -0.178 | +0.070 | -0.012 |
| 4 | +0.184 | -0.174 | +0.076 | -0.006 |
| 5 | +0.174 | -0.164 | +0.092 | +0.000 |
| **Mean** | **+0.18040** | **-0.17680** | **+0.07960** | **-0.00200** |
| **Median** | **+0.17400** | **-0.17800** | **+0.07600** | **-0.00600** |
| **Range** | **0.03200** | **0.02200** | **0.02200** | **0.02600** |

### Focused T1/T4 PETG cross-check

Because T1 and T4 disagreed materially with the retained configuration, a
separate block was run after the bed re-stabilized at 69.88, 69.89 and 69.88 C:

```text
TOOL_VISION_CALIBRATE MODE=Z METHOD=CARTOGRAPHER_TOUCH TOOLS=0,1,4 BATCH=3 HOME=1 ASYNC=1 VERBOSITY=QUIET
```

- Session: `61f0b44720f74b6f9b4d03e4435510be`; duration 465.95 s.
- All 3/3 attempts completed, no cleanup errors, no ToolVision failure, no
  shutdown, configuration unchanged and `applied=false`.
- Aggregate record:
  `/home/voron/printer_data/config/Generated-Data/ToolVision/tool-vision-history/20260828-120904-598-batch-z-cartographer_touch-01.json`.
- Local immutable copies and hashes:
  `D:/Desktop/Tool-Vision/.local-backups/pre-btt-inline-close-20260828-181322/petg-targeted-61f0b447/`.

| Attempt | T1 | T4 | T0 return drift | Bed start/end C |
| --- | ---: | ---: | ---: | ---: |
| 1 | +0.242 | +0.072 | -0.002 | 69.84 / 70.03 |
| 2 | +0.192 | +0.082 | +0.002 | 70.02 / 69.98 |
| 3 | +0.194 | +0.078 | +0.012 | 70.03 / 70.02 |
| **Mean** | **+0.20933** | **+0.07733** | **+0.00400** | — |
| **Median** | **+0.19400** | **+0.07800** | **+0.00200** | — |
| **Range** | **0.05000** | **0.01000** | **0.01400** | — |

Across the new 5+3 evidence, T1 has median `+0.188`, range `0.072` and sample
SD `0.02352`; it is still regime-dependent and not safe to replace by a single
new sample. T4 has median `+0.077`, range `0.022` and sample SD `0.00800`, a
repeatable measurement candidate that still lacks any T4 print evidence.

### Log review and production decision

- Primary log: `/home/voron/printer_data/logs/klippy.log`.
- Five-attempt session spans lines 35939–38732; focused session spans
  39380–40623.
- Latest CAN evidence for main MCU, EBB0–4 and Cartographer: all
  `bus_state=active`, `rx_error=0`, `tx_error=0`, `tx_retries=0`, and
  `bytes_retransmit=0`.
- One non-fatal console-pipe event occurred at lines 39916–39919:
  `BlockingIOError: [Errno 11] Resource temporarily unavailable` from
  `gcode._respond_raw`. Measurement continued, all three attempts remained
  valid, and there was no shutdown. Track this as console-response backpressure,
  not as a Cartographer measurement failure.
- ToolVision reports `COMPLETED_NO_THRESHOLDS` because machine-specific
  validation limits are not configured; it does not infer or widen limits.
- Retain production offsets unchanged:
  T1 `+0.21217`, T2 `-0.2688`, T3 `-0.18409`, T4 `+0.10522`.
  T2 is repeatable and print-supported; T3 remains close to the new five-run
  cluster and print-supported; T1 remains inconsistent across sessions; T4
  needs a dedicated coupon that actually selects T4 before considering the
  measured `~+0.077..+0.078` candidate.
- Final machine state: standby/ready, T0 active and detected, all nozzle and bed
  targets 0 C, ToolVision report-only, production configuration unchanged by
  both batches.

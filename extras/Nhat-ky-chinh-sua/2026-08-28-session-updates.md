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

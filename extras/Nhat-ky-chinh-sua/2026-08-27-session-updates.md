# Session updates — 2026-08-27

## 1. Direct Cartographer Touch convergence diagnostic for T2

- Operator requested a direct Cartographer touch test to explain intermittent
  T2 convergence failures even though normal printing remains stable.
- No printer configuration, production offset, Cartographer tolerance, sample
  count, or ToolVision source was changed. This session was diagnostic-only.
- Initial state: Klipper ready, print standby, physical T2 mounted/detected.
  `INITIALIZE_TOOLCHANGER` produced `ready/2/2`; full `G28` completed and the
  test point was X174 Y168.
- Live Cartographer was version 1.9.0. The official command used for both
  thermal conditions was:

  ```gcode
  CARTOGRAPHER_TOUCH_ACCURACY SAMPLES=5 SAMPLE_RETRACT_DIST=2 LIFT_SPEED=5
  ```

- Live inner touch filtering remained unchanged: `samples=3`,
  `max_samples=10`, `max_noisy_samples=2` (latest window of five),
  `sample_range=0.010 mm`, retract 2 mm. Saved touch model was threshold 1819,
  speed 2 mm/s, Z offset -0.05 mm.

### Cold test at approximately 28 C

| Outer sample | Raw inner touches (mm) | Accepted three-touch subset (mm) |
| --- | --- | --- |
| 1 | -0.7388, -0.7308, -0.7268, **-0.3168**, -0.7348 | -0.7388, -0.7308, -0.7348 |
| 2 | -0.7368, **-0.4468**, -0.7288, -0.7248, -0.7288 | -0.7288, -0.7248, -0.7288 |
| 3 | -0.7348, -0.7288, -0.7268 | all three |
| 4 | -0.7368, -0.7268, -0.7268 | all three; range exactly 0.0100 |
| 5 | -0.7228, -0.7268, -0.7268 | all three |

- Returned medians: `-0.734804, -0.728804, -0.728804, -0.726804,
  -0.726804 mm`.
- Accuracy result: range `0.008000 mm`, average `-0.729204 mm`, median
  `-0.728804 mm`, population standard deviation `0.002939 mm`.
- Two of 19 raw touches were isolated early-trigger outliers, but all five
  outer samples found a valid three-value cluster.

### PETG probing condition: bed 70 C, T2 150 C

- Heating was stabilized before the command: four consecutive bed samples
  were 70.47, 70.31, 70.23, and 70.20 C; T2 was approximately 150 C.

| Outer sample | Raw inner touches (mm) | Accepted three-touch subset (mm) |
| --- | --- | --- |
| 1 | -0.4928, -0.4868, **-0.2428**, -0.4848 | -0.4928, -0.4868, -0.4848 |
| 2 | -0.4828, -0.4888, -0.4868 | all three |
| 3 | -0.4948, -0.4888, -0.4868 | all three |
| 4 | -0.4868, -0.4868, -0.4888 | all three |
| 5 | **-0.2528**, -0.4908, -0.4868, -0.4868 | -0.4908, -0.4868, -0.4868 |

- Returned medians: `-0.486804, -0.486804, -0.488804, -0.486804,
  -0.486804 mm`.
- Accuracy result: range `0.002000 mm`, average `-0.487204 mm`, median
  `-0.486804 mm`, population standard deviation `0.000800 mm`.
- Two of 17 raw touches were isolated early-trigger outliers. Heating did not
  increase their frequency in this sample, and the accepted hot result was
  tighter than the cold result.

### Assessment

- T2 has a clear and repeatable convergence point under both conditions. The
  intermittent problem is an isolated early trigger outside the main cluster,
  not continuous drift or a permanently incorrect T2 height.
- Every outlier was positive relative to the main cluster and the next touch
  immediately returned to the cluster. This pattern prioritizes inspection of
  transient nozzle/contact contamination or ooze, intermittent tool
  seating/compliance, and Cartographer early-trigger response. It does not
  support a CAN/HTTP transport cause: the CAN bus stayed active, counters did
  not increase beyond the boot baseline, and `tx_retries=0`.
- The hot and cold accepted centers differ by approximately `+0.2420 mm`.
  Absolute Cartographer touch coordinates therefore must only be compared at
  matched thermal conditions. `CARTOGRAPHER_TOUCH_ACCURACY` values are not
  candidate production tool offsets and were not applied.
- Cartographer's current filter is operating as implemented: within the latest
  five raw touches it chooses the three-value combination with the smallest
  range and accepts it only when the range is at most 0.010 mm. This explains
  why direct/manual sessions can pass despite isolated outliers, while a
  session becomes `INVALID` when no three-value cluster appears within ten
  touches. The evidence does not justify changing this core logic, widening
  tolerance, or adding an automatic retry.
- The raw evidence and conclusions were sent to the ToolVision task
  `01a02382-e5a5-7c93-952f-f01783f6cd55` for diagnostics/UI follow-up only.
- Final state: `TURN_OFF_HEATERS` executed; Klipper ready, print standby,
  homed XYZ, T2 still mounted and detected as `ready/2/2`, Z lifted to about
  15 mm, bed and T2 heater targets zero.

## 2. Five additional ToolVision Cartographer Z runs

- Ran exactly five new report-only attempts on live ToolVision `3.4.0-rc2`.
  Each invocation used the same backend command with a full home:

  ```gcode
  TOOL_VISION_CALIBRATE MODE=Z METHOD=CARTOGRAPHER_TOUCH HOME=1 VERBOSITY=QUIET
  ```

- Preflight passed: Klipper ready, print standby, KTC `ready/2/2`, CAN active,
  Cartographer ready, and stepper X `DRV_STATUS 80190000 cs_actual=25 stst=1`
  without `ShortToSupply`. The bed was stabilized at 70 C with four consecutive
  samples `70.22, 70.25, 70.26, 70.28 C`. Each selected nozzle was waited at
  150 C by ToolVision.

| Attempt | Status | T1 | T2 | T3 | T4 | T0 drift | Duration | History |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | WARNING | +0.168 | -0.288 | -0.172 | +0.112 | +0.010 | 290.930 s | `20260827-003840-964-z-cartographer_touch-01.json` |
| 2 | WARNING | +0.158 | -0.294 | -0.188 | +0.088 | -0.024 | 270.113 s | `20260827-004341-450-z-cartographer_touch-01.json` |
| 3 | WARNING | +0.162 | -0.296 | -0.194 | +0.090 | -0.014 | 262.616 s | `20260827-004832-323-z-cartographer_touch-01.json` |
| 4 | WARNING | +0.170 | -0.288 | -0.192 | +0.076 | -0.018 | 278.328 s | `20260827-005336-052-z-cartographer_touch-01.json` |
| 5 | WARNING | +0.168 | -0.284 | -0.182 | +0.102 | +0.000 | 280.142 s | `20260827-010004-071-z-cartographer_touch-01.json` |

- All five sessions completed without `INVALID`. `WARNING` is expected because
  `max_reference_z_drift` is not configured. Every history records
  `applied=false`, `configuration_changed=false`, `HOME=1`, bed
  `69.96..70.20 C`, and nozzle request 150 C. Mean duration was 276.426 s.

| Tool | Mean | Median | Range | Sample SD | Production | Mean - production |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T1 | +0.1652 | +0.168 | 0.012 | 0.00502 | +0.2464 | -0.0812 |
| T2 | -0.2900 | -0.288 | 0.012 | 0.00490 | -0.2688 | -0.0212 |
| T3 | -0.1856 | -0.188 | 0.022 | 0.00888 | -0.1896 | +0.0040 |
| T4 | +0.0936 | +0.090 | 0.036 | 0.01381 | +0.1028 | -0.0092 |
| T0 drift | -0.0092 | -0.014 | 0.034 | 0.01390 | 0.0000 | -0.0092 |

### Raw T2 convergence evidence

| Attempt | Raw touches | Accepted subset | Touches | Full spread |
| --- | --- | --- | ---: | ---: |
| 1 | -0.3016, +0.0604, -0.2996, -0.2636, -0.2536, -0.2996, -0.3056 | -0.2996, -0.2996, -0.3056 | 7 | 0.366 |
| 2 | -0.3422, -0.3302, -0.3302, -0.0202, -0.3282 | -0.3302, -0.3302, -0.3282 | 5 | 0.322 |
| 3 | -0.3587, -0.3587, -0.3527 | all three | 3 | 0.006 |
| 4 | -0.2056, -0.3796, -0.3696, -0.3396, -0.3596, -0.3596 | -0.3696, -0.3596, -0.3596 | 6 | 0.174 |
| 5 | -0.3455, -0.3695, -0.3715, -0.2555, -0.3695 | -0.3695, -0.3715, -0.3695 | 5 | 0.116 |

- T2 still needed filtering in four of five attempts despite all sessions
  completing. The accepted relative results were repeatable (`0.012 mm` range),
  but the raw full spread confirms intermittent early-trigger/multi-cluster
  behavior remains. This matches the direct provider test and earlier manual
  runs; it does not justify widening the 0.010 mm limit or adding auto-retry.
- T3 also required more than three raw touches in four of five attempts, but
  its final mean is now only `+0.0040 mm` from production after cleaning. T1
  remains a large discontinuity from production (`-0.0812 mm`). T4 has the
  largest final batch range (`0.036 mm`). No new mean or median should be
  applied without an A/B print and a resolved T1 baseline.
- CAN remained active with `tx_retries=0`. After the batch,
  `TURN_OFF_HEATERS` and a safe Z lift were executed. Final state: Klipper
  ready, print standby, homed XYZ, T2 restored/detected `ready/2/2`, Z about
  15 mm, and every heater target/power zero.
- Results and raw T2 sequences were sent to ToolVision task
  `01a02382-e5a5-7c93-952f-f01783f6cd55` for documentation only; no measurement
  logic change was requested.

## 3. BTT KlipperScreen prompt could not be closed

- Operator reported that the ToolVision selection/result dialog on the BTT
  5-inch screen could not be dismissed with X or Close.
- Live versions during diagnosis were ToolVision `3.4.0-rc2` and KlipperScreen
  `v0.4.7-158-g686d106` at 800x480. Only one live
  `Printer-Setup/tool-vision.cfg` existed.
- Controlled reproduction proved the close macro itself is valid: `TOOL_VISION`
  opened the dialog at `07:31:20`; `_TOOL_VISION_UI_CLOSE` reached Klipper at
  `07:31:22`; KlipperScreen decoded `prompt_end` and immediately logged
  `remove_dialog`.
- KlipperScreen source shows both its native X button and ToolVision footer
  buttons must send a `printer.gcode.script` request and wait for the
  `action:prompt_end` response. The old ToolVision flow closed the confirmation
  dialog and then opened `_TOOL_VISION_UI_JOB` immediately before the long,
  synchronous calibration callback. A later Close request could therefore sit
  behind the running G-code job and appear frozen; terminal results could also
  reopen a modal prompt.
- The ToolVision task implemented a source-only fix in commit
  `e38bd4d51bfd94b5cad47cc086f389551e37350a`: Start now closes confirmation and
  does not auto-open job/results; `_TOOL_VISION_UI_JOB` is non-modal in all
  states; Close remains UI-only and never cancels calibration. Security Gate
  and all 231 tests passed.
- The fix was deliberately not deployed during the five-run batch, preserving
  one live version and comparable conditions. The printer still runs
  `3.4.0-rc2`. A later idle canary must update via Moonraker, restart Klipper
  for macro changes, and verify static open/close, Start closing before G28,
  no modal during the job, and explicit Latest results on both Mainsail and BTT.

## 4. Consolidated non-INVALID Cartographer Z reference

- Read-only parsing of the retained Klipper logs from 2026-08-24 through
  2026-08-27 recovered 35 unique Cartographer result blocks that reached the
  terminal `WARNING` result with complete T0-T4 values and a history filename.
  The `WARNING` label is caused by the unconfigured
  `max_reference_z_drift`; these are provider-complete sessions, not
  production-approved offsets.
- The live history directory currently retains only the latest 20 files, so
  older rows below were reconstructed from immutable Klipper log result blocks
  and cross-checked against the committed 24-26 August journals.
- Classification:
  - A: provider-complete, but outside the final controlled clean series on
    24 August; kept only as historical evidence.
  - B: final controlled series on 24 August after the operator resolved T3
    ooze/cleanliness.
  - C: three-run pilot on 25 August before the dedicated 70 C PETG batch.
  - D: provider-complete, but no fresh G28 was issued because of the PowerShell
    `$home` variable collision; excluded from controlled statistics.
  - E: five-run PETG 70 C baseline on 25 August; this is the set that was
    averaged into the print-tested production values.
  - F: procedure-complete on 26 August, but later physical inspection found a
    flattened plastic remnant on T3; retained in history and excluded from the
    clean subset.
  - G: two complete runs after T3 cleaning and a machine power reset.
  - H: five manual runs after the full host reboot.
  - I: latest five-run batch on 27 August.

| Local time (+07) | Class | T1 | T2 | T3 | T4 | T0 drift | History |
| --- | :---: | ---: | ---: | ---: | ---: | ---: | --- |
| 24/08 21:17:31 | A | +0.210 | -0.294 | -0.232 | +0.062 | -0.030 | `20260824-141731-041-z-cartographer_touch-01.json` |
| 24/08 21:46:28 | B | +0.256 | -0.282 | -0.172 | +0.116 | +0.010 | `20260824-144628-534-z-cartographer_touch-01.json` |
| 24/08 21:51:42 | B | +0.248 | -0.268 | -0.180 | +0.106 | +0.014 | `20260824-145142-725-z-cartographer_touch-01.json` |
| 24/08 21:56:48 | B | +0.240 | -0.262 | -0.188 | +0.124 | -0.002 | `20260824-145648-209-z-cartographer_touch-01.json` |
| 25/08 16:17:29 | C | +0.238 | -0.270 | -0.184 | +0.104 | +0.000 | `20260825-091729-285-z-cartographer_touch-01.json` |
| 25/08 16:52:00 | C | +0.248 | -0.266 | -0.196 | +0.102 | +0.014 | `20260825-095200-233-z-cartographer_touch-01.json` |
| 25/08 16:56:39 | C | +0.242 | -0.268 | -0.178 | +0.108 | +0.018 | `20260825-095639-268-z-cartographer_touch-01.json` |
| 25/08 20:18:29 | E | +0.236 | -0.268 | -0.188 | +0.108 | +0.016 | `20260825-131829-509-z-cartographer_touch-01.json` |
| 25/08 20:22:48 | E | +0.242 | -0.280 | -0.194 | +0.106 | +0.002 | `20260825-132248-757-z-cartographer_touch-01.json` |
| 25/08 20:26:49 | D | +0.230 | -0.282 | -0.196 | +0.104 | +0.006 | `20260825-132649-786-z-cartographer_touch-01.json` |
| 25/08 20:30:58 | E | +0.252 | -0.266 | -0.194 | +0.090 | +0.000 | `20260825-133058-681-z-cartographer_touch-01.json` |
| 25/08 20:35:15 | E | +0.242 | -0.276 | -0.188 | +0.110 | +0.006 | `20260825-133515-148-z-cartographer_touch-01.json` |
| 25/08 20:39:44 | E | +0.260 | -0.254 | -0.184 | +0.100 | +0.020 | `20260825-133944-202-z-cartographer_touch-01.json` |
| 26/08 17:31:27 | F | +0.246 | -0.270 | -0.140 | +0.114 | +0.002 | `20260826-103127-777-z-cartographer_touch-01.json` |
| 26/08 17:36:21 | F | +0.244 | -0.270 | -0.148 | +0.102 | -0.002 | `20260826-103621-562-z-cartographer_touch-01.json` |
| 26/08 17:49:48 | F | +0.240 | -0.262 | -0.126 | +0.108 | +0.004 | `20260826-104948-744-z-cartographer_touch-01.json` |
| 26/08 17:54:31 | F | +0.264 | -0.272 | -0.120 | +0.118 | +0.014 | `20260826-105431-421-z-cartographer_touch-01.json` |
| 26/08 19:10:18 | F | +0.258 | -0.268 | -0.118 | +0.120 | +0.004 | `20260826-121018-449-z-cartographer_touch-01.json` |
| 26/08 19:20:23 | F | +0.272 | -0.264 | -0.102 | +0.128 | +0.020 | `20260826-122023-520-z-cartographer_touch-01.json` |
| 26/08 19:24:33 | F | +0.246 | -0.280 | -0.118 | +0.114 | +0.000 | `20260826-122433-553-z-cartographer_touch-01.json` |
| 26/08 19:28:33 | F | +0.250 | -0.288 | -0.128 | +0.120 | +0.000 | `20260826-122833-740-z-cartographer_touch-01.json` |
| 26/08 19:32:59 | F | +0.256 | -0.268 | -0.108 | +0.132 | +0.010 | `20260826-123259-936-z-cartographer_touch-01.json` |
| 26/08 19:37:23 | F | +0.248 | -0.268 | -0.136 | +0.118 | -0.006 | `20260826-123723-967-z-cartographer_touch-01.json` |
| 26/08 20:16:52 | G | +0.250 | -0.266 | -0.164 | +0.120 | +0.008 | `20260826-131652-546-z-cartographer_touch-01.json` |
| 26/08 20:21:17 | G | +0.238 | -0.276 | -0.190 | +0.106 | -0.008 | `20260826-132117-268-z-cartographer_touch-01.json` |
| 26/08 20:34:58 | H | +0.176 | -0.276 | -0.178 | +0.128 | +0.016 | `20260826-133458-106-z-cartographer_touch-01.json` |
| 26/08 20:39:54 | H | +0.170 | -0.282 | -0.186 | +0.108 | +0.002 | `20260826-133954-656-z-cartographer_touch-01.json` |
| 26/08 20:45:26 | H | +0.178 | -0.268 | -0.180 | +0.106 | +0.000 | `20260826-134526-955-z-cartographer_touch-01.json` |
| 26/08 20:50:25 | H | +0.168 | -0.278 | -0.182 | +0.106 | +0.004 | `20260826-135025-985-z-cartographer_touch-01.json` |
| 26/08 20:54:51 | H | +0.170 | -0.294 | -0.180 | +0.104 | +0.016 | `20260826-135451-252-z-cartographer_touch-01.json` |
| 27/08 07:38:40 | I | +0.168 | -0.288 | -0.172 | +0.112 | +0.010 | `20260827-003840-964-z-cartographer_touch-01.json` |
| 27/08 07:43:41 | I | +0.158 | -0.294 | -0.188 | +0.088 | -0.024 | `20260827-004341-450-z-cartographer_touch-01.json` |
| 27/08 07:48:32 | I | +0.162 | -0.296 | -0.194 | +0.090 | -0.014 | `20260827-004832-323-z-cartographer_touch-01.json` |
| 27/08 07:53:36 | I | +0.170 | -0.288 | -0.192 | +0.076 | -0.018 | `20260827-005336-052-z-cartographer_touch-01.json` |
| 27/08 08:00:04 | I | +0.168 | -0.284 | -0.182 | +0.102 | +0.000 | `20260827-010004-071-z-cartographer_touch-01.json` |

### Batch means

| Class | N | T1 mean | T2 mean | T3 mean | T4 mean | Drift mean | Use |
| :---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| A | 1 | +0.2100 | -0.2940 | -0.2320 | +0.0620 | -0.0300 | Historical only; condition not locked |
| B | 3 | +0.2480 | -0.27067 | -0.1800 | +0.11533 | +0.00733 | Controlled clean reference |
| C | 3 | +0.24267 | -0.2680 | -0.1860 | +0.10467 | +0.01067 | Pilot reference only |
| D | 1 | +0.2300 | -0.2820 | -0.1960 | +0.1040 | +0.0060 | Exclude: no fresh G28 |
| E | 5 | +0.2464 | -0.2688 | -0.1896 | +0.1028 | +0.0088 | Print-tested production baseline |
| F | 10 | +0.2524 | -0.2710 | -0.1244 | +0.1174 | +0.0046 | Exclude from clean baseline: T3 plastic |
| G | 2 | +0.2440 | -0.2710 | -0.1770 | +0.1130 | +0.0000 | Post-clean evidence; N too small |
| H | 5 | +0.1724 | -0.2796 | -0.1812 | +0.1104 | +0.0076 | Clean, but T1 discontinuity |
| I | 5 | +0.1652 | -0.2900 | -0.1856 | +0.0936 | -0.0092 | Clean/latest; T1 remains discontinuous |

### Aggregate statistics

| Population | N | Tool | Mean | Median | Range | Sample SD |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| All provider-complete rows | 35 | T1 | +0.22411 | +0.242 | 0.114 | 0.03705 |
| All provider-complete rows | 35 | T2 | -0.27531 | -0.272 | 0.042 | 0.01069 |
| All provider-complete rows | 35 | T3 | -0.16874 | -0.180 | 0.130 | 0.03119 |
| All provider-complete rows | 35 | T4 | +0.10743 | +0.108 | 0.070 | 0.01418 |
| All provider-complete rows | 35 | T0 drift | +0.00320 | +0.004 | 0.050 | 0.01178 |
| Controlled rows, excluding A and D | 33 | T1 | +0.22436 | +0.242 | 0.114 | 0.03809 |
| Controlled rows, excluding A and D | 33 | T2 | -0.27455 | -0.270 | 0.042 | 0.01042 |
| Controlled rows, excluding A and D | 33 | T3 | -0.16600 | -0.180 | 0.094 | 0.02962 |
| Controlled rows, excluding A and D | 33 | T4 | +0.10891 | +0.108 | 0.056 | 0.01210 |
| Controlled rows, excluding A and D | 33 | T0 drift | +0.00412 | +0.004 | 0.044 | 0.01058 |
| Clean subset, excluding A/D/F | 23 | T1 | +0.21217 | +0.238 | 0.102 | 0.03946 |
| Clean subset, excluding A/D/F | 23 | T2 | -0.27609 | -0.276 | 0.042 | 0.01121 |
| Clean subset, excluding A/D/F | 23 | T3 | -0.18409 | -0.184 | 0.032 | 0.00806 |
| Clean subset, excluding A/D/F | 23 | T4 | +0.10522 | +0.106 | 0.052 | 0.01161 |
| Clean subset, excluding A/D/F | 23 | T0 drift | +0.00391 | +0.004 | 0.044 | 0.01172 |

- The 35-row and 23-row cross-session means are descriptive only. They mix
  different machine/reboot/thermal regimes, and T1 clearly changes regime from
  about `+0.24..+0.25 mm` to `+0.16..+0.18 mm`. Averaging those regimes does
  not create a safe candidate offset.
- The only print-tested reference remains class E:
  `T1 +0.2464, T2 -0.2688, T3 -0.1896, T4 +0.1028 mm`. Class I confirms T3
  closely but does not confirm T1. No configuration was changed or applied by
  this consolidation.

## 5. Áp mean sạch Cartographer cho bản in A/B

### Mục tiêu

- Người vận hành chọn mean của 23 lượt không ghi nhận nhiễm bẩn để in thử:
  T1 `+0.21217`, T2 `-0.27609`, T3 `-0.18409`, T4 `+0.10522 mm`.
- File so sánh đúng là `Khoi lap phuong_PETG_33m38s.gcode`; chưa coi các giá trị
  này là production-approved trước khi đánh giá vật thể hoàn tất.

### Baseline và backup

- Baseline live/repository trước thử nghiệm: T1 `+0.2464`, T2 `-0.2688`,
  T3 `-0.1896`, T4 `+0.1028 mm`.
- Backup local:
  `extras/backups/pre-clean-cartographer-mean-print-test-20260827-090014/`.
- Backup live:
  `/home/voron/printer_data/config_backups/manual-before-clean-cartographer-mean-print-test-20260827-090014/printer.cfg`.
- SHA-256 của `printer.cfg` repo/live trước thay đổi cùng là
  `e72de505f9521983d5c4b530526d76b7ee74440eff5a34cbed67179124890538`.

### Áp dụng và xác minh

- Lần đầu dùng `SET_TOOL_PARAMETER` để thử runtime, nhưng một Klipper restart
  trước lần khởi chạy thủ công làm các object tool trở lại baseline cũ.
- Bản `Khoi lap phuong_PETG_33m38s.gcode` khởi chạy thủ công sau restart vì vậy
  không phải phép thử candidate. Đã hủy khi chưa vào vật thể; chỉ còn prime line,
  `display_status` báo `Print canceled`, filament counter `148.96 mm`.
- Sau khi backup, dùng `SET_TOOL_PARAMETER`, `SAVE_TOOL_PARAMETER` cho T1-T4 và
  `SAVE_CONFIG`. Live `printer.cfg` sau restart chứa chính xác:
  - T1 `gcode_z_offset = 0.21217`;
  - T2 `gcode_z_offset = -0.27609`;
  - T3 `gcode_z_offset = -0.18409`;
  - T4 `gcode_z_offset = 0.10522`.
- SHA-256 live mới:
  `718d227924eaaf6b1d5b2d2a6a033f3a375cd7d7bad0b23ca0c7fed5e6da1436`.
- `INITIALIZE_TOOLCHANGER` khôi phục KTC `ready/0/0`; Klipper ready, print
  standby và mọi heater target/power bằng 0.
- `config/printer.cfg` trong Git vẫn giữ baseline đã in kiểm chứng; candidate chỉ
  được ghi live để thực hiện A/B. Không đồng bộ candidate vào production repo
  trước kết quả bản in.

### Trạng thái chờ

- Người vận hành đã dọn prime line; đã chạy lại đúng file
  `Khoi lap phuong_PETG_33m38s.gcode` với candidate live.
- Moonraker history job `000270` xác nhận `completed`, 100 lớp, cao 20.04 mm,
  print duration 2130.07 s, total duration 2395.87 s, filament 2087.26 mm;
  không có shutdown/pause/error trong job. Job trước `00026F` là lần hủy
  prime-line và không được dùng để đánh giá.
- Ảnh bốn mặt do người vận hành cung cấp cho thấy bản candidate có bám lớp và
  thành đều, các dải màu/đường lớp liên tục; ranh giới T1 (xanh) và T2 (đen)
  không có khe hoặc bậc lớn. Vẫn thấy nhẹ seam/độ bóng không đều trên một số
  dải đỏ và xanh, nhưng không đủ bằng chứng để quy cho Z offset riêng lẻ.
- So với bộ bốn ảnh baseline, candidate tương đương hoặc sạch hơn nhẹ ở
  ranh giới dải và không còn hạt trắng rõ trên dải đen; khác biệt ánh sáng,
  góc chụp và hướng xoay làm so sánh định lượng không hợp lệ. Kết luận ngoại
  quan: candidate đạt để tiếp tục A/B, chưa phải phê duyệt production.
- G-code này thực tế chỉ gọi `T0`, `T1`, `T2`, `T3` (không có `T4`); vì vậy
  phép in không xác minh offset T4 `+0.10522 mm` dù giá trị vẫn đang lưu live.
- Chưa thay đổi `config/printer.cfg` trong Git; giữ baseline làm đường rollback.
  Cần người vận hành quyết định giữ candidate sau khi kiểm tra trực tiếp độ
  phẳng đáy, độ bám và kích thước nếu muốn cập nhật production.

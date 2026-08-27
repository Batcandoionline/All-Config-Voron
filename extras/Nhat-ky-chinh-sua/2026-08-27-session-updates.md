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

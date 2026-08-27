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

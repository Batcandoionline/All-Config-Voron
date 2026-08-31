# ToolVision proposal: repeated XY measurement within one pickup

## Review basis

This proposal is based on the retired ToolVision Git bundle at commit `374d5e2`
(`main`, 2026-08-29) and the 2026-08-31 live kTAMV measurement. It is a design
for the separate ToolVision repository only; ToolVision was not reinstalled.

The current source already supports multiple full attempts and takes a median
across valid attempts, but `_measure_xy()` centers only once per tool in each
attempt. Its candidate is the relative centered position against T0 and the
production path remains report-only.

## Proposed changes

1. Add `xy_samples_per_tool`, default `3`, and
   `max_xy_sample_spread_mm`, default `0.12`.
2. In `_measure_xy()`, call `_move_to_station("camera", tool_number)` before
   **every** sample. Re-centering from an already centered position makes
   samples two and three misleading zeros.
3. Persist every raw center position, station/reference residual and detector
   evidence. Compute per-axis mean/min/max/range and fail closed on missing
   samples or excessive range.
4. Report `mean_residual_xy`, the starting `configured_xy`, and
   `candidate_xy = configured_xy + mean_residual_xy`, plus raw samples/spread.
5. Keep the median across full attempts/pickup cycles as an outer statistic.
   The three-sample mean measures detection/centering repeatability within one
   pickup; the median of at least three pickup means measures dock repeatability.
6. Turn the existing T0 reference-return evidence into a configurable gate.
   This machine observed up to `Y+0.072 mm`; classify excessive return drift as
   `REVIEW_PICKUP_REPEATABILITY`.
7. Add a pre-camera lighting hook. This machine disables only `Tn_LED`; the
   independent 5% WCMCU WS2812B/ESP32-C3 ring must not be assumed controllable.
8. If apply support is added, keep a separate
   `TOOL_VISION_APPLY_LAST_XY` command. Require matching active/detected tool,
   unchanged fingerprint/config snapshot, PASS status, non-T0 tool, accepted
   spread/drift and explicit operator confirmation. Stage with
   `SET_TOOL_PARAMETER`/`SAVE_TOOL_PARAMETER`; require a separate reviewed
   `SAVE_CONFIG`. Never auto-apply at batch completion.

## Source locations

- `klippy/extras/tool_vision.py`: `_measure_xy()`, reference-return,
  batch aggregation, production comparison and status/report.
- `klippy/extras/tool_vision_state.py`: raw samples, residual/candidate,
  within-pickup spread and between-pickup statistics schema.
- `tool_vision.cfg`: sampling/spread options, lighting hook and apply guard.
- Logic, integration, result and contract tests: station reset per sample, sign
  convention, unchanged Z, tool mismatch, stale fingerprint, spread/drift
  failure and proof that measurement never applies implicitly.

## Proposed HIL acceptance

- Camera at Z40, zero-XY T0 reference, heater targets zero and tool LEDs off.
- Three complete samples per T1–T4; per-axis spread at most `0.12 mm`.
- At least three pickup cycles per tool, with pickup means and their median kept
  separately.
- T0 return drift within a declared threshold; otherwise report only.
- A report-only verification after trial application returns near zero at the
  camera resolution, while every Z offset remains byte-for-byte unchanged.

## Lessons from the kTAMV run

- Calibration filtering must not mutate caller input before retained-count
  validation, and MPP/space/camera rows must be removed together.
- Result APIs need raw samples, mean, spread and tool identity so a macro cannot
  consume stale evidence.
- Stability within one pickup does not prove dock repeatability. T0 return drift
  must gate any production-ready classification.

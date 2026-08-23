# ToolVision Z Calibration UX and Console Noise Proposal

## Purpose

This proposal is based on a real five-tool Voron 2.4 hardware-in-the-loop
session on 2026-08-23. It asks ToolVision to make Z calibration safer to
understand, easier to operate from Mainsail, and quieter in the console without
weakening the existing report-only safety model.

The printer's current production Z offsets have already produced a visually
good first layer. ToolVision measurements were therefore reviewed as diagnostic
evidence, not applied automatically.

## Evidence from the real calibration session

Current production values and the two ToolVision runs from the same session are
shown below. `Difference` is `measured - production`; it is shown only for
comparison and must not be interpreted as an instruction to add that value to
the configured offset.

| Tool | Production Z | PF2 switch Z | PF2 difference | Cartographer Touch Z | Cartographer difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| T0 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 |
| T1 | +0.228 | +0.098 | -0.130 | +0.242 | +0.014 |
| T2 | -0.295 | -0.384 | -0.089 | -0.256 | +0.039 |
| T3 | -0.268 | -0.154 | +0.114 | -0.160 | +0.108 |
| T4 | -0.014 | +0.078 | +0.092 | +0.102 | +0.116 |

Additional observations:

- The PF2 run reported T0 return drift of `+0.028 mm`.
- The Cartographer Touch run reported T0 return drift of `-0.008 mm`.
- An older retained PF2 run reported T1 `+0.092`, T2 `-0.376`, T3 `-0.054`,
  and T4 `+0.090 mm`. The new PF2 differences were respectively `+0.006`,
  `-0.008`, `-0.100`, and `-0.012 mm`; T3 is the clear outlier.
- The latest Cartographer result is close to the print-tested production value
  for T1 and reasonably close for T2, but T3 and T4 differ by more than
  `0.10 mm`. A single run is not sufficient evidence to replace the values that
  already print well.
- In the implementation, each reported tool Z value is calculated as
  `tool_trigger_z - reference_trigger_z`. The configured tool offset is used to
  approach the station, but the result is not a residual correction to add to
  the configured value. The UI should state this explicitly.

## Problems observed

### P0: setup, method selection, and calibration are too easy to confuse

The main `TOOL_VISION` prompt groups Setup, Calibrate, Status, and Results. The
Setup prompt then places camera XY, physical switch Z, and Cartographer Touch Z
next to each other. Teaching either Z mechanism also changes the active Z
method used by the generic Z calibration action.

During this session, a PF2 switch calibration was followed a few minutes later
by Cartographer setup and another generic `Z only` run. The final confirmation
did not prominently restate the active method. Both runs completed, but the
second run replaced the first result file. This creates a realistic operator
error path: a setup action can silently change what the next calibration button
does.

### P1: the console is too noisy during a normal UI run

ToolVision emits preheat status, every per-tool measurement, return drift, and
the complete report. Heater waits and tool macros can also produce their own
messages. The combined stream makes it hard for an operator to find the few
items that matter: current stage, warnings, final offsets, and final drift.

ToolVision cannot necessarily suppress messages produced natively by Klipper
or third-party macros. It can, however, avoid duplicating them and make its own
responses concise by default.

### P1: a single latest-result file loses useful evidence

`results.json` is atomically rewritten for each completed run. Consequently,
the Cartographer run replaced the PF2 result from the same session. Method
comparison and repeatability analysis then require reconstructing data from the
console log.

### P1: result semantics are ambiguous

Labels such as `offset` or `relative offset` can be read as a delta that should
be added to the current configuration. For Z, the value is a measured physical
position relative to the reference tool and is therefore a candidate absolute
tool value, not an add-on correction. This distinction matters at the
hundredths-of-a-millimetre scale.

## Proposed interaction design

### 1. Give each routine a clearly named entry point

Keep the first prompt focused on routine work:

1. `Measure Z - PF2 switch`
2. `Measure Z - Cartographer Touch`
3. `Calibrate camera XY`
4. `Results and history`
5. `Advanced setup`

Setup/teaching belongs under `Advanced setup`, visually separated from routine
measurement. If a compact two-level menu is preferred, the active Z method
must still be visible in the first prompt.

The command API should accept an explicit method, for example:

```text
TOOL_VISION_CALIBRATE MODE=Z METHOD=SWITCH
TOOL_VISION_CALIBRATE MODE=Z METHOD=CARTOGRAPHER_TOUCH
```

Existing commands can remain backward compatible, but a UI-generated Z run
should not depend only on previously stored global method state.

### 2. Make the run confirmation an effective preflight

Before heating or motion, show one compact confirmation containing:

- exact method and method-specific display name;
- reference tool;
- station/fixture and taught position;
- requested nozzle temperature;
- tools to be measured;
- readiness of the selected mechanism;
- report-only statement: `No printer offsets will be applied`;
- result semantics: `Values are measured relative Z candidates, not deltas to add`.

The final action label should repeat the method, for example `Run Z - PF2
switch`, rather than only `Run Z`.

Teaching a different mechanism should show `Current method -> New method` and
confirm that the default will change. Teaching must not automatically begin a
calibration run.

### 3. Provide quiet progress with optional diagnostics

Add a verbosity option such as `quiet`, `normal`, and `debug`, or an equivalent
`QUIET=1` command parameter. UI buttons should use the quiet/normal operator
mode by default; direct CLI use can retain detailed diagnostics.

For a normal UI run:

- use one replaceable display/prompt status where possible, such as
  `Heating tools`, `Measuring T2 (3/5)`, `Returning to T0`, and `Cooling down`;
- always show errors and safety warnings immediately;
- avoid duplicate ToolVision responses for heater/tool status already emitted
  elsewhere;
- print one grouped final summary instead of repeating the full report in
  multiple forms.

### 4. Preserve result history

Store every successful run in an immutable, method-labelled file, for example:

```text
results/20260823-214200-switch.json
results/20260823-214700-cartographer_touch.json
```

`results.json` may remain as a backward-compatible copy or pointer to the latest
run. Retention should be configurable, with a conservative default such as the
latest 20 runs. The Results prompt should show timestamp, method, temperature,
reference drift, and a `Not applied` badge, and should allow comparison of the
last two compatible runs.

### 5. Label the final data precisely

Suggested Z result labels:

- `Measured Z relative to T0 (candidate absolute tool value)`
- `Difference from configured value (review only)`
- `Reference return drift (diagnostic; no universal pass threshold)`
- `Configuration changed: No`

Do not present drift alone as a universal pass/fail verdict unless a printer-
specific tolerance has been configured by the operator.

## Acceptance criteria

1. A user cannot start a UI Z calibration without seeing the selected method in
   both the preflight body and final action label.
2. Setup/teaching is separated from routine calibration, and changing the
   default method requires an explicit confirmation that names old and new
   methods.
3. The default UI path emits no more than six ToolVision-originated console
   messages for a successful run, excluding unavoidable native Klipper,
   heater, and third-party macro output. Errors remain unsuppressed.
4. Two consecutive runs with different methods remain available as separate
   result records; `results.json` backward compatibility is retained.
5. Z output clearly distinguishes a candidate absolute relative-to-reference
   value from a delta-to-apply.
6. No offset is applied automatically, and the final screen states that fact.
7. Existing CLI workflows remain backward compatible.
8. Automated tests cover method-explicit UI actions, method-change
   confirmation, quiet output, history retention, result labels, and the
   report-only invariant.

## Recommended implementation order

1. P0: explicit method in every Z action and confirmation; separate setup.
2. P1: immutable run history and precise result semantics.
3. P1: quiet UI output with errors always visible.
4. P2: last-run comparison and richer progress display.

Until repeatability is established with at least three runs under the same
method and temperature, the measured values above should remain diagnostic and
the print-tested production offsets should remain unchanged.

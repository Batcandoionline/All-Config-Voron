
## 1. Automatic OrcaSlicer profile synchronization

### Goal
Copy the active OrcaSlicer user presets directly from AppData into the repository and synchronize requested G-code/log diagnostics without manual export.

### Source
- `C:\Users\batca\AppData\Roaming\OrcaSlicer\user\838ce884-12ee-416b-9e1b-1c7503cf6b5f`
- Selected profile ID: `838ce884-12ee-416b-9e1b-1c7503cf6b5f`

### Updated files
- `extras/Orcasilcer setting/MulticolorPETG.json`
- `extras/Orcasilcer setting/Printersetting.json`
- `Orca Config/0.20mm PETG Multimaterial.json`
- `Orca Config/PETG Bambu Basic Black.json`
- `Orca Config/PETG Kabber Blue.json`
- `Orca Config/PETG TPoimns Orange.json`
- `Orca Config/PETG TPoimns Red.json`
- `Orca Config/PETG TPoimns White.json`
- `Orca Config/Voron Stealthchanger.json`

### Backup
- `extras/backups/pre-orcaslicer-profile-sync-20260730-154400`

### Validation
- All source and destination JSON files passed `ConvertFrom-Json` validation.
- Exact source bytes were copied without reformatting.

### Result
- 9 repository JSON file(s) synchronized.
- 0 G-code/log diagnostic file(s) added or updated.
- Use `Orca Config\Sync-OrcaProfiles.cmd` for one-click sync, commit and push.

## 2. Completed PETG five-tool print analysis

### Goal

Analyze the completed five-color PETG Voron Design Cube print, compare it with
the previous tool-crash incidents, reconcile the active OrcaSlicer presets with
the generated G-code, and calibrate OrcaSlicer's time estimate from Moonraker
history.

### Evidence

- G-code:
  `extras/gcode/voron_design_cube_v8-v1(1)_PETG_3h13m.gcode`
- Printed-object photographs:
  - `extras/pictures/IMG_20260730_152145.jpg`
  - `extras/pictures/IMG_20260730_152148.jpg`
  - `extras/pictures/IMG_20260730_152150.jpg`
  - `extras/pictures/IMG_20260730_152152.jpg`
  - `extras/pictures/IMG_20260730_152156.jpg`
  - `extras/pictures/IMG_20260730_152159.jpg`
- Prime-tower photograph:
  `extras/pictures/IMG_20260730_152140.jpg`
- Two supplied Discord screenshots discussing PETG drying, restart-extra
  length, filament ramming, standby temperature, preheating and material-change
  retraction.
- Active OrcaSlicer profile:
  `C:\Users\batca\AppData\Roaming\OrcaSlicer\user\838ce884-12ee-416b-9e1b-1c7503cf6b5f`
- Moonraker history API:
  `http://192.168.1.43/server/history/list?limit=30&order=desc`
- Related local logs:
  - `extras/logs/klippy.log`
  - `extras/logs/moonraker.log`

The local log snapshots predate this completed print. The exact duration for
this print therefore comes from Moonraker job history, not from those stale
snapshots.

### Confirmed G-code facts

- OrcaSlicer version: `2.4.2`.
- Generated estimate: `03:12:50`.
- Layers: `150`.
- Filament changes: `519`.
- Tool commands, including the initial tool selection:
  - `T0`: `130`
  - `T1`: `96`
  - `T2`: `130`
  - `T3`: `55`
  - `T4`: `109`
- Tool-change retraction: `6 mm` for all tools.
- Normal wipe: enabled for all tools, `0.5 mm` wipe distance.
- Multi-tool filament ramming: disabled for all tools.
- Prime tower: `type1`, maximum purge speed `45 mm/s`, framework enabled.
- Tool change on wipe tower: disabled.
- Print temperature: `220 °C` for all five PETG profiles.
- Idle temperature: `150 °C`.
- Saved process preheat time is `15 s`, but the generated G-code footer records
  `12 s`. The G-code value is authoritative for this completed print.
- `machine_tool_change_time` is absent from the saved machine preset and became
  `0 s` in the G-code estimate.

### Preset synchronization findings

The repository copy before this session was stale relative to the presets used
by OrcaSlicer. The synchronized differences include:

- Process preheat time: `20 s` to `15 s`.
- Object brim mode: `no_brim` to `painted`.
- Tool-change retraction: `5 mm` to `6 mm`.
- Normal wipe: disabled to enabled.
- Wipe tower: explicit `type1`.
- Tool-change time: the previous explicit `15 s` entry is no longer present, so
  the effective estimate value is `0 s`.
- Tool change on wipe tower: the previous explicit enabled entry is no longer
  present, so the effective G-code value is disabled.
- Multi-tool ramming enable entries were removed from all five active PETG
  profiles; the generated G-code confirms the effective value is disabled.
- Orange PETG print temperature: `225 °C` to `220 °C`.

The machine/process analysis aliases are now byte-identical to their active
repository counterparts:

- `extras/Orcasilcer setting/Printersetting.json`
- `extras/Orcasilcer setting/MulticolorPETG.json`

### Comparison with the previous tool-crash prints

The current job completed without a tool-crash, but it changed several variables
at once relative to the earlier failed prints:

| Item | Earlier failed prints | Current completed print |
| --- | --- | --- |
| Tool changes | `519` | `519` |
| Tool-change retract | `5 mm` | `6 mm` |
| Normal wipe | Off | On, `0.5 mm` |
| Multi-tool ramming | On | Off |
| Wipe tower | Type 2 | Type 1 |
| Tower purge speed | Up to `60`, later `45 mm/s` | `45 mm/s` |
| Machine tool-change estimate | `0` or `15 s` | `0 s` |

The successful completion therefore cannot be attributed to a single parameter.
The strongest local evidence is that disabling ramming, enabling wipe and
increasing tool-change retraction reduced the peak blobs enough to avoid the
previous tower collision. The remaining loose multi-color curls show that the
underlying dock-to-tower contamination has not been eliminated.

### Photograph findings

- There is no clear global layer shift, catastrophic XY registration error or
  bed-adhesion failure on the object.
- Several color boundaries and vertical faces are acceptably aligned.
- Top surfaces vary by color/tool, so per-spool flow, pressure advance,
  temperature and cooling should not be treated as uniformly calibrated.
- One logo/feature face has severe loose white strands. This may be transferred
  tower debris or a local unsupported/overhang failure; supports are disabled in
  the current G-code. A same-model single-tool print is required to separate
  those causes.
- The prime-tower brim and outer body remain attached, but long loose loops
  accumulate on both sides and across the top. The loops contain several colors,
  supporting a shared tool-change path problem rather than a T0-only fault.

### Root-cause assessment

The current tool pickup sequence reaches the full PETG target while the tool is
still at its dock, then moves the hot nozzle to the tower. With `519` changes,
even a small hot PETG tail is repeated hundreds of times. The photograph is
consistent with two coupled effects:

1. PETG oozes or carries a tail during full-temperature travel from the dock.
2. Some tower entry/purge lines fail to anchor cleanly and are pulled into long
   loops; later passes can catch and enlarge them.

The completed print reduces the prior collision outcome but does not disprove
this mechanism. Drying remains a valid prerequisite, but wet filament alone
does not explain why the debris is concentrated around repeated tool-change
travel and tower entry.

### Time-estimate calibration

Moonraker job `000203` reports:

- Status: completed.
- Start: `2026-07-30 06:32:13 +07:00`.
- End: `2026-07-30 13:08:11 +07:00`.
- `print_duration`: `23,451.594 s` = `06:30:51`.
- `total_duration`: `23,758.681 s` = `06:35:58`.

The generated G-code estimate with tool-change time set to zero is `11,570 s`.
The measured average unmodelled overhead is:

```text
(23,451.594 - 11,570) / 519 = 22.893 seconds per tool change
```

Setting OrcaSlicer `machine_tool_change_time` to `22.9 s` would predict
approximately `06:30:55` for this file. This setting corrects statistics only;
it does not insert a G-code delay. For future calibration, use the median result
from two or three completed prints with the same tool-change sequence:

```text
tool_change_time =
    (Moonraker print_duration - Orca estimate at 0 s) / filament_changes
```

Recalibrate after changing preheat timing, pickup mechanics or tool-change
retraction. Use `total_duration` separately when wall-clock startup and ending
time are required.

### Recommended controlled test order

No production preset was tuned in this session. The following changes require
user approval and should be tested one variable group at a time:

1. Save the Orca project overrides into named presets so that the saved
   `preheat_time` and generated footer no longer disagree.
2. Set `machine_tool_change_time` to `22.9 s` for estimate accuracy.
3. Print a short 40-to-60-change tower coupon while keeping ramming off,
   retraction at `6 mm`, wipe enabled, `220 °C` print temperature and `150 °C`
   idle temperature.
4. Test Type 2 tower with tool change on the wipe tower as one paired change.
   Earlier Type 2 crashes also had ramming on, wipe off and shorter retraction,
   so they do not isolate Type 2 as the cause.
5. If a hot tail remains, increase wipe distance from `0.5` to `1.0 mm`; verify
   a continuous first tower line before trying `7 mm` tool-change retraction.
6. Keep restart-extra length at `0` during the baseline. A negative value acts
   after pickup and cannot directly stop ooze that already occurred before
   reaching the tower.
7. Dry every PETG spool to its manufacturer's specification and verify blocker
   contact/cleaning for all five tools.
8. If full-temperature dock-to-tower ooze remains, use a late mechanical
   wiper/string catcher near the tower path. A two-stage heat sequence would be
   the firmware alternative, but it conflicts with the current decision not to
   modify or override `pickup_gcode` without explicit approval.
9. Print the same model with one tool and no tower. If the loose feature remains,
   tune orientation/support/cooling; if it disappears, focus on tower transfer
   and tool-change ooze.
10. Calibrate flow, pressure advance and temperature for each physical
    spool/tool, then run a lower-speed quality comparison before raising speeds.

### Official references

- OrcaSlicer advanced multi-material settings:
  https://www.orcaslicer.com/wiki/printer_settings/multimaterial/printer_multimaterial_advanced
- OrcaSlicer ooze prevention:
  https://www.orcaslicer.com/wiki/print_settings/multimaterial/multimaterial_settings_ooze_prevention
- OrcaSlicer wipe tower:
  https://www.orcaslicer.com/wiki/printer_settings/multimaterial/printer_multimaterial_wipe_tower
- OrcaSlicer prime tower:
  https://www.orcaslicer.com/wiki/print_settings/multimaterial/multimaterial_settings_prime_tower
- OrcaSlicer material multi-tool settings:
  https://www.orcaslicer.com/wiki/material_settings/multimaterial/material_multimaterial
- Moonraker printer objects:
  https://moonraker.readthedocs.io/en/latest/printer_objects/
- Moonraker history API:
  https://moonraker.readthedocs.io/en/latest/external_api/history/

### Result

- Active OrcaSlicer JSON profiles were synchronized and backed up.
- No Klipper or toolchanger configuration was changed.
- No new production tuning values were applied.
- The remaining primary issue is cumulative full-temperature PETG
  dock-to-tower contamination, amplified by tower entry stability across
  `519` tool changes.

## 3. PETG maximum volumetric speed assessment

### Goal

Assess whether the uncalibrated `15 mm³/s` filament maximum volumetric speed is
reasonable for the TZ V6 2.0 setup and whether it can explain the tower debris.

### Current G-code

- Layer height: `0.20 mm`.
- Maximum volumetric speed: `15 mm³/s` for all five tools.
- Outer wall: `0.42 mm × 0.20 mm × 120 mm/s`, approximately `10.1 mm³/s`.
- Top surface: `0.42 mm × 0.20 mm × 100 mm/s`, approximately `8.4 mm³/s`.
- Inner wall request: `0.45 mm × 0.20 mm × 200 mm/s`, approximately
  `18.0 mm³/s`; therefore capped by the `15 mm³/s` filament limit.
- Internal solid infill request: `0.42 mm × 0.20 mm × 230 mm/s`,
  approximately `19.3 mm³/s`; therefore capped.
- Sparse infill request: `0.45 mm × 0.20 mm × 230 mm/s`, approximately
  `20.7 mm³/s`; therefore capped.
- A `0.42 mm × 0.20 mm` tower path at the configured `45 mm/s` purge speed is
  approximately `3.8 mm³/s`, far below the filament limit.

### Assessment

`15 mm³/s` is a plausible ceiling for this hotend, but hotend model alone does
not validate it. The usable quality limit also depends on the exact PETG brand
and color, nozzle, print temperature, extruder and cooling. At the current
`220 °C`, opaque white, black and other pigmented PETG profiles may reach their
quality limit at different flow rates.

The current limit affects fast inner/infill paths but does not explain the
dock-to-tower PETG tails or loose tower loops. A high maximum volumetric-speed
setting is only a ceiling; it does not force every path to extrude at that flow.

### Recommended calibration

Run OrcaSlicer's Max Volumetric Speed calibration for each of the five active
filament/tool combinations at the actual `220 °C` print condition. Use the
official `5–20 mm³/s` range and `0.5 mm³/s` step, identify the first visible
loss of surface quality, sheen consistency, adhesion or extrusion, then set the
production profile `10–20%` below that failure value. Calibrate temperature
before maximum volumetric speed and pressure advance/flow afterwards.

### Official references

- OrcaSlicer material volumetric-speed limit:
  https://www.orcaslicer.com/wiki/material_settings/filament/material_volumetric_speed_limitation.html
- OrcaSlicer maximum flow calibration:
  https://github.com/OrcaSlicer/OrcaSlicer/wiki/volumetric_speed_calib
- OrcaSlicer calibration order:
  https://www.orcaslicer.com/wiki/calibration/Calibration/

### Result

No profile value was changed. Keep `15 mm³/s` as a temporary ceiling until
per-spool tests provide measured limits; focus the tower-debris investigation
on tool-change ooze, wiping and tower entry rather than hotend throughput.

## 4. Verification of the `8 mm / -3 mm` tool-change settings

### Goal

Verify whether `Retraction When Switching Materials = 8 mm` and
`Extra length on restart = -3 mm` are present and executed in
`extras/gcode/voron_design_cube_v8_PETG_6h28m.gcode`.

### Confirmed values

- OrcaSlicer version: `2.4.2`.
- Generated: `2026-07-30 16:11:02`.
- Tool changes: `519`.
- Estimated time: `06:28:22`.
- `machine_tool_change_time`: `22.9 s`.
- `retract_length_toolchange`: `8,8,8,8,8`.
- `retract_restart_extra_toolchange`: `-3,-3,-3,-3,-3`.
- Exact `G1 E-8 F1800` unload moves: `519`, one per tool change.

The restart compensation is integrated into the Type 2 tower extrusion paths
rather than emitted as one standalone `G1 E5` command. Semantically, an `8 mm`
retract plus `-3 mm` restart extra leaves a nominal `5 mm` compensation. For
1.75 mm filament, the negative `3 mm` removes approximately `7.216 mm³` from
the restart amount.

### Comparison with the previous completed G-code

The new file changes more than the two requested retraction values:

| Setting | Previous completed file | New file |
| --- | --- | --- |
| Tool-change retract | `6 mm` | `8 mm` |
| Restart extra | `0 mm` | `-3 mm` |
| Filament ramming | Off | On |
| Ramming volume | Inactive | `5 mm³` per change |
| Preheat time | `12 s` | `15 s` |
| Tower type | Type 1 | Type 2 |
| Statistical tool-change time | `0 s` | `22.9 s` |

The new G-code contains `519` outgoing `E2.0788` moves, each equal to
approximately `5 mm³` of 1.75 mm filament, before the `E-8` retract. Ramming
therefore adds `2.595 cm³` of planned outgoing material across the job. This
conflicts with the previous ramming-off baseline and can recreate raised tower
material.

Total planned filament falls from `67.13 g` to `43.54 g`, a reduction of
`23.59 g` or `35.1%`. This confirms that the new tower/restart combination
materially changes the generated tool-change paths, but the reduction cannot be
attributed to `-3 mm` alone because the tower type also changed.

### Assessment

- The `8 mm` and `-3 mm` values are correctly stored and used by OrcaSlicer.
- G-code inspection cannot prove that they stop physical PETG ooze; that
  requires a print observation or photograph.
- `8 mm` can reduce residual pressure before parking.
- `-3 mm` acts when extrusion resumes and cannot prevent material that already
  leaked during full-temperature dock-to-tower travel.
- `-3 mm` is aggressive relative to the configured `15 mm³` minimal purge and
  can cause an under-filled first tower line or delayed extrusion at the
  object.
- The file is not a controlled A/B test because ramming, preheat and tower type
  changed at the same time.

### Recommendation

Do not use the full `519`-change object as the first validation print. Generate
a 40-to-60-change coupon. For a clean test of the community recommendation,
disable multi-tool ramming again and keep all other baseline variables fixed.
Test `8/0`, then `8/-1`; only retain `8/-3` if the first tower line is continuous,
the object resumes without under-extrusion and the dock-to-tower tail is
visibly shorter. If the travel tail does not improve with `8/0`, a negative
restart-extra value will not correct the root cause.

### Official reference

- OrcaSlicer retraction settings:
  https://www.orcaslicer.com/wiki/printer_settings/extruder/printer_extruder_retraction

### Result

No G-code or profile was modified. The new file correctly encodes `8/-3`, but
ramming must be disabled and a short physical coupon must pass before this
combination can be considered validated for production.

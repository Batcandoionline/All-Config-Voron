# Session Updates — 2026-07-29

## Clarification: T0 already has an RTV silicone blocker

### New observation
- The T0 dock already has an RTV silicone blocker.
- The blocker currently contains ooze while the tool is parked, but T0 still carries an approximately 5 mm PETG tail after pickup and deposits it at the repeated prime-tower entry point.

### Updated diagnosis
- The blocker is performing its parked-tool function. It does not clean or sever the material attached to the nozzle when the nozzle separates from the silicone.
- The remaining failure window is the release from the blocker and the hot travel from the dock to the tower.
- StealthChanger documents these as two separate components:
  - the blocker prevents ooze while docked;
  - the PTFE/Bambu wiper cleans the nozzle as the tool exits the dock.

### Updated priority
1. Verify blocker preload:
   - retract the blocker;
   - make the tool sit flush in the dock;
   - raise the blocker only until it touches the nozzle without pushing the toolhead.
2. Add or correctly position a PTFE/Bambu exit wiper for T0 so the nozzle crosses it after leaving the blocker.
3. Keep the slicer-side mitigation plan:
   - disable multi-tool ramming for T0;
   - enable wipe while retracting for T0;
   - test preheat at 16 s, then 14 s if required;
   - keep 5 mm toolchange retract first and test 5.5/6 mm only if the exit tail remains.
4. If an exit wiper cannot be installed, use two-stage heating or a short Z-safe `TOOLCHANGE_FLICK` routine.

### Source
- StealthChanger Modular Dock: https://stealthchanger.com/hardware/modular_dock/
- StealthChanger dock adjustment guidance: https://sdylewski.github.io/StealthChanger/Docks/

## Observation update: the 5 mm strand grows during dock-to-tower travel

### Revised diagnosis
- T0 does not primarily pull the 5 mm strand from the RTV blocker. The strand grows after pickup during the approximately five-second hot move from the dock to the prime tower.
- An exit wiper can remove residue present at dock release, but it cannot prevent a new strand from growing after the nozzle has passed the wiper.
- The current pickup macro waits for the selected extruder to reach its full target temperature while the nozzle is on the pad. Therefore `preheat_time` mainly changes how long the shuttle waits at the dock; T0 still leaves the dock at the full 225°C target.
- Shortening `preheat_time` alone cannot eliminate hot-travel ooze while the pickup macro retains the full-target `M109` wait.

### Updated solution order
1. Run a controlled pickup-temperature test at 195, 200, 205, 210 and 225°C over the same five-second travel, recording strand length. Select the highest pickup temperature that keeps the strand below approximately 1 mm.
2. Implement two-stage heating:
   - heat/wait only to the measured pickup temperature while docked;
   - pick up and travel toward the tower;
   - complete heating to 225°C at the tower;
   - purge before printing.
3. If two-stage heating is not yet available, perform the final flick/wipe as late as possible, near the tower or at the existing brush, rather than relying only on a dock-exit wiper.
4. Continue reducing internal pressure by disabling T0 multi-tool ramming, enabling wipe while retracting, drying the PETG and testing toolchange retract in 0.5 mm increments.
5. Do not lower the actual object printing temperature; the final tower-side `M109` must still reach 225°C.

## New unlogged failure: ToolCrash occurred while T4 was active

### Observation
- A later print reached approximately two thirds of the cube before ToolCrash.
- T4 was active at the failure, and loose plastic debris was again present on the prime tower.
- The logs currently stored in `extras/logs/` were last updated on 2026-07-28 at about 20:06 and do not contain this newer event.

### Interpretation
- The active tool at crash time is the tool that detected or experienced the collision; it is not necessarily the tool that deposited the debris.
- Tool selection counts in the 5h02 G-code are T0=150, T1=150, T2=110, T3=55 and T4=55.
- Incoming T4 transitions are primarily T2→T4 (34) and T1→T4 (20), with only one T0→T4 transition. Therefore the new observation weakens a T0-only explanation and supports a shared hot-travel/tower-contamination mechanism.
- A late failure after roughly two thirds of the model is consistent with repeated small deposits accumulating until one tool collides with a sufficiently high fragment.

### Revised scope
1. Apply the two-stage pickup-temperature strategy to every tool, with a per-tool pickup temperature if required.
2. Disable multi-tool ramming and enable wipe while retracting for all PETG tools during the diagnostic print, not only T0.
3. Use a late wipe/flick shared by all tools, as close to the tower as safely possible.
4. Record the color of the highest debris and the immediately preceding tool at the next event; this identifies the depositing tool more reliably than the ToolCrash tool number.
5. Use a shorter 40–60-change diagnostic coupon before repeating the full 520-change cube.

## 1. Automatic OrcaSlicer profile synchronization

### Goal
Copy the active OrcaSlicer user presets directly from AppData into the repository and remove the need for manual JSON export.

### Source
- `C:\Users\batca\AppData\Roaming\OrcaSlicer\user\838ce884-12ee-416b-9e1b-1c7503cf6b5f`
- Selected profile ID: `838ce884-12ee-416b-9e1b-1c7503cf6b5f`

### Updated files
- `extras/Orcasilcer setting/MulticolorPETG.json`
- `extras/Orcasilcer setting/Printersetting.json`
- `Orca Config/0.20mm PETG Multimaterial.json`
- `Orca Config/PETG Bambu Basic Black.json`
- `Orca Config/PETG Kabber Blue.json`
- `Orca Config/PETG Tinmory.json`
- `Orca Config/PETG TPoimns Orange.json`
- `Orca Config/PETG TPoimns Red.json`
- `Orca Config/PETG TPoimns White.json`
- `Orca Config/Voron Stealthchanger.json`

### Backup
- `extras/backups/pre-orcaslicer-profile-sync-20260729-155440`

### Validation
- All source and destination JSON files passed `ConvertFrom-Json` validation.
- Exact source bytes were copied without reformatting.

### Result
- 10 repository JSON file(s) synchronized.
- Use `Orca Config\Sync-OrcaProfiles.cmd` for one-click sync, commit and push.

## 2. One-click OrcaSlicer and diagnostic Git synchronization

### Goal
Automatically synchronize OrcaSlicer profiles and publish the requested G-code/log diagnostics without manual JSON export or separate Git commands.

### Files added or documented
- `Orca Config/Sync-OrcaProfiles.ps1` — discovers the active Orca account, validates/copies JSON, creates local backups, writes the daily journal, and optionally commits/pushes.
- `Orca Config/Sync-OrcaProfiles.cmd` — one-click launcher using `-IncludeDiagnostics -Commit -Push`.
- `Orca Config/README.md` — documents automatic and command-line use.

### Diagnostic scope
- All `.gcode` files under `extras/gcode/` were force-added because the extension is normally ignored.
- `extras/logs/klippy.log` and `extras/logs/moonraker.log` were force-added.
- Existing untracked Orca JSON exports and the two analysis aliases were included.

### Safety and validation
- Largest individual file: approximately 38.15 MiB, below GitHub's 100 MiB single-file limit.
- No password, bearer token, API-key, access-token, secret, or token-assignment pattern was detected in the two log files or Orca JSON files.
- All 24 repository Orca JSON files passed `ConvertFrom-Json`.
- A second profile synchronization run reported zero updates, confirming idempotent behavior.

### Backup
- `extras/backups/pre-orcaslicer-profile-sync-20260729-155440/` (local and gitignored).

## Full G-code, Klipper configuration, and Orca profile correlation

### Scope
- Scanned all 243,251 lines of `voron_design_cube_v8-v1(1)_PETG_5h2m.gcode`.
- Scanned the complete 31-file Klipper include tree (3,957 lines).
- Parsed all 24 live Orca JSON profiles under `Orca Config/` and
  `extras/Orcasilcer setting/`; backup copies were excluded from the live-profile
  count.
- Compared the live JSON values with the settings footer embedded by Orca in the
  generated G-code.

### G-code findings
- The print contains 520 tool-change blocks.
- Incoming selections are T0=150, T1=150, T2=109, T3=55, and T4=55; the initial
  T2 selection occurs outside the regular tool-change blocks.
- T4 is normally selected after T2 (34 times) or T1 (20 times), and only once
  after T0. The active tool at a ToolCrash is therefore the collision victim and
  does not identify the tool that deposited the debris.
- Every PETG profile enables 5 mm3 of multi-tool ramming at 8 mm3/s. The print
  schedules approximately 2.6 cm3 of rapid ramming across the 520 changes.
- The outgoing tool is retracted by 5 mm, cooled to 150 C, and the incoming tool
  is restored by 5 mm at the tower. No positive G4 dwell is present.
- The generated file has `wipe = 0,0,0,0,0` even though two legacy duplicate
  machine JSON files contain `wipe = 1,1,1,1,1`.

### Temperature and timing findings
- The readonly upstream pickup macro waits for the selected tool's full current
  target with `M109` while the nozzle is resting on the blocker pad.
- The local override changes dropoff behavior but does not override pickup, so
  the full-target wait remains active.
- The fine pickup path takes approximately 3.42 seconds at 15 mm/s. Restoring
  from the dock to the tower adds approximately 2.3-2.6 seconds at the configured
  250 mm/s fast speed. This predicts the observed 5-6 second hot travel.
- Comparison of the two cube G-codes:
  - `2h24m`, machine tool-change time 0: effective preheat comments average
    20.09 seconds (20-22 seconds).
  - `5h02m`, machine tool-change time 15: effective preheat comments average
    30.03 seconds (20-35 seconds).
- The 15-second value does not emit a physical dwell, but this Orca build uses
  the estimate when placing preheat commands. The newer file therefore heats the
  next tool roughly ten seconds earlier on average and increases full-temperature
  soak behind the silicone blocker.

### Correlated diagnosis
- The prime-tower brim and outer frame remain attached. The photograph shows
  multi-color fragments accumulated on purge bands, consistent with repeated
  carried ooze rather than initial tower adhesion failure.
- The silicone blocker controls ooze only while parked. It cannot stop thermal
  expansion from creating a new strand after the nozzle leaves the blocker.
- The primary failure is full-temperature pickup plus a 5-6 second dock-to-tower
  flight, amplified by early preheating, disabled wipe-while-retracting, enabled
  ramming on all five filaments, and 520 repetitions.
- The stored logs end at 2026-07-28 20:06 and contain the earlier T0 crash only;
  they do not contain the later unlogged T4 crash.

### Recommended implementation order
1. Set the Orca machine tool-change time back to 0 while diagnosing. It is a
   statistics field, and in this Orca build it also moves preheat commands earlier.
2. Disable multi-tool ramming and enable wipe while retracting for all five PETG
   profiles. Keep the 5 mm tool-change retract initially.
3. Add a local pickup override (never edit readonly configuration) that waits only
   for a measured release temperature, initially 200 C, while leaving the final
   220-225 C target active so heating finishes during the 5-6 second flight.
4. Add a short Z-safe purge/flick at the existing X320/Y-8 bucket immediately
   before returning to the tower, or add a dedicated late wiper/catch point.
5. Validate with a 40-60-change diagnostic coupon before repeating the full
   520-change cube.

### Primary references
- OrcaSlicer Ooze Prevention:
  https://www.orcaslicer.com/wiki/print_settings/multimaterial/multimaterial_settings_ooze_prevention
- OrcaSlicer Retraction:
  https://www.orcaslicer.com/wiki/printer_settings/extruder/printer_extruder_retraction
- OrcaSlicer Prime Tower:
  https://www.orcaslicer.com/wiki/print_settings/multimaterial/multimaterial_settings_prime_tower
- OrcaSlicer Material Multimaterial:
  https://www.orcaslicer.com/wiki/material_settings/multimaterial/material_multimaterial
- OrcaSlicer Advanced Multi-Material Settings:
  https://www.orcaslicer.com/wiki/printer_settings/multimaterial/printer_multimaterial_advanced
- Klipper Pressure Advance:
  https://www.klipper3d.org/Pressure_Advance.html
- StealthChanger Modular Dock:
  https://stealthchanger.com/hardware/modular_dock/

## 2026-07-29 - StealthChanger-specific ooze-control research

### Confirmed upstream behavior
- Official StealthChanger documentation defines the RTV blocker as protection
  while the nozzle is docked and the optional PTFE/Bambu wiper as a cleaner while
  the tool exits the dock. Neither component can prevent a new strand from
  forming after the nozzle has left the wiper.
- Official tuning guidance states that a normal Voron 2.4 tool change is under
  10 seconds and eventually becomes limited by the physical pickup operation.
  The observed 5-6 second pickup-to-tower interval is therefore not itself a
  fault and should not be removed by unsafe motion increases.
- The upstream klipper-toolchanger selection sequence activates the incoming
  extruder before executing its `pickup_gcode`. This makes a guarded, local
  pressure-relief retract technically possible while the incoming nozzle is
  still resting on its RTV blocker. Any added retract must be restored only at a
  waste location, not over the model or the tower entry point.

### Recommended StealthChanger control sequence
1. Keep the incoming tool below full PETG print temperature while parked; use a
   measured release temperature around 195-205 C, initially 200 C.
2. While the nozzle is still sealed by the RTV blocker, apply only a small
   additional pressure-relief retract, initially 0.5 mm.
3. Pick up the tool normally and allow the existing 5-6 second motion to provide
   most of the remaining heat-up time.
4. Finish heating, restore the additional 0.5 mm, and perform a short purge/flick
   at a waste bucket or late wiper immediately before returning to the tower.
5. Keep Orca's 5 mm tool-change retract initially, disable multi-tool ramming,
   enable wipe-while-retracting, and set machine tool-change time to 0 while
   validating.

### Validation limits
- Do not jump directly to very long tool-change retractions: excessive retraction
  can pull softened PETG into the heatbreak and cause clogs or missing extrusion.
- Tune the added pressure-relief retract in 0.5 mm steps and stop when the
  pickup-to-tower strand is at most 1 mm and the first prime line remains
  continuous.
- Dry PETG remains a prerequisite because moisture materially increases leakage
  from a preheated nozzle.

### Additional references
- StealthChanger slicer guidance:
  https://stealthchanger.com/software/slicers/
- StealthChanger tuning:
  https://stealthchanger.com/calibration/tuning/
- klipper-toolchanger selection sequence:
  https://raw.githubusercontent.com/viesturz/klipper-toolchanger/main/klipper/extras/toolchanger.py
- klipper-toolchanger tool activation:
  https://raw.githubusercontent.com/viesturz/klipper-toolchanger/main/klipper/extras/tool.py
- Prusa multi-tool moisture and travel-ooze guidance:
  https://help.prusa3d.com/article/printing-without-purge-tower-on-the-xl-multi-tool_649633

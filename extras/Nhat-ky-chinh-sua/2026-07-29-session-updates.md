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

## 2026-07-29 - Refined local pickup-override design

### Local geometry constraint
- The existing `CLEAN_NOZZLE` brush/bucket is at X320/Y-8/Z2 while the tool
  docks are at approximately Z343.
- Calling the complete cleaning macro during every pickup would add a full-height
  Z trip and a multi-pass scrub to every change. It is not suitable for a
  520-change print.
- The first implementation should therefore perform pressure relief on the RTV
  blocker only. A dedicated late wiper should be considered separately only if
  pressure relief is insufficient.

### Phase-one pickup behavior
- Preserve the complete upstream pickup path and verification sequence in a
  local `[toolchanger] pickup_gcode` override.
- During an active print only:
  1. Keep the incoming heater's final target unchanged.
  2. Replace the full-target dock wait with
     `TEMPERATURE_WAIT SENSOR=<incoming extruder> MINIMUM=200`.
  3. Because klipper-toolchanger has already activated the incoming extruder,
     issue a relative 0.5 mm retract at 30 mm/s while the nozzle remains on the
     RTV blocker.
  4. Execute the original pickup path and position restore unchanged.
- Preserve the upstream full-target `M109` behavior outside an active print so
  PRINT_START, calibration, pause, and manual tool selection do not unexpectedly
  change behavior.
- Set Orca's tool-change restart-extra value to 0.5 mm so a generated `G1 E5`
  restore becomes `G1 E5.5`, compensating exactly for the added pickup retract
  on the prime tower.

### Initial tuning range
- Start with release temperature 200 C and pickup pressure relief 0.5 mm.
- If the post-blocker strand remains longer than 1 mm, test 0.8 mm and then
  1.0 mm.
- If the first prime line is incomplete, reduce pressure relief or confirm that
  Orca generated the matching restart compensation.

## 2026-07-29 - DraftShift Discord ooze-control research

### Access and scope
- Searched the signed-in DraftShift Design Discord desktop application in
  read-only mode. No message, reaction, account setting, or server setting was
  changed.
- Mouse-driven search automation was stopped after it was found to take control
  away from the user. Discord is not currently running with an Electron remote
  debugging port; starting a second process with
  `--remote-debugging-port=9223` did not enable one on the existing instance.

### Community findings
- MikeyMike (DSD), `#general`, 2026-07-22: the common baseline is Orca ooze
  prevention for idle temperature and preheating, spring-steel/silicone
  overmold blockers, tool-change retract settings, and a small prime tower.
  A front-bed brush is used mostly for nozzle probing rather than as the main
  tool-change ooze solution.
- Drakarah, `#help-and-support`, 2025-08-16: restore a picked tool using a safe
  sequence of `Z+5`, then `XY`, then final `Z`. This sends leakage that begins
  during pickup to the tower instead of dragging the nozzle across the model.
  The same message recommends a sufficiently wide, measured `M109` deadband to
  avoid unnecessary waiting for heater overshoot.
- Nic335 (DSD), `#stealthchanger`, 2026-07-28: Orca's move-to-prime-tower
  behavior can be used without multi-tool ramming. The main value is restoring
  the tool to the prime tower so incidental ooze is caught there; ramming is not
  necessarily required for that movement.
- Other community replies recommend small prime towers, toolchanger ramming,
  and ooze prevention as a general starting point. This is not a consensus that
  ramming must stay enabled for every machine.

### Local interpretation
- The local printer already enables `tool_change_on_wipe_tower`, so it can keep
  the important return-to-tower behavior while testing all five PETG filament
  profiles with multi-tool ramming disabled.
- Because this printer's failure is tower over-height caused by repeated
  leakage and blobs, disabling the current 5 mm3 ramming is a targeted
  diagnostic A/B test, not a universal StealthChanger rule.
- No DraftShift result established a universal numeric retract for the TZ V6
  2.0. The current 5 mm Orca tool-change retract is already substantial;
  increasing it blindly is not supported by the community evidence.
- The Discord restore-order guidance strengthens the case for a local guarded
  pickup override: pressure relief on the blocker, a safe raised return toward
  the tower, final descent, then restart compensation/purge at the tower.

## 2026-07-29 - Background Discord control and matching failure thread

### Background access
- Restarted Discord with Electron remote debugging bound only to
  `127.0.0.1:9223`.
- Connected through the local DevTools protocol and verified the signed-in
  DraftShift Design session.
- Search and message inspection now run through the background DOM. They do not
  synthesize mouse or keyboard input and do not take focus from the user.

### Exact matching community case
- AjzRide, `#stealthchanger`, 2025-09-06, reported heavy ooze while a toolhead
  traveled down from its dock. It accumulated as a clump on the prime tower or
  fell onto the print before the move to the tower. The user specifically asked
  about fetching at standby temperature and heating near print height.
- Community replies recommended:
  - an Orca waiting/idle temperature, with 175 C given only as an example;
  - tuning Orca's preheat time;
  - tuning tool-change retraction in the Orca GUI.
- cekim noted that insufficient preheat can produce under-extrusion or clogging
  because heat must propagate from the nozzle walls into the center of the
  filament column. This confirms that moving all heating to bed level is not a
  zero-risk change.
- The thread did not provide a standard macro that fetches fully at standby
  temperature and heats only at bed level. It ended with Orca preheat and
  tool-change retraction tuning.

### Retraction and blocker evidence
- MikeyMike (DSD), 2025-06-11, stated that practical tool-change retracts vary
  with hotend, nozzle, filament, cooling, and tool-change time; the reported
  range was 4-15 mm, with tip shaping suggested as the upper-limit reference.
- Shane, 2025-10-12, reported that increasing post-toolchanger retraction still
  did not stop leakage. MikeyMike separately noted that retract/de-retract helps
  stringing, but the sequence and timing may still fail to solve the ooze blob.
- A separate community diagnostic recommends checking each silicone blocker for
  visible clearance at the nozzle. A gap at one tool can explain why a specific
  tool, such as T4, oozes more than its neighbors.

### Updated local test order
1. Confirm light contact between every nozzle and its silicone pad, especially
   T4; no visible light gap is acceptable.
2. Disable the current 5 mm3 multi-tool ramming for all five PETG profiles while
   retaining Orca's move-to-prime-tower behavior.
3. Keep the measured preheat strategy; do not copy the community's 30-second
   example because the local 20-second file already heated far too early.
4. Test the existing 5 mm tool-change retract first, then 6, 7, and 8 mm in
   separate short tool-change coupons. Do not jump directly to 15 mm.
5. Only if the GUI-only tests still leave a long pickup strand, test the guarded
   pickup override with a 200 C release, 0.5 mm pressure relief on the blocker,
   raised `Z+5 -> XY -> Z` return, and matched restart compensation on the
   tower.

## 2026-07-29 - Non-pickup-gcode mitigation plan

### User constraint
- Do not modify or override `pickup_gcode`.
- Prefer OrcaSlicer settings and mechanical ooze control. A wider local `M109`
  deadband is an optional printer-wide timing optimization, not a pickup-path
  change.

### Evidence from the active profiles and generated file
- `voron_design_cube_v8-v1(1)_PETG_5h2m.gcode` was generated with 520 tool
  changes, 20 s preheat, 15 s machine tool-change time, 5 mm tool-change
  retraction, wipe disabled for every extruder, and 5 mm3 multi-tool ramming
  enabled for all five filaments.
- Direct inspection of tool changes #1-#3 shows the outgoing sequence extrudes
  approximately 2.0788 mm of filament as the 5 mm3 ramming pulse and then
  retracts 5 mm before `Tn`. After pickup there is no `G1 E5` restore before
  travel to the tower; priming resumes progressively in the tower extrusion
  moves. The observed strand therefore is not caused by an early 5 mm
  unretract. It is consistent with residual molten-zone pressure/gravity despite
  the existing retract.
- At 520 changes, 5 mm3 ramming alone commands approximately 2,600 mm3
  (2.6 cm3) of extra tower material before accounting for purge, priming, and
  uncontrolled leakage.
- The generated file uses the `Voron Stealthchanger` printer profile. Its wipe
  arrays are disabled even though the separate `Stealthchanger.json` profile
  has wipe enabled; changes must therefore be made in the profile actually
  selected for slicing.
- All five filament profiles use a non-zero 150 C idle temperature. In Orca,
  this explicit idle temperature takes priority over the configured -80 C
  standby delta.
- The local `SET_TEMPERATURE_WITH_DEADBAND` macro already replaces exact `M109`
  stabilization with a 4 C total window (target +/-2 C).

### GUI-only baseline
1. Set machine tool-change time to 0 s. It is an estimate, not a physical delay,
   and the local 15 s value causes excessively early heat scheduling and an
   inflated slice estimate.
2. Start preheat at 12 s and test 12-14 s. The local log with 2 s preheat showed
   about 13 s of additional temperature waiting; the target is no more than
   0-2 s of final wait without reaching full temperature early at the dock.
3. Keep idle temperature at 150 C initially. Do not raise it to community
   examples from machines with different hotends and materials.
4. Disable `filament_multitool_ramming` in all five PETG filament profiles.
   Keep Type 2 and `tool_change_on_wipe_tower` enabled so the incoming tool still
   returns to the tower.
5. Enable wipe while retracting on all five extruders, starting with the
   existing 0.5 mm wipe distance and 70 percent retract-before-wipe.
6. Keep tool-change retract at 5 mm for the first A/B coupon, then test 6, 7,
   and 8 mm one value at a time. Keep restart extra at 0 initially; only add
   0.2-0.5 mm if the first tower extrusion is visibly starved.
7. Keep the current conservative 45 mm/s maximum tower purge speed and 40 mm
   tower width. Do not trade a leakage problem for a higher tower collision
   impulse.

### Mechanical controls
- Verify light spring contact between each TZ V6 nozzle and RTV blocker,
  especially T4. Any visible light gap allows a parked tool to retain a bead
  before release.
- Align a silicone lip or dock-exit wiper so it removes the initial bead during
  undock. A blocker seals while parked but cannot stop pressure-driven leakage
  during the subsequent 5-6 s travel.
- Dry PETG before comparing retract values so moisture expansion is not
  mistaken for hotend pressure.

### Optional non-pickup printer setting
- PID-tune each hotend at its real PETG print temperature and representative fan
  state.
- If the shuttle still waits for exact temperature, increase the existing
  printer-wide deadband from 4 C total to 8 C total (target +/-4 C). Community
  reports for compact high-power TriangleLab-style hotends commonly use a
  +/-4-5 C `M109` window after PID tuning.
- This allows heater ramp-up to continue during the 5-6 s trip and reduces
  full-temperature travel without changing any pickup coordinate or command.

### Validation
- Slice a 40-60-change T0/T4 coupon and inspect the G-code footer before
  printing: machine tool-change time 0, preheat 12-14, ramming
  `0,0,0,0,0`, wipe `1,1,1,1,1`, and retract 5 for the first run.
- Success criteria: final temperature wait no more than 2 s, post-blocker strand
  no longer than 1 mm, no growing entry blob, and a continuous first tower
  line.
- The previously documented pickup override is not part of this plan and must
  not be applied under the current user constraint.

## 2026-07-29 - Clarification: eliminating the dock temperature pause

- Orca's `Ooze prevention -> Preheat time` is the available slicer control for
  eliminating the visible temperature pause without changing pickup G-code. It
  sends the next tool's non-blocking `M104` while the current tool is still
  printing.
- The current upstream pickup sequence explicitly executes `M109` before
  running the physical pickup path. Therefore no Orca setting can make this
  configuration release an under-temperature tool and finish heating during
  the dock-to-tower move. Preheat can make the `M109` condition already true,
  but the tool still leaves the dock at the accepted target window.
- The observed 2 s preheat plus approximately 13 s dock wait implies an initial
  local preheat value of approximately 15 s. Tune in 1 s increments:
  `new preheat = current preheat + observed dock wait`; subtract time when the
  tool reaches temperature early.
- Start at 15 s for the next short coupon. A 14 s setting is preferable if a
  near-zero one-second pause is acceptable and minimizing full-temperature
  dock dwell is more important.
- The active local process JSON currently contains 20 s. That value can remove
  waiting but starts heat roughly five seconds earlier than the measured need,
  increasing parked full-temperature dwell and residual pressure.
- A user whose tool visibly continues heating during descent either has a
  different pickup sequence, a wider heater wait window, or is observing
  temperature recovery after the wait threshold. That exact behavior is not
  selectable in the current Orca profile alone.

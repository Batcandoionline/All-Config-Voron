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

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

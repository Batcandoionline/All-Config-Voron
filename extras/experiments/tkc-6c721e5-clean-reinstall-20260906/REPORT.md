# TKC `6c721e5` clean reinstall and live deployment audit

## Scope and result

The previous TKC installation at `04431dfe575a717833c6966685ecdfac90c6568b` was removed from the physical printer, the clean state was checked, and the latest resolved upstream `main` was installed with the repository's updated installer.

- **Upstream:** [Tool-Klipper-Calibration at `6c721e5`](https://github.com/IDcrazy123/Tool-Klipper-Calibration/tree/6c721e5798184da1bf92445dbf345141b326ecc2)
- **Revision:** `6c721e5798184da1bf92445dbf345141b326ecc2`
- **Commit:** `fix(deploy): resolve 9 deployment audit defects for clean unattended installations`
- **Reported daemon version:** `0.8.19`
- **Printer:** `voron-local`, `192.168.1.43`
- **Source:** `/home/voron/Tool-Klipper-Calibration`, branch `main`, clean worktree
- **Environment:** `/home/voron/Tool-Klipper-Calibration/env`
- **Daemon:** enabled user service `tool_calibrator.service`, listening on `127.0.0.1:8090`
- **Update Manager:** current hash equals remote hash, zero commits behind, clean and valid

The final installation is operational for supervised camera testing. It applies no tool offsets, blocks TKC Z calibration, retains kTAMV for comparison, and keeps all machine-owned TKC `.cfg` paths under `Printer-Setup` as requested. No file in the upstream TKC checkout was modified.

## Backup and clean removal

Before changing any active configuration, the live printer configuration, Moonraker configuration, ASVC list, user service, source state, symlink inventory, service health, machine state, and old source working tree were backed up.

- Local backup: `extras/backups/pre-tkc-6c721e5-reinstall-20260906-203328/`
- Printer backup: `/home/voron/printer_data/config_backups/tkc-6c721e5-reinstall-20260906-203328/`

The upstream uninstaller was audited but was not run directly on the live configuration. It still executes `rm -rf` on the macro directory and archives `tool_offsets.cfg` before the user removes its active include. That behavior conflicts with this project's configuration-preservation rule and can leave Klipper with a missing include. The safe removal therefore performed the equivalent actions with ownership checks and moved every `.cfg` or `.cfg` symlink into the timestamped backup.

The removal checkpoint confirmed:

- old source and temporary preflight worktree absent;
- user unit absent and inactive;
- port 8090 closed while kTAMV remained active on port 8086;
- no TKC-owned Klipper extras or macro symlink;
- no TKC include, machine block, offset include, or Moonraker updater block;
- machine and offset `.cfg` files absent from active paths and present in the backup;
- after a Klipper configuration reload, no `tool_calibrator` object or TKC command was registered and Klipper returned ready.

A Klipper `RESTART` reloads configuration but does not terminate the Python host process, so it cannot prove that an imported module has left `sys.modules`. The later full `klipper.service` restart removed that ambiguity and loaded the new `6c721e5` module into a fresh process.

Evidence: [disk and service clean check](evidence/clean-verification-before-reload.txt), [clean Klipper objects and commands](evidence/clean-klipper-after-restart.jsonl), and [clean Moonraker state](evidence/clean-moonraker-after-restart.jsonl).

## What the new upstream revision fixes

The new revision materially improves deployment compared with `04431df`:

| Upstream change | Verification |
|---|---|
| Installer and uninstaller committed as executable | Both files are mode `100755`; direct `./scripts/install.sh` worked |
| Preflight tests venv capability instead of requiring `python3-pip` | The printer passed preflight without an apt or sudo package install |
| Explicit `--system-service` and `--user-service` modes | `--user-service` generated, enabled, and started a valid user unit |
| Safer removal of individual extras and `z_backends` links | Regular extras are no longer removed by the updated uninstaller |
| Creates an initial `tool_offsets.cfg` | A valid placeholder was created during the official install |
| Sync is called by `CALIBRATION_TEST_VISION` and registered on `klippy:ready` | Command-time sync worked; ready-time sync still fails as documented below |
| Dependency upper bounds | Major-version caps are present, though they remain too broad for reproducibility |
| `--keep-data` and timestamped offset archive | Present in the updated uninstaller |
| Expanded test suite | 101/101 tests passed on the Pi in 7.79 seconds |

The production venv intentionally contains runtime dependencies only, so the first attempt to run tests from that venv reported `No module named pytest`. Tests were rerun in a disposable test venv created from the exact revision. This should be made explicit in the development documentation or represented by a development requirements file.

## Official installer result

The exact command `./scripts/install.sh --user-service` completed with exit code zero. It created the source venv, extras links, macro links, placeholder offsets file, Update Manager block, and user service. Its dependency preflight and user-unit generation are corrected in this revision.

The installer then attempted these two commands in user mode:

```text
sudo systemctl restart moonraker.service || true
sudo systemctl restart klipper.service || true
```

Both failed because the deployment account has no noninteractive sudo. The script ignored both failures, checked only that the vision daemon process answered `/health`, and printed `CÀI ĐẶT HOÀN TẤT THÀNH CÔNG`. At that point Klipper had not loaded the new extras and Moonraker had not loaded the new updater block.

The health line also temporarily reported `6c721e5-dirty`. The installer performs its health check while `.install_manifest.txt` still exists inside the repository, then removes that journal after the check. The final worktree is clean, but the success message is confusing.

Evidence: [official installer output](evidence/official-installer-output.txt), [preflight tests](evidence/preflight-tests.txt), and [resolved packages](evidence/dependency-and-remote-check.txt).

## Machine-specific configuration layout

Upstream source and macros remain unchanged. The runtime macro symlinks and machine-owned data were organized under `Printer-Setup`:

```text
config/Printer-Setup/
├── tool-calibrator.cfg
├── tool_offsets.cfg
└── tool_calibrator/
    ├── tool_calibrator_macros.cfg -> upstream macro
    └── safe_staging_macros.cfg    -> upstream macro
```

`printer.cfg` now includes those three paths through `Printer-Setup`, and `offsets_config_path` points to `/home/voron/printer_data/config/Printer-Setup/tool_offsets.cfg`. The installer-generated root placeholder was preserved in the timestamped backup before the supervised station data was deployed.

The machine configuration keeps `safe_z` and `camera_target_z` at 40 mm, disables wiggle recovery, and routes both Z hooks to a deliberate error. `Printer-Setup/tool_offsets.cfg` contains only the camera station, MPP, and matrix; it has no `[tool_offsets]` section, so no X/Y/Z production offset is applied.

The upstream installer remains hard-coded to `config/tool_calibrator/` and `config/tool_offsets.cfg`. Re-running it will recreate those root paths alongside this machine layout. An upstream `--config-subdir` or `--offsets-path` option is recommended to support organized machine configurations without post-install relocation.

## Live validation

After the official installer finished, Moonraker and the full Klipper system service were restarted through Moonraker's service API. A normal `G28` completed, T0 became active and matched detected T0, and Z was raised to 40 mm before the camera move. No tool change, heating, Z calibration, or offset application was performed.

| Check | Result |
|---|---|
| Upstream tests | 101/101 passed in 7.79 seconds |
| Dependency integrity | `pip check`: no broken requirements |
| Source integrity | exact remote SHA, branch `main`, clean, not detached |
| Service | user unit enabled and active; port 8090 loopback only |
| Vision health after command-time sync | camera URL correct, MPP `0.023`, matrix solved, session unlocked |
| Update Manager | clean, current=remote `6c721e5`, behind=0, no warning/anomaly |
| No-op Update Manager request | accepted with `result=ok`; source and machine state unchanged |
| kTAMV | active on port 8086; no idle port or service-name conflict |

At the camera target `X170.910 Y18.917 Z40`, five consecutive stationary commands each requested five frames. All 25 frames were accepted.

| Run | Center UV (px) | Confidence | Dispersion |
|---:|---:|---:|---:|
| 1 | 639.40, 354.95 | 90.4% | 2.75 px / 0.0633 mm |
| 2 | 639.40, 354.95 | 99.0% | 0.20 px / 0.0046 mm |
| 3 | 639.45, 354.85 | 99.0% | 0.10 px / 0.0023 mm |
| 4 | 639.45, 354.85 | 99.0% | 0.20 px / 0.0046 mm |
| 5 | 639.45, 354.75 | 99.0% | 0.20 px / 0.0046 mm |

The first run remained inside the configured 0.08 mm physical spread gate. After returning to the bed center, a five-frame negative test correctly rejected the image as having no nozzle. A separate one-frame test at that off-camera position had previously accepted a small circular feature at U614.50/V270.45, radius 8.60 px and only 40% confidence. The burst gate prevents this instance at five frames, but the detector lacks a hard minimum-confidence and expected-radius/ROI gate.

After the expected negative vision error, the toolchanger was observed as `uninitialized` while the detection input still reported T0. `INITIALIZE_TOOLCHANGER` restored the correct active/detected T0 state without motion. This error-path state transition should be covered by an integration test.

Evidence: [service restart and ready-time result](evidence/full-klipper-service-restart-ready-sync.jsonl), [command-time sync](evidence/new-process-test-vision-sync.jsonl), [G28 and Z40](evidence/g28-z40.jsonl), [five camera runs](evidence/camera-station-five-runs.jsonl), [negative and false-positive check](evidence/off-camera-false-positive-check.jsonl), [Update Manager](evidence/update-manager-tool-calibrator.json), and [final live verification](evidence/final-live-verification.txt).

## Confirmed defects and proposed changes

### 1. User-mode install reports success without reloading Klipper or Moonraker

The user-mode branch still calls system-service restart commands through sudo and suppresses their failure. This leaves old Python modules cached and the Update Manager block unloaded while the installer reports success.

**Proposed change:** in user mode, restart the user daemon with `systemctl --user`; reload Moonraker and restart the Klipper system service through a configured Moonraker API, a privileged helper, or a clear required manual step. Treat a failed required reload as a partial install and print the exact unresolved actions. Verify the new TKC object and command from Moonraker before success.

### 2. `klippy:ready` synchronization uses a reactor operation that is disabled during ready

On a fresh Klipper process the ready handler logged:

```text
Could not contact vision service health: Internal error - reactor pause disabled
```

Health therefore remained on the default `/webcam2` URL with no MPP and no matrix after `klippy:ready`. The same synchronization function succeeded when called later by `CALIBRATION_TEST_VISION`.

**Proposed change:** schedule synchronization with `reactor.register_callback()` or a short timer after ready rather than calling the pause-based request directly inside the ready callback. Make sync failures visible at warning level for camera, MPP, and matrix operations, and add a real Klipper-reactor integration test.

### 3. Process health is presented as calibration readiness

The installer accepts `/health` when the daemon still has the default camera URL, no MPP, and no matrix. The endpoint returns `status=ok` in that state.

**Proposed change:** expose separate `process_ready`, `camera_ready`, `scale_ready`, and `matrix_ready` fields. The installer should validate a snapshot fetch and confirm the commit expected by the install. Its final result should distinguish daemon started, Klipper module loaded, camera usable, and calibration data loaded.

### 4. User-service updates cannot restart the user daemon

The generated Update Manager block correctly sets `is_system_service: False`, but `managed_services` contains only Klipper. A real source/venv update can complete while the existing user daemon continues running the old server code.

**Proposed change:** provide a supported user-service restart hook or helper and document it as mandatory. Report both the source commit and running daemon commit after update; block calibration when they differ.

### 5. The uninstaller can leave Klipper unstartable and is not layout-aware

The updated script archives root `tool_offsets.cfg` but leaves `[include tool_offsets.cfg]`, macro includes, and `[tool_calibrator]` for manual cleanup, then attempts a Klipper restart. It also removes the whole macro directory with `rm -rf`. With the requested `Printer-Setup` layout it does not discover the active offset file or macro path.

**Proposed change:** parse a persistent ownership manifest, remove or comment owned includes before archiving data, move rather than delete config artifacts by default, support custom config paths, perform a full service restart, and verify exact object/command absence before printing clean success.

### 6. The transactional rollback journal is incomplete

The new temporary manifest records created symlinks, one created offsets file, and a Moonraker backup. It does not preserve overwritten links, a removed legacy `z_backends` link, the created venv, created directories, ASVC edits, or service files. Rollback is performed in forward order, and the manifest is deleted after success so the uninstaller cannot use it.

**Proposed change:** preflight every collision; never overwrite an unowned path with `ln -sf`; record all mutations with previous state; roll back in reverse order; retain a versioned installation manifest for upgrade and uninstall ownership.

### 7. Single-frame detection can accept a low-confidence false positive

The off-camera one-frame request accepted a 40% confidence, 8.60 px-radius feature. The five-frame burst rejected the same scene.

**Proposed change:** enforce configurable minimum confidence, radius range, expected camera ROI, and minimum valid-frame ratio. Disallow one-frame measurements for commands that can lead to motion or saved offsets, and include the rejection reason in telemetry.

### 8. Error handling can invalidate toolchanger state

The negative camera test was followed by a toolchanger state of `uninitialized` even though T0 remained physically detected. Recovery required `INITIALIZE_TOOLCHANGER`.

**Proposed change:** preserve and restore the pre-command toolchanger state for no-motion diagnostics, or explicitly report that reinitialization is required. Test success and failure cleanup paths against the real toolchanger object.

### 9. Dependency bounds do not make deployments reproducible

The new caps resolved to Flask 3.0.3, Waitress 3.0.2, OpenCV 5.0.0.93, NumPy 2.4.6, Requests 2.34.2, and urllib3 2.7.0. Tests pass today, but future releases inside those broad major ranges can change image processing behavior without a TKC commit.

**Proposed change:** publish tested constraints or a lock per supported Python/platform combination, test minimum and maximum dependency sets, and expose resolved versions in diagnostics.

### 10. Release and documentation metadata remain ambiguous

The daemon still reports `0.8.19`, while Moonraker infers `v0.0.0-46` because there is no matching release tag. User-mode documentation still emphasizes system-service status/restart commands and ASVC behavior.

**Proposed change:** tag releases, derive the daemon version from package/release metadata, document user and system modes separately, and include an exact uninstall residue checklist for each mode.

## Recommended update procedure for this printer

Until the confirmed user-service and ready-callback issues are fixed upstream:

1. Confirm standby state, active/detected tool agreement, heater targets zero, and no active TKC session.
2. Back up `Printer-Setup/tool-calibrator.cfg`, `Printer-Setup/tool_offsets.cfg`, `printer.cfg`, `moonraker.conf`, and the user unit.
3. Update `tool_calibrator` through Moonraker Update Manager.
4. Run `systemctl --user restart tool_calibrator.service` so the daemon uses the updated source and venv.
5. Restart the **Klipper system service** through Moonraker. A G-code `RESTART` is insufficient for changed Python extras.
6. Move any installer-created root macro links and offset placeholder back into the machine's `Printer-Setup` layout, or remove the duplicate placeholder after preserving it.
7. With the nozzle at the camera target and Z=40, run `CALIBRATION_TEST_VISION SAMPLES=5`. This currently performs the post-ready camera/MPP/matrix sync.
8. Verify daemon commit equals Update Manager hash, health shows the real camera plus MPP/matrix, source is clean, and the negative off-camera burst is rejected.

Keep Z calibration blocked and keep `[tool_offsets]` absent until separate attended XY ownership/sign tests and Cartographer Z acceptance tests are completed.

## Final printer state

At completion the printer was standby with XYZ homed, T0 active and matching detected T0, `X175.8 Y168.0 Z40.0`, and every hotend and bed target at zero. TKC was active on loopback port 8090 with commit `6c721e5`, camera URL `http://127.0.0.1:8080/snapshot.jpg`, MPP `0.023`, and matrix loaded. kTAMV remained active on port 8086.

No TKC upstream source, macro, installer, uninstaller, test, or documentation file was changed.

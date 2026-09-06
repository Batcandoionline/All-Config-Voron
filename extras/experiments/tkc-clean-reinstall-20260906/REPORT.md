# TKC 0.8.19 clean reinstall and deployment audit

## Scope and conclusion

The previous manually patched TKC trial was fully removed from active paths on the physical printer, the clean state was verified, and the current upstream `main` revision was installed without modifying TKC source code.

- **Upstream:** [Tool-Klipper-Calibration at `04431df`](https://github.com/IDcrazy123/Tool-Klipper-Calibration/tree/04431dfe575a717833c6966685ecdfac90c6568b)
- **Reported version:** `0.8.19`
- **Resolved revision:** `04431dfe575a717833c6966685ecdfac90c6568b`
- **Printer:** `voron-local`, `192.168.1.43`
- **Source:** `/home/voron/Tool-Klipper-Calibration`, branch `main`, clean worktree
- **Environment:** `/home/voron/Tool-Klipper-Calibration/env`
- **Daemon:** user service `tool_calibrator.service`, loopback `127.0.0.1:8090`
- **Camera:** `http://127.0.0.1:8080/snapshot.jpg`
- **Update Manager:** registered, current hash equals remote hash, zero commits behind, no warnings or anomalies

The repository installer could not complete under the available SSH account. The resulting installation follows the latest repository layout for source, environment, Klipper extras, macros, and Moonraker metadata, with a documented user-service adaptation. A standard system-service install still requires one administrative setup step or upstream support for user services.

## Clean uninstall evidence

Before any configuration change, the live `printer.cfg`, `moonraker.conf`, `moonraker.asvc`, old service, old station data, source patch, symlink inventory, runtime objects, and service health were copied to timestamped local and printer backups.

The previous installation used `tool-calibrator-experiment.service`, `/home/voron/tkc-env`, an experimental include, and Klipper extras linked to a patched `b6c3328` worktree. Removal performed the following actions:

1. Stopped and disabled the old user service and removed its enablement link.
2. Removed the exact experimental include from live `printer.cfg`.
3. Unlinked only the confirmed TKC Klipper extras.
4. Moved `/home/voron/printer_data/tkc-experiment` into the timestamped backup.
5. Removed the old source tree, old venv, and temporary preflight worktree after preserving the revision and binary patch.
6. Restarted the Klipper process through Moonraker.

The active-path audit then confirmed all old source, venv, service, runtime-config, macro, and extras paths absent; port 8090 closed; no TKC process; no active configuration reference; and no exact TKC object or command in Klipper. The first broad command-name scan matched unrelated production commands such as `CALIBRATION_STATUS`; [the exact follow-up](evidence/clean-runtime-exact.txt) confirmed TKC runtime commands were absent. Klipper was ready with a new process, while `ktamv-server.service` and port 8086 remained active.

Evidence: [clean-verification.txt](evidence/clean-verification.txt), [clean-runtime-exact.txt](evidence/clean-runtime-exact.txt), [clean-printer-info.json](evidence/clean-printer-info.json), and [clean-objects-list.json](evidence/clean-objects-list.json).

## Reference installer result

Two attempts reproduced the installation guide exactly enough to locate the blockers before deployment:

| Attempt | Result | Evidence |
|---|---|---|
| `./scripts/install.sh` after a clean clone | Exit `126`: permission denied | [install-official-attempt.txt](evidence/install-official-attempt.txt) |
| `bash ./scripts/install.sh` | Exit `1`: missing Debian package `python3-pip`, followed by a `sudo` password/TTY failure | [install-official-attempt-2.txt](evidence/install-official-attempt-2.txt) |

Both scripts are committed with mode `100644`. The guide's `chmod +x scripts/install.sh scripts/uninstall.sh` makes both tracked files dirty on Linux, which conflicts with clean Moonraker git update management. This was reproduced in a disposable clone and did not modify the installed source. See [executable-mode-audit.txt](evidence/executable-mode-audit.txt).

The host already had `python3-venv` and a working `ensurepip`; `python3 -m venv env` succeeded without the system `python3-pip` package. Treating that package as mandatory caused an avoidable privilege request before the installer could do useful work.

## Installed layout and local adaptation

The latest upstream source was cloned again and verified at the resolved SHA. The venv was created at the upstream path and dependencies were installed directly from `server/requirements.txt`. All 100 upstream tests passed in this clean environment, and `pip check` found no broken requirements.

The official Klipper extras and macro symlink layout was created. The initial user-service conversion of the upstream system-service template failed with `status=216/GROUP` because `User=voron` is invalid in this user manager. The deployed unit removes `User=`, uses `WantedBy=default.target`, and supplies `--camera-url` plus the known `--mpp` at startup. These are deployment settings; the upstream repository remains byte-clean.

Moonraker is configured with `is_system_service: False` and `managed_services: klipper`. This gives a valid, clean Update Manager entry and dependency updates without falsely claiming that Moonraker can control the user daemon. The `moonraker.asvc` file was therefore not given a nonfunctional `tool_calibrator` entry.

The production configuration loads both upstream macro files, a machine-specific `[tool_calibrator]` block, and `tool_offsets.cfg`. Camera station data from the successful supervised trial was migrated. It contains no `[tool_offsets]` section, so no X/Y/Z tool offset is applied. Safe Z is 40 mm, motion speeds are 1800/600/600 mm/min (30/10/10 mm/s after the upstream normalization), wiggle recovery is disabled, and both Cartographer Z hooks deliberately raise an error until Z is validated.

kTAMV remains active on `0.0.0.0:8086`. TKC listens only on `127.0.0.1:8090`; there is no port, source, venv, service-name, or Klipper-object conflict at idle.

## Validation on the printer

| Check | Result |
|---|---|
| Upstream unit tests | 100/100 passed in 6.890 seconds in the new venv |
| Source integrity | branch `main`, exact SHA, clean, not detached |
| Python environment | `pip check`: no broken requirements |
| Vision health | `status=ok`, service identity correct, version `0.8.19`, commit `04431df` |
| Update Manager | current=remote exact SHA, dirty=false, detached=false, behind=0, no warnings/anomalies |
| Klipper | ready; TKC object, camera station, core commands, and convenience macros loaded |
| Camera smoke test | 5/5 frames; U639.95/V360.05 px; radius 22.30 px; confidence 99.0%; dispersion 0.00 px |
| No-motion property | reported position and detected tool were unchanged across the camera smoke test |
| No-op update request | accepted with `result=ok`; source stayed at the same clean SHA |
| kTAMV | user service active; port 8086 active |

After the process restarts, the operator-authorized normal `G28` completed, T0 became active and matched detected T0, and Z was moved to 40 mm. Final state was standby, XYZ homed, `X175.8 Y168.0 Z40.0`, T0 active/detected, all heater targets zero, TKC `IDLE`, and both TKC and kTAMV services active.

Evidence: [final checks](evidence/final/checks.txt), [machine state](evidence/final/final-machine-state.json), [health](evidence/final/health.json), [Update Manager state](evidence/final/update-status.json), [service journal](evidence/final/tool-calibrator-journal.txt), [dependency list](evidence/final/python-packages.txt), [test output](evidence/latest-venv-tests.txt), [vision console](evidence/vision-test-gcode-store.json), and [no-op update](evidence/final/noop-update-test.txt).

## Confirmed defects and proposed changes

### 1. Scripts are not executable, and the documented workaround dirties the repo

`install.sh` and `uninstall.sh` are stored as `100644`. Direct execution fails, while `chmod +x` produces tracked mode changes that Moonraker reports as a dirty repository.

**Proposed change:** commit both scripts with mode `100755`; remove the mandatory chmod step; add a CI assertion for executable modes and `bash -n`.

### 2. The dependency preflight requests unnecessary administrator access

The installer requires the Debian `python3-pip` package even when `python3-venv` can create a venv containing pip. On this printer, the requirement forced `sudo` and stopped the install, while direct venv creation worked.

**Proposed change:** test `python3 -m venv` and the new venv's pip first. Install only the packages that are actually missing. Run all privilege and platform checks before creating links or changing Moonraker files, and provide a clear noninteractive failure message.

### 3. Installation is not transactional

The script creates the venv, extras links, macro links, ASVC entry, and Update Manager block before the system unit is installed. A late sudo or service failure leaves a partial installation without automatic rollback.

**Proposed change:** preflight `sudo`, paths, ports, collisions, camera reachability, and service names before mutation. Record an ownership manifest, stage configuration in temporary files, and use an error trap to restore timestamped backups.

### 4. Legacy and third-party `z_backends` paths can be corrupted or deleted

The installer runs `mkdir -p` followed by `ln -sf` inside `klippy/extras/z_backends`. A legacy whole-directory symlink can make those targets resolve back into the source tree. The uninstaller then executes `rm -rf` on the whole directory. It also removes matching regular extras files, not only links owned by TKC.

**Proposed change:** reject a symlinked `z_backends` directory unless it points to the expected managed layout; create and remove only a manifest of links owned by this installation; never delete real files or an entire shared directory; back up collisions and stop for operator review.

### 5. Health passes while the configured camera path is unusable

Immediately after a fresh daemon start, `/health` returned `ok` with the default `/webcam2` URL, no MPP, and no matrix. The first `CALIBRATION_TEST_VISION` then failed after five HTTP 502 camera reads. That command does not call `_ensure_vision_sync()`. Adding the real camera URL and MPP to the deployed service made the same stationary test pass 5/5.

**Proposed change:** call `_ensure_vision_sync()` at the start of `cmd_CALIBRATION_TEST_VISION`; optionally synchronize on Klipper ready. Extend readiness reporting to distinguish process health from camera readiness and calibration readiness. Make the installer perform a real snapshot decode or a non-motion vision smoke test when a camera URL is configured.

### 6. The documented `tool_offsets.cfg` include can point to a nonexistent file

The guide tells users to include `tool_offsets.cfg`, but the installer does not create it. A fresh user who follows that step before a teach/save command gets a Klipper include error. The sample header still shows a tilde include even though the corrected guide states that Klipper includes do not expand `~`.

**Proposed change:** create an empty, valid station/offset file during installation, or instruct users to omit the include until TKC creates the file. Use one consistent relative include in every sample and final installer message.

### 7. System-service-only automation has no supported fallback

The reference installer and uninstaller require sudo for `/etc/systemd/system`. On this machine, a user service works and survives restarts, but Moonraker cannot restart it after a source update. The no-op update endpoint passed; a future real update still requires `systemctl --user restart tool_calibrator.service` before the daemon uses new Python code.

**Proposed change:** provide explicit `--system-service` and `--user-service` modes. For user mode, generate a unit without `User=`, use `default.target`, configure Update Manager without false system-service management, and supply a supported post-update restart path. Keep the system-service mode as the preferred fully automated option when one-time sudo is available.

### 8. Fresh installations are not dependency-reproducible

The unbounded `opencv-python-headless>=4.5.5` and `numpy>=1.21.0` constraints installed OpenCV `5.0.0.93` and NumPy `2.4.6`. All current tests passed, but a later release can change behavior without a TKC commit.

**Proposed change:** publish tested upper bounds or a constraints file per supported Python/platform combination; record resolved package versions in health or diagnostics; test the minimum and maximum supported dependency sets in CI.

### 9. “Clean uninstall” does not fully describe or reverse all installed state

The upstream uninstaller leaves the repository, printer includes, machine-specific `[tool_calibrator]`, and `tool_offsets.cfg` for manual cleanup. It cannot remove the earlier user-service/alternate-venv layout, and its broad deletion behavior is unsafe for shared paths.

**Proposed change:** use the installation manifest, support `--keep-data`, archive configuration instead of deleting it by default, verify exact service/process/port/config/object state after restart, and report residual user actions explicitly instead of always printing clean success.

## Update recommendation for this printer

The current deployment is suitable for supervised, no-offset TKC evaluation. Until upstream supports user-service restart integration, use this sequence for a real update:

1. Confirm the printer is standby and no calibration run is active.
2. Use Moonraker Update Manager to update `tool_calibrator`.
3. Run `systemctl --user restart tool_calibrator.service`.
4. Restart the Klipper service through Moonraker so symlinked extras are imported by a fresh process.
5. Verify `/health` reports the expected commit and camera URL, run `pip check`, confirm Update Manager is clean, and execute the stationary vision test before any calibration motion.

For fully automatic one-click updates, perform a one-time administrative installation of the upstream system unit after the script issues above are fixed. Keep Z disabled and do not include a generated `[tool_offsets]` section until separate XY sign, offset ownership, and Cartographer Z acceptance tests pass.

## Source-change statement

No TKC source, macro, installer, uninstaller, test, or documentation file was modified. The live upstream worktree is clean at the exact remote SHA. Changes in this repository are limited to machine configuration, timestamped backups, evidence, this report, and the daily maintenance log.

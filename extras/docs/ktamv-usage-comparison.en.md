# kTAMV usage and method comparison

[English](ktamv-usage-comparison.en.md) | [Tiếng Việt](ktamv-usage-comparison.vi.md)

This guide describes the kTAMV integration installed on the five-tool Voron on
2026-08-31 and compares its operator workflow with the retired ToolVision
integration. The reviewed upstream is [TypQxQ/kTAMV](https://github.com/TypQxQ/kTAMV)
at commit `72421f2d54da0de8701c4f84449c6e6b7d060301`. That commit is still upstream
`main`/HEAD and dates from 2024-04-02.

## Current installation

| Item | Value |
| --- | --- |
| Source | `/home/voron/kTAMV` at reviewed commit `72421f2` |
| Local fix | `config/scripts/patches/ktamv-multi-object-selection.patch` |
| Python | `/home/voron/ktamv-env`, with system OpenCV packages |
| Service | user unit `ktamv-server.service` |
| Server | `http://192.168.1.43:8086/` |
| Processed image | `http://192.168.1.43:8086/image` |
| Source camera | `http://127.0.0.1/webcam/?action=snapshot` |
| Klipper config | `config/Printer-Setup/ktamv.cfg` |
| Cloud upload | `false` |
| Old ToolVision unit | Disabled/removed and followed by `daemon-reload` with sudo |

The upstream installer was deliberately not executed. It changes system time,
runs system-wide `apt`, writes an invalid Moonraker header with an extra `]`,
modifies active printer configuration and restarts services. This machine uses
a pinned manual install and a user service instead.

The user-owned ToolVision runtime, venv, links, generated data and logs were
removed. The old root-owned unit was also removed with the following bounded
commands:

```bash
sudo systemctl disable --now tool-vision.service
sudo rm -f /etc/systemd/system/tool-vision.service
sudo systemctl daemon-reload
```

## What kTAMV actually does

kTAMV consists of a Klipper extension and a Flask/Waitress image server. The
server resizes each camera frame to 640×480 and tries five fixed OpenCV
preprocessor/detector combinations. A nozzle position must repeat three times
within `detection_tolerance`; the configured value is zero pixels.

Camera calibration samples ten approximately 0.5 mm points around the starting
position. It needs at least 75% valid samples, filters mm/pixel outliers and
builds a camera-to-printer transform. Centering then detects the nozzle and jogs
X/Y until the computed correction is zero.

Important source observations:

- kTAMV only measures X and Y; it has no Z workflow.
- Camera calibration, transform and origin exist only in RAM.
- `KTAMV_GET_OFFSET` reports `raw current XY - raw origin XY` and does not save.
- `calib_iterations` and `calib_value` are read from config but are not used by
  the reviewed command path.
- `move_speed` is exposed as `printer.ktamv.travel_speed` for macros, but native
  calibration moves use the utility default `F3000` and native centering uses
  `F1000`.
- The README names `KTAMV_MOVE_TO_ORIGIN`, but the reviewed Python does not
  register that command. The repository only supplies a separate example macro,
  which this machine does not include.

## Command safety classification

### No intentional printer motion

| Command | Effect |
| --- | --- |
| `KTAMV_SETUP` / `KTAMV_SEND_SERVER_CFG` | Send camera URL and detector options to the server |
| `KTAMV_STATUS` | Report calibrated state, mm/pixel and origin |
| `KTAMV_START_PREVIEW` / `KTAMV_STOP_PREVIEW` | Start/stop image processing preview |
| `KTAMV_SIMPLE_NOZZLE_POSITION` | Detect and report the nozzle pixel position |
| `KTAMV_SET_ORIGIN` | Store current raw X/Y as the reference |
| `KTAMV_GET_OFFSET` | Report current raw X/Y minus the stored origin |

### Moves the printer

| Command | Motion |
| --- | --- |
| `KTAMV_CALIB_CAMERA` | Ten small X/Y calibration moves and a possible final centering move |
| `KTAMV_FIND_NOZZLE_CENTER` | Repeated X/Y corrections; may wiggle 0.1–0.2 mm after detection loss |

Both moving commands require X/Y/Z to be homed. They must be run only with an
operator at the printer, the camera and cable secure, all dock paths clear and
an emergency stop ready. A failure does not guarantee exact return to the
starting coordinate.

No G-code, homing, toolchange, heating or movement command was sent during the
2026-08-31 installation. The physical tool was intentionally left above the
camera.

## Manual comparison workflow

Do not start this sequence merely because installation checks pass. First clean
the nozzle, use soft even lighting, focus on the nozzle hole and keep enough
frame margin for the 0.5 mm pattern.

1. While the machine is idle and attended, home through the normal machine
   workflow and select T0 with X/Y offsets equal to zero.
2. Move T0 near the camera center at a safe Z, then run the non-motion setup,
   preview and simple detection commands.
3. Stop preview and run `KTAMV_CALIB_CAMERA`. Continue only when
   `KTAMV_STATUS` reports calibrated with a valid mm/pixel value.
4. Run `KTAMV_FIND_NOZZLE_CENTER`, then `KTAMV_SET_ORIGIN` exactly once for T0.
5. For each T1–T4, select the tool through KTC, move it close to the same focus
   plane, verify with simple detection, center it and run `KTAMV_GET_OFFSET`.
6. Repeat at least three times per tool. Record raw readings and compare signs
   with the loaded offsets; never run `KTAMV_SET_ORIGIN` for T1–T4.
7. Do not modify production X/Y from one result. Z values are out of scope and
   must remain unchanged.

## kTAMV versus retired ToolVision

| Area | kTAMV | Retired ToolVision integration |
| --- | --- | --- |
| Axes | X/Y only | X/Y plus switch or Cartographer Touch Z |
| Image model | Fixed 640×480 OpenCV pipelines | Native-resolution learned profile with ambiguity checks |
| Operator flow | Manual command-by-command | Guided setup and integrated five-tool batches |
| Persistence | None across Klipper restart | State, latest result and history on disk |
| Statistics | Single observations; operator repeats/records | Batch attempts and per-tool statistics |
| Apply behavior | Reports only | Configured report-only on this printer |
| Recovery | Limited; native commands may leave a shifted position | KTC restore verification and cleanup evidence |
| Updates | Pinned/manual because of a local patch | Previously managed by Moonraker |

The comparison is not a claim that one detector is universally better. On this
specific MF-500 setup, both systems saw ambiguous reflective features. The
2026-08-22 kTAMV calibration accepted only six of ten points; its processed
marker sat on a bright reflection below the actual nozzle hole, and one accepted
scale (`0.028`) was an outlier from the `0.041–0.044` cluster. ToolVision also
rejected the scene as multiple nozzle-like objects. Improve the optical scene
before any new attended motion test.

## Processed image in Mainsail

Add a separate webcam entry if desired:

- name: `kTAMV Processed`;
- stream URL: empty;
- snapshot URL: `http://192.168.1.43:8086/image`;
- service: Adaptive MJPEG-Streamer;
- target FPS: 2–4.

Use the printer IP, not `localhost`, because Mainsail resolves the URL in the
browser. This view is detector output and does not replace the original MF-500
camera entry.

## Non-motion verification and troubleshooting

Host checks:

```bash
systemctl --user status ktamv-server
journalctl --user -u ktamv-server -n 100 --no-pager
curl --fail http://127.0.0.1:8086/
```

After Klipper loads the config, `KTAMV_STATUS`, `CALIBRATION_STATUS` and
`CHECK_OFFSETS` are non-motion checks. `Camera URL not set` is resolved by
`KTAMV_SETUP`. `No nozzle found` requires optical correction, not blindly
raising tolerance. More than 25% failed camera points is a hard stop: do not
continue to centering or offset collection.

Restarting Klipper clears calibration and origin by design. The runtime has no
automatic persistence or offset writeback.

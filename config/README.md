# Active Klipper configuration payload

[English](README.md) | [Tiếng Việt](README.vi.md)

This directory is deployed to `~/printer_data/config` by `scripts/install.sh`
and `scripts/update.sh`. Markdown files are documentation only and are excluded
from deployment.

## Ownership and include contract

`printer.cfg` currently loads:

```ini
[include mainsail.cfg]
[include toolchanger/readonly-configs/toolchanger-include.cfg]
[include Printer-Setup/calibration-probe.cfg]
[include Printer-Setup/tool-vision.cfg]
[include Printer-Setup/hardware.cfg]
[include Printer-Setup/fans-leds.cfg]
[include Printer-Setup/input-shaper.cfg]
[include Printer-Setup/nozzle-clean.cfg]
[include Printer-Setup/prime-lines.cfg]
[include Printer-Setup/print-macros.cfg]
[include Printer-Setup/tool-crash.cfg]
```

KTC-Easy owns every file under `toolchanger/readonly-configs/`. Do not edit,
replace or copy regular files into that directory. All-Config owns
`toolchanger/toolchanger-config.cfg`, `toolchanger/tools/T*.cfg` and the
`Printer-Setup/` overrides.

## Directory map

```text
config/
├── printer.cfg
├── mainsail.cfg
├── moonraker.conf
├── crowsnest.conf
├── KlipperScreen.conf
├── Printer-Setup/
│   ├── calibration-probe.cfg
│   ├── tool-vision.cfg
│   ├── hardware.cfg
│   ├── fans-leds.cfg
│   ├── input-shaper.cfg
│   ├── nozzle-clean.cfg
│   ├── prime-lines.cfg
│   ├── print-macros.cfg
│   └── tool-crash.cfg
├── toolchanger/
│   ├── toolchanger-config.cfg
│   ├── tools/T0.cfg ... T4.cfg
│   └── readonly-configs/       # KTC-Easy-owned symlinks
└── scripts/
    ├── install.sh
    ├── update.sh
    ├── cleanup-voron.sh
    └── patches/
```

## Source-verified hardware map

| Component | Active value |
| --- | --- |
| Main MCU | Manta M8P V2.0, CAN UUID `19b203d75137` |
| Cartographer | CAN UUID `da13d909ce34`, offsets X `0`, Y `35` |
| X/Y endstops | `PF0` / `PF1`; Y minimum `-10` |
| Z step pins | `PG9`, `PB4`, `PG13`, `PB8` |
| Bed | heater `PA1`, sensor `PB0`, maximum 120 °C |
| Chamber sensor | Generic 3950 on `PB1` |
| Under-bed fan | `PF8` |
| Chamber LEDs | WS2812 on `PD15` |
| ToolVision switch | Manta `^PF2` with GND |

The five tool CAN UUIDs, docks and production offsets are documented in the
[root README](../README.md) and defined in `toolchanger/tools/` plus the
`SAVE_CONFIG` block in `printer.cfg`.

## Calibration ownership

- Cartographer Touch provides production Z homing.
- Cartographer Scan provides the adaptive bed mesh. The configured mesh spans
  X `20..320`, Y `45..325` at 55 × 55 samples.
- ToolVision is loaded from `Printer-Setup/tool-vision.cfg`. It is report-only
  and uses PF2 for the physical-switch method.
- Axiscope and `[tools_calibrate]` are commented rollback material in
  `calibration-probe.cfg`, not active backends.
- ToolVision camera XY is not configured by this repository; it becomes ready
  only after an attended camera setup.

Generated ToolVision state/result files are explicitly routed to:

```text
Generated-Data/ToolVision/state.json
Generated-Data/ToolVision/results.json
```

The entire `Generated-Data/` tree is excluded from Git deployment and from
`rsync --delete`.

## Deployment behavior

First install without a persistent All-Config checkout:

```bash
tmp_dir="$(mktemp -d /tmp/all-config-voron.XXXXXX)"
curl -fsSL https://github.com/IDcrazy123/All-Config-Voron/archive/refs/heads/main.tar.gz \
  | tar -xz -C "${tmp_dir}" --strip-components=1
bash "${tmp_dir}/config/scripts/install.sh"
rm -rf -- "${tmp_dir}"
sudo systemctl restart moonraker klipper
```

Update an existing deployment:

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart moonraker klipper
```

`install.sh` performs these checks before deployment:

1. All six KTC-Easy readonly entries are valid symlinks with existing targets.
2. If the ToolVision include is active, the ToolVision checkout, isolated
   Python, systemd unit and five exact Klipper module symlinks exist.
3. The installed `tool_crash.py` is already patched or exactly matches the
   reviewed patch preimage.
4. A timestamped snapshot is created under
   `~/printer_data/config_backups/config-install-YYYYMMDD-HHMMSS/`.

Deployment excludes Markdown, `Generated-Data/`, downloaded snapshots, local
diagnostics, legacy ToolVision JSON and `toolchanger/readonly-configs/`. The
scripts do not restart services.

`cleanup-voron.sh` lists legacy cleanup candidates by default. `--apply` only
removes the displayed `config.update-backup-*`, `config.backup-*` and
`~/axiscope.bak` targets after strict path checks. It does not prune normal
`config_backups/` snapshots.

## Safe validation

After a documentation-only change, no printer action is required. After a
configuration deployment while the printer is idle:

```text
CALIBRATION_STATUS
QUERY_ENDSTOPS
TOOL_VISION_STATUS
```

These commands do not intentionally home, probe or select a tool. Opening the
`TOOL_VISION` macro only opens its panel; Setup and Calibrate actions can move
and heat the machine.

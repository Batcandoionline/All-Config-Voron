# TKC 0.8.19 clean reinstall

The physical printer at `192.168.1.43` now runs unmodified upstream revision `04431dfe575a717833c6966685ecdfac90c6568b` on branch `main`. See [REPORT.md](REPORT.md) for the uninstall proof, installation differences, validation results, defects, and proposed upstream changes.

The deployment uses a user service because the SSH account cannot perform noninteractive `sudo`. Moonraker Update Manager can fetch source and Python dependencies, but it cannot restart that user service. Restart it after a real update with:

```sh
systemctl --user restart tool_calibrator.service
```

TKC Z calibration remains blocked pending a separate supervised Cartographer validation. The installed `tool_offsets.cfg` contains camera station geometry only and does not apply any tool offsets. kTAMV remains installed and active on its separate port.

Evidence is retained in [evidence](evidence/). The pre-change configuration is preserved in `extras/backups/pre-clean-reinstall-tkc-20260906-195259/` and on the printer at `/home/voron/printer_data/config_backups/tkc-clean-reinstall-20260906-195259/`.

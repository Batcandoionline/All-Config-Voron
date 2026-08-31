# Pre-change backup: kTAMV repeated XY averaging and application

- Created: 2026-08-31 13:49:48 Asia/Saigon
- Scope: repository-owned printer configuration files that may be changed while
  removing the final active-config ToolVision reference, adding a three-sample
  kTAMV XY command, and applying measured X/Y tool offsets.
- Live-machine backup:
  `/home/voron/printer_data/config_backups/pre-ktamv-average-apply-20260831-134948/`
- Z offsets are outside this change and must remain unchanged.

## SHA-256

```text
169b37cf75fd7bc5e1f92a135da707f56c97ff02d998e2f0d01b85407de904c0  config/Printer-Setup/calibration-probe.cfg
45f1946f5a569381e984c4212f509aa331885b96d1052af5291661342f54c736  config/Printer-Setup/ktamv.cfg
3521db1250f1ee3434aae16c00ec8009baf542e259ffc4883e105b38999b5ede  config/printer.cfg
f34fdf98f671564b51a350a91ba244960000527bf330260872b52e4d79cb68c5  config/scripts/install.sh
f8b33fa4f757d931990d6f5cd1d819fe73c3a2433d1ef2d48eb660383e7273b4  config/toolchanger/toolchanger-config.cfg
```

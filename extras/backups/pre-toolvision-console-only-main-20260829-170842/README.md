# Backup record

- **Date:** 2026-08-29 17:08:42 +07:00
- **Purpose:** Deploy the console-only ToolVision macro surface from ToolVision
  `main` and return the live Moonraker updater to `primary_branch: main`.
- **Previous runtime HEAD:**
  `ba424a3dbec5af55d9c0e579a3b3c3fe3e187cdf`.
- **Target ToolVision main HEAD:**
  `374d5e22db393c74f91706791727771f9413547e`.
- **Target feature commit:**
  `25fe4bec56fbbcb42d127d85e64d565255239f50`.
- **Main CI:**
  `https://github.com/IDcrazy123/Tool-Vision/actions/runs/33247017779`.
- **Files:**
  - `tool-vision.cfg` — previous repository/live macro configuration;
  - `moonraker-live.conf` — previous live Moonraker configuration, whose
    ToolVision updater still tracked `codex/compact-mainsail-output`.
- **SHA-256:**
  - `tool-vision.cfg`:
    `051A61E5F52EAB16B840DC221C3AB0C59E8E99391FC1428F37C6350873C41F5B`;
  - `moonraker-live.conf`:
    `D023D1D270323D7C29B844D5BA80D2EFF5C4CAD64450405487CCB5F48CB18531`.
- **Remote backup:**
  `/home/voron/printer_data/config_backups/tool-vision/pre-console-only-main-20260829-170842/`.
- **Related journal:**
  `extras/Nhat-ky-chinh-sua/2026-08-29-session-updates.md`.

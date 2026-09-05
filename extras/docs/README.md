# Documentation index and language policy

[English](README.md) | [Tiếng Việt](README.vi.md)

This index separates current documentation from immutable evidence. Current
owned guides are maintained as English/Vietnamese pairs. Historical journals,
backup snapshots and downloaded machine snapshots preserve what was recorded at
their date; rewriting them would destroy rollback/audit meaning.

Source-review baseline for this documentation pass: current production config,
the full repository Markdown corpus and kTAMV upstream commit `72421f2`, reviewed
on 2026-08-31.

## Current documentation

| Topic | English | Vietnamese |
| --- | --- | --- |
| Project/system overview | [README](../../README.md) | [README](../../README.vi.md) |
| Active config payload | [README](../../config/README.md) | [README](../../config/README.vi.md) |
| OrcaSlicer sync/profiles | [README](../../Orca%20Config/README.md) | [README](../../Orca%20Config/README.vi.md) |
| StealthChanger operation | [Guide](huong-dan-he-thong-stealthchanger.en.md) | [Guide](huong-dan-he-thong-stealthchanger.md) |
| kTAMV usage and method comparison | [Guide](ktamv-usage-comparison.en.md) | [Guide](ktamv-usage-comparison.vi.md) |
| TEST_SPEED & Input Shaper Evaluation (2026-09-04) | — | [Report (vi)](danh-gia-input-shaper-va-test-speed-2026-09-04.md) |
| Mainsail 1-Click Update & 51-file cross-check (2026-09-04) | — | [Guide (vi)](danh-sach-doi-chieu-va-huong-dan-update-mainsail.md) |

## Historical and retired material

- `extras/Nhat-ky-chinh-sua/`: append-only engineering history. Existing entries
  are not translated or modernized after the fact. New current documentation
  above supplies bilingual navigation and present-state descriptions.
- [`axiscope-cartographer/`](../axiscope-cartographer/README.md): inactive local
  fork evidence retained for rollback/reference. Its local status is summarized
  bilingually in [`FORK_INFO.md`](../axiscope-cartographer/FORK_INFO.md).
- [`retired-configs/2026-08-20-config-merge/`](../retired-configs/2026-08-20-config-merge/README.md):
  files no longer included by `printer.cfg`; README contains both languages.
- [`retired-configs/2026-08-31-toolvision-removal/`](../retired-configs/2026-08-31-toolvision-removal/README.md):
  the final machine ToolVision CFG retained byte-for-byte after kTAMV cutover.
- **ToolVision docs & proposals:** All retired ToolVision integration guides and proposal drafts
  were removed from `docs/` to eliminate stale or conflicting configuration instructions; historical
  snapshots are preserved in Git and backup [`pre-replace-toolvision-with-ktamv-20260831-113047`](../backups/pre-replace-toolvision-with-ktamv-20260831-113047/README.md).
- `extras/Config download/`: downloaded printer snapshots. They are not current
  repository documentation and are not edited.

## Recent tracked rollback snapshots

Only links and current context are added here; snapshot contents remain
immutable.

1. [`pre-replace-toolvision-with-ktamv-20260831-113047`](../backups/pre-replace-toolvision-with-ktamv-20260831-113047/README.md) — before removing the active ToolVision integration and installing pinned kTAMV.
2. [`pre-move-toolvision-to-printer-setup-20260823-220605`](../backups/pre-move-toolvision-to-printer-setup-20260823-220605/README.md) — before moving the machine ToolVision config into `Printer-Setup/` and routing JSON under `Generated-Data/ToolVision/`.
3. [`pre-toolvision-z-canary-20260823-211530`](../backups/pre-toolvision-z-canary-20260823-211530/README.md) — before enabling the PF2 report-only ToolVision canary.

These are repository-tracked snapshots, not a statement about which directories
currently exist on the CM4. Printer-side retention actions remain recorded in
their dated immutable journals.

## Rules for future documentation changes

1. Read the loaded config and scripts before changing current-state claims.
2. Label facts as active, observed, development/planned or unknown.
3. Update both language companions in the same commit.
4. Do not translate a plan into an implemented claim.
5. Do not rewrite old journals, backup READMEs or downloaded snapshots; add a
   new current guide/index entry instead.
6. When code, path or macro behavior changes, update the affected current pair
   and the daily journal together.

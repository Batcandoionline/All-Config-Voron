# Documentation index and language policy

[English](README.md) | [Tiếng Việt](README.vi.md)

This index separates current documentation from immutable evidence. Current
owned guides are maintained as English/Vietnamese pairs. Historical journals,
backup snapshots and downloaded machine snapshots preserve what was recorded at
their date; rewriting them would destroy rollback/audit meaning.

Source-review baseline for this documentation pass: All-Config commit
`9d848f04`, ToolVision deployed evidence `2b3bf2c6`, ToolVision development UX
branch `2d936f3`, reviewed on 2026-08-24.

## Current bilingual documentation

| Topic | English | Vietnamese |
| --- | --- | --- |
| Project/system overview | [README](../../README.md) | [README](../../README.vi.md) |
| Active config payload | [README](../../config/README.md) | [README](../../config/README.vi.md) |
| OrcaSlicer sync/profiles | [README](../../Orca%20Config/README.md) | [README](../../Orca%20Config/README.vi.md) |
| StealthChanger operation | [Guide](huong-dan-he-thong-stealthchanger.en.md) | [Guide](huong-dan-he-thong-stealthchanger.md) |
| ToolVision machine integration | [Guide](toolvision-integration-guide.en.md) | [Guide](toolvision-integration-guide.vi.md) |
| ToolVision Z UX status | [Evidence/status](toolvision-z-calibration-ux-proposal.md) | [Evidence/status](toolvision-z-calibration-ux-proposal.vi.md) |

## Historical and retired material

- `extras/Nhat-ky-chinh-sua/`: append-only engineering history. Existing entries
  are not translated or modernized after the fact. New current documentation
  above supplies bilingual navigation and present-state descriptions.
- [`axiscope-cartographer/`](../axiscope-cartographer/README.md): inactive local
  fork evidence retained for rollback/reference. Its local status is summarized
  bilingually in [`FORK_INFO.md`](../axiscope-cartographer/FORK_INFO.md).
- [`retired-configs/2026-08-20-config-merge/`](../retired-configs/2026-08-20-config-merge/README.md):
  files no longer included by `printer.cfg`; README contains both languages.
- `extras/Config download/`: downloaded printer snapshots. They are not current
  repository documentation and are not edited.

## Three recent tracked rollback snapshots

Only links and current context are added here; snapshot contents remain
immutable.

1. [`pre-move-toolvision-to-printer-setup-20260823-220605`](../backups/pre-move-toolvision-to-printer-setup-20260823-220605/README.md) — before moving the machine ToolVision config into `Printer-Setup/` and routing JSON under `Generated-Data/ToolVision/`.
2. [`pre-toolvision-z-canary-20260823-211530`](../backups/pre-toolvision-z-canary-20260823-211530/README.md) — before enabling the PF2 report-only ToolVision canary.
3. [`pre-ktc-ownership-and-doc-sync-20260823-083206`](../backups/pre-ktc-ownership-and-doc-sync-20260823-083206/README.md) — before KTC ownership and documentation synchronization.

These are repository-tracked snapshots, not a statement about which three
directories currently exist on the CM4. The printer-side retention action and
its three retained recovery points are recorded in the immutable journal
[`2026-08-23-session-updates.md`](../Nhat-ky-chinh-sua/2026-08-23-session-updates.md).

## Rules for future documentation changes

1. Read the loaded config and scripts before changing current-state claims.
2. Label facts as active, observed, development/planned or unknown.
3. Update both language companions in the same commit.
4. Do not translate a plan into an implemented claim.
5. Do not rewrite old journals, backup READMEs or downloaded snapshots; add a
   new current guide/index entry instead.
6. When code, path or macro behavior changes, update the affected current pair
   and the daily journal together.

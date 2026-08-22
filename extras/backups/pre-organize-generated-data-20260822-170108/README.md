# Bản ghi sao lưu

- **Ngày:** 2026-08-22 17:01:08
- **Tác vụ:** Organize generated ToolVision and ShakeTune data and relocate misplaced printer backups.
- **File đã sao lưu:**
  - `all-config/Printer-Setup/input-shaper.cfg` — preserve the previous ShakeTune output path.
  - `all-config/Tool-Vision/tool_vision.cfg` — preserve the previous ToolVision state/result paths.
  - `all-config/scripts/install.sh` — preserve deployment exclusions.
  - `all-config/.gitignore` — preserve generated-data ignore rules.
  - `all-config/*.md` — preserve related project documentation.
  - `original-docs/` — preserve both pre-change `README.md` files without basename collision.
  - `tool-vision-source/` — preserve all ToolVision source, installer, test, and documentation files changed by this task.
  - `tool-vision-source/uninstall.sh` — preserve uninstall-time backup behavior.
- **Nhật ký liên quan:** `extras/Nhat-ky-chinh-sua/2026-08-22-session-updates.md`

The matching live-printer backup is stored at
`/home/voron/printer_data/config_backups/pre-organize-generated-data-20260822-170108/`.

`concurrent-toolvision-work/` preserves two tracked documentation files that
changed concurrently during this task. Their SHA-256 hashes were verified after
restoring them to the ToolVision PC checkout as unstaged user work.

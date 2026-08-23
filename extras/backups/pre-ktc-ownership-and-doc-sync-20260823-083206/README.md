# Backup: KTC Ownership and Documentation Sync

- Created: 2026-08-23 08:32:06 (Asia/Saigon)
- Scope: preserve the original deployment script, Input Shaper configuration,
  project documentation, Git submodule metadata, and project-rule status files.
- Reason: enforce KTC-Easy ownership of `toolchanger/readonly-configs/`, record
  operator-confirmed resolutions, and remove stale kTAMV/Input Shaper guidance.
- Safety: no printer connection, deployment, service restart, or G-code command
  was performed while the printer was running a job.

The `repo/` tree mirrors files from `Voron 5 Tool/`. The `project-rules/` tree
contains the original files from the workspace-level `.agents/` directory.

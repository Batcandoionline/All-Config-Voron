# Backup before ToolVision dd645103 sync

- Created: 2026-08-25 16:27:45 +07:00
- Source: `config/Printer-Setup/tool-vision.cfg`
- SHA-256: `6947c09f402f30fe20985d69f40ceb9236ce5f6b9bcf58846b80427d110f7809`
- Purpose: preserve the live-source panel before syncing ToolVision commit
  `dd645103c709d1312347dd09193aee586536ca19` and enabling the reviewed
  machine-specific KTC initialization hook.

The copied CFG is the rollback source. Runtime generated JSON is backed up
separately on the printer and off-device under the matching ToolVision backup.

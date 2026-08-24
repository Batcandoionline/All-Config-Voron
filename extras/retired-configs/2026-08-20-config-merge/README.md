# Retired configuration files — 2026-08-20

## English

These files are preserved for rollback and historical comparison. They are no
longer included by `config/printer.cfg`.

- `calibration.cfg` and `probe-mesh.cfg` were consolidated into
  `config/Printer-Setup/calibration-probe.cfg`.
- `crash_detection_override.cfg` and `tool_crash_cartographer.cfg` were
  consolidated into `config/Printer-Setup/tool-crash.cfg`.

The consolidation preserved production hardware values. Stale PF4/SexBolt
instructions and unused thermal-calibration storage macros were not carried
into the active files. Do not edit retired files to match current state; make a
new migration record if the active layout changes again.

## Tiếng Việt

Các file này được giữ cho rollback và so sánh lịch sử. `config/printer.cfg`
không còn include chúng.

- `calibration.cfg` và `probe-mesh.cfg` đã được hợp nhất vào
  `config/Printer-Setup/calibration-probe.cfg`.
- `crash_detection_override.cfg` và `tool_crash_cartographer.cfg` đã được hợp
  nhất vào `config/Printer-Setup/tool-crash.cfg`.

Lần hợp nhất giữ nguyên giá trị phần cứng production. Hướng dẫn PF4/SexBolt cũ
và macro lưu thermal calibration không còn dùng không được đưa vào file active.
Không sửa file retired để giống hiện trạng; nếu layout active đổi lần nữa, hãy
tạo record migration mới.

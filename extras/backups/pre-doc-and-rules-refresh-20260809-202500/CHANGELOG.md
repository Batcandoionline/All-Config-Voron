# Nhật ký thay đổi (Changelog)

Tất cả thay đổi đáng chú ý của cấu hình máy in được ghi nhận ở đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/).

---

## [Chưa phát hành]

### Thêm mới
- Hệ thống quy tắc AI đa file trong `.agents/` (PROJECT, DIRECTORY, WORKFLOW, SAFETY, STYLE, BACKUP, LOGGING, GIT_RULE, PROMPTS, DECISIONS, KNOWN_ISSUES, CHANGELOG, TODO)
- File tương thích đa AI (CLAUDE.md, GEMINI.md, .cursorrules, .clinerules, .roo/rules.md, .github/copilot-instructions.md)

### Thay đổi
- Di dời nhật ký chỉnh sửa từ `config/Nhat-ky-chinh-sua/` sang `extras/Nhat-ky-chinh-sua/`
- Đổi tên thư mục chính từ `All-Config-Voron-work` sang `Voron 5 Tool`
- Chuyển toàn bộ file quy tắc AI sang tiếng Việt

---

## [1.3.0] — 2026-07-02

### Thêm mới
- Nhật ký xử lý sự cố cho sự cố timeout CAN Cartographer

### Đã sửa
- Timeout kết nối MCU Cartographer sau soft restart (giải pháp tạm: tắt nguồn hoàn toàn)

---

## [1.2.0] — 2026-06-30

### Thay đổi
- Cập nhật `zero_reference_position` trong `probe-mesh.cfg` từ `170, 203` sang `174, 168` để khớp vị trí homing nozzle
- Cập nhật ngưỡng touch Cartographer từ `1968` lên `2594` sau khi hiệu chuẩn lại
- Điều chỉnh Z-offset cho tool T1, T2, T3, T4 dựa trên hiệu chuẩn lại
- Tinh chỉnh Z-offset T3 thêm -0.08mm dựa trên thử in thực tế

### Thêm mới
- Quy tắc bảo mật trong `.gitignore` cho `*.secrets`, `moonraker.secrets`, `wpa_supplicant.conf`

---

## [1.1.0] — 2026-06-23

### Thay đổi
- Tăng `check_gain_time` của `heater_bed` từ 120s lên 240s để ngăn shutdown giả từ nhiễu SSR
- Điều chỉnh `retry_tolerance` QGL từ 0.005 lên 0.0075 để ngăn hủy giả do motor numbering

### Thêm mới
- Cấu hình camera MF-500 ở độ phân giải 2K (2560x1400) với chống nhấp nháy 50Hz
- Hỗ trợ WebRTC qua camera-streamer

---

## [1.0.0] — 2026-05-16

### Thêm mới
- Cấu hình production ban đầu cho Voron 2.4 StealthChanger 5-Tool
- Cấu hình SexBolt Z endstop
- Tất cả định nghĩa tool (T0–T4) với board EBB CAN bus
- Cài đặt probe Cartographer v3
- Bộ macro hoàn chỉnh (PRINT_START, PRINT_END, vệ sinh đầu phun, prime line)

# Cấu trúc thư mục

## Tổng quan

```
All-Config-Voron-main/                  ← Thư mục workspace gốc
│
├── .agents/                            ← Hệ thống quy tắc AI (bạn đang ở đây)
│   ├── AGENTS.md                       ← Điểm vào — đọc đầu tiên
│   ├── PROJECT.md                      ← Mô tả dự án
│   ├── DIRECTORY.md                    ← File này
│   ├── WORKFLOW.md                     ← Quy trình làm việc từng bước
│   ├── SAFETY.md                       ← Quy tắc an toàn
│   ├── STYLE.md                        ← Phong cách code & quy tắc ngôn ngữ
│   ├── BACKUP.md                       ← Quy tắc sao lưu
│   ├── LOGGING.md                      ← Mẫu nhật ký hàng ngày
│   ├── GIT_RULE.md                     ← Quy tắc Git
│   ├── PROMPTS.md                      ← Mẫu xử lý yêu cầu
│   ├── DECISIONS.md                    ← Nhật ký quyết định kỹ thuật
│   ├── KNOWN_ISSUES.md                 ← Lỗi đã biết & cách khắc phục
│   ├── CHANGELOG.md                    ← Nhật ký thay đổi phiên bản
│   └── TODO.md                         ← Công việc đang chờ
│
├── Voron 5 Tool/                       ← ⭐ Thư mục git repo chính
│   ├── config/                         ← ⭐ Cấu hình Klipper ĐANG VẬN HÀNH
│   │   ├── printer.cfg                 ← Cấu hình chính của máy in
│   │   ├── moonraker.conf              ← Cấu hình Moonraker API server
│   │   ├── crowsnest.conf              ← Cấu hình streaming camera
│   │   ├── KlipperScreen.conf          ← Cấu hình màn hình KlipperScreen
│   │   ├── mainsail.cfg                ← Macro giao diện Mainsail
│   │   │
│   │   ├── Printer-Setup/             ← Cấu hình phần cứng & macro
│   │   │   ├── hardware.cfg            ← Định nghĩa MCU, stepper, heater
│   │   │   ├── fans-leds.cfg           ← Cấu hình quạt & LED
│   │   │   ├── calibration.cfg         ← PID, pressure advance, retraction
│   │   │   ├── input-shaper.cfg        ← Thông số input shaper
│   │   │   ├── probe-mesh.cfg          ← Probe Cartographer & bed mesh
│   │   │   ├── nozzle-clean.cfg        ← Macro vệ sinh đầu phun
│   │   │   ├── prime-lines.cfg         ← Macro prime line cho từng tool
│   │   │   ├── print-macros.cfg        ← PRINT_START/END và các macro hỗ trợ
│   │   │   ├── crash_detection_override.cfg
│   │   │   └── tool_crash_cartographer.cfg
│   │   │
│   │   ├── toolchanger/               ← Cấu hình StealthChanger
│   │   │   ├── toolchanger-config.cfg   ← Cài đặt toolchanger chính
│   │   │   ├── tools/                   ← Định nghĩa từng tool (T0–T4)
│   │   │   └── readonly-configs/        ← File do plugin quản lý (KHÔNG ĐƯỢC SỬA)
│   │   │
│   │   └── scripts/                    ← Shell script
│   │       ├── install.sh
│   │       ├── update.sh
│   │       └── cleanup-voron.sh
│   │
│   └── extras/                         ← Tài liệu bổ sung
│       ├── backups/                    ← 🔒 Sao lưu cấu hình (chỉ lưu cục bộ, gitignored)
│       ├── Nhat-ky-chinh-sua/         ← 📓 Nhật ký chỉnh sửa hàng ngày
│       │   ├── 2026-07-02-session-updates.md
│       │   ├── 2026-06-30-session-updates.md
│       │   └── ...
│       ├── logs/                       ← File nhật ký Klipper & Moonraker
│       │   ├── klippy.log
│       │   └── moonraker.log
│       ├── docs/                       ← Tài liệu & tài liệu tham khảo
│       ├── pictures/                   ← Ảnh phần cứng
│       ├── gcode/                      ← File G-code thử nghiệm
│       ├── axiscope-cartographer/      ← Dữ liệu hiệu chuẩn Cartographer
│       └── Config download/            ← Cấu hình tham khảo đã tải
│
└── Orca Config/                        ← Profile OrcaSlicer (riêng biệt)
```

## Quy tắc thư mục

### `config/` — Chỉ dành cho cấu hình Production
- Thư mục này đồng bộ trực tiếp với máy in qua Klipper.
- **Chỉ lưu file cấu hình đang vận hành (production-ready).**
- Không bao giờ lưu file tạm, script thử nghiệm, hoặc bản nháp cấu hình ở đây.
- Mọi file ở đây ảnh hưởng trực tiếp đến hoạt động của máy in.

### `config/toolchanger/readonly-configs/` — Không chạm vào
- Các file này do plugin `klipper-toolchanger-easy` quản lý.
- **Tuyệt đối không sửa đổi thủ công các file trong thư mục này.**
- Mọi thay đổi ở đây sẽ bị plugin ghi đè.

### `extras/Nhat-ky-chinh-sua/` — Nhật ký hàng ngày
- Mỗi ngày một file: `YYYY-MM-DD-session-updates.md`
- Ghi lại tất cả thay đổi cấu hình và sự cố cần khắc phục.
- Xem `LOGGING.md` để biết mẫu bắt buộc.

### `extras/backups/` — Sao lưu cục bộ
- Bản sao lưu tự động được tạo trước mỗi lần sửa đổi cấu hình.
- **Đã gitignore** — chỉ lưu cục bộ để giữ repo GitHub sạch.
- Xem `BACKUP.md` để biết quy tắc đặt tên.

### `extras/logs/` — File nhật ký hệ thống
- Sao chép từ máy in để phân tích offline.
- Dùng khi xử lý sự cố.
- Không tự động đồng bộ; sao chép thủ công khi cần điều tra.

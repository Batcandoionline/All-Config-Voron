# Cấu trúc thư mục

## Tổng quan

```
All-Config-Voron-main/                  ← Thư mục workspace gốc
│
├── .agents/                            ← Hệ thống quy tắc AI (bạn đang ở đây)
│   ├── AGENTS.md                       ← Điểm vào — đọc đầu tiên
│   ├── PROJECT.md                      ← Mô tả dự án & phần cứng thực tế
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
│   ├── README.md                       ← Tài liệu tổng quan dự án (English)
│   │
│   ├── config/                         ← ⭐ Cấu hình Klipper ĐANG VẬN HÀNH
│   │   ├── README.md                   ← Tài liệu cấu hình & pinout (English)
│   │   ├── printer.cfg                 ← Cấu hình chính (includes, kinematics, SAVE_CONFIG)
│   │   ├── moonraker.conf              ← Cấu hình Moonraker API server
│   │   ├── crowsnest.conf              ← Cấu hình streaming camera (WebRTC)
│   │   ├── KlipperScreen.conf          ← Cấu hình màn hình KlipperScreen (vi)
│   │   ├── mainsail.cfg                ← Macro giao diện Mainsail
│   │   │
│   │   ├── Printer-Setup/             ← Cấu hình phần cứng & macro máy in
│   │   │   ├── hardware.cfg            ← Định nghĩa MCU (Manta M8P V2), stepper, heater
│   │   │   ├── fans-leds.cfg           ← Cấu hình quạt thùng, quạt bed, LED trạng thái
│   │   │   ├── calibration.cfg         ← Thermal compensation, [axiscope] switch calib
│   │   │   ├── input-shaper.cfg        ← Thông số input shaper
│   │   │   ├── probe-mesh.cfg          ← Cartographer V3 Touch/Scan & bed mesh (55×55)
│   │   │   ├── nozzle-clean.cfg        ← Bambu A1 silicone brush & bucket (CLEAN_NOZZLE)
│   │   │   ├── prime-lines.cfg         ← Macro prime line cho từng tool (T0–T4)
│   │   │   ├── print-macros.cfg        ← PRINT_START/END và các macro hỗ trợ
│   │   │   ├── crash_detection_override.cfg ← Macro override chống crash tool
│   │   │   └── tool_crash_cartographer.cfg  ← Cartographer tool crash protection
│   │   │
│   │   ├── toolchanger/               ← Cấu hình StealthChanger
│   │   │   ├── toolchanger-config.cfg   ← Cài đặt toolchanger chính & tọa độ switch
│   │   │   ├── tools/                   ← Định nghĩa từng tool (T0.cfg – T4.cfg)
│   │   │   └── readonly-configs/        ← File do plugin quản lý (KHÔNG ĐƯỢC SỬA)
│   │   │
│   │   └── scripts/                    ← Shell script quản lý & triển khai
│   │       ├── install.sh              ← Script cài đặt cấu hình lần đầu
│   │       ├── update.sh               ← Script cập nhật cấu hình & auto backup
│   │       └── cleanup-voron.sh        ← Dọn dẹp các bản backup rác cũ
│   │
│   └── extras/                         ← Tài liệu bổ sung & dữ liệu vận hành
│       ├── backups/                    ← 🔒 Bản sao lưu timestamped trước mỗi lần sửa
│       ├── Nhat-ky-chinh-sua/         ← 📓 Nhật ký chỉnh sửa hàng ngày (Tiếng Việt)
│       ├── logs/                       ← File nhật ký Klipper & Moonraker
│       ├── docs/                       ← Tài liệu hướng dẫn & sơ đồ phần cứng
│       ├── pictures/                   ← Ảnh chụp phần cứng, sơ đồ chân
│       ├── gcode/                      ← File G-code thử nghiệm
│       ├── axiscope-cartographer/      ← Dữ liệu hiệu chuẩn Axiscope & Cartographer
│       ├── Orcasilcer setting/         ← Profile OrcaSlicer đã xuất
│       └── Config download/            ← Cấu hình tham khảo đã tải về
│
└── Orca Config/                        ← Profile OrcaSlicer (riêng biệt)
```

## Quy tắc thư mục

### `config/` — Chỉ dành cho cấu hình Production
- Thư mục này đồng bộ trực tiếp với máy in qua `scripts/install.sh` và `scripts/update.sh`.
- **Chỉ lưu file cấu hình đang vận hành (production-ready).**
- Không bao giờ lưu file tạm, script thử nghiệm, hoặc bản nháp cấu hình ở đây.
- Các file tài liệu (`README.md`, `*.md`) trong `config/` được các script tự động loại trừ (`--exclude`) khi đồng bộ sang `~/printer_data/config/` để đảm bảo máy in luôn gọn gàng.

### `config/toolchanger/readonly-configs/` — Không chạm vào
- Các file này do plugin `klipper-toolchanger-easy` quản lý.
- **Tuyệt đối không sửa đổi thủ công các file trong thư mục này.**
- Mọi thay đổi ở đây sẽ bị plugin ghi đè.

### `extras/Nhat-ky-chinh-sua/` — Nhật ký hàng ngày
- Mỗi ngày một file: `YYYY-MM-DD-session-updates.md`.
- Ghi lại tất cả thay đổi cấu hình, bảng số liệu đo đạc, phân tích và sự cố cần khắc phục.
- Xem `LOGGING.md` để biết mẫu bắt buộc.

### `extras/backups/` — Bản sao lưu hệ thống
- Bản sao lưu tự động được tạo trước mỗi lần sửa đổi file cấu hình.
- Đã được theo dõi trên Git (theo quyết định an toàn dữ liệu đám mây) để phòng trường hợp hỏng máy tính cá nhân.
- Xem `BACKUP.md` để biết quy tắc đặt tên và quản lý.

### `extras/logs/` — File nhật ký hệ thống
- Sao chép từ máy in để phân tích offline khi cần điều tra sự cố.
- Tránh commit các file log quá lớn trừ khi được yêu cầu.

# Nhật ký — 2026-08-09

## 1. Cấu hình Axiscope Z-Offset Switch (Tọa độ X:68, Y:-10, Z:7)

### Mục tiêu
Cấu hình module `[axiscope]` và cập nhật tọa độ switch hiệu chuẩn Z-offset giữa các tool (T0-T4) tại vị trí X:68, Y:-10, Z:7.

### File đã sửa đổi
- `config/Printer-Setup/calibration.cfg` — Kích hoạt và cấu hình section `[axiscope]` với tọa độ công tắc (X:68, Y:-10, Z:7), pin switch, và macro gia nhiệt an toàn 150°C.
- `config/toolchanger/toolchanger-config.cfg` — Cập nhật tọa độ `_CALIBRATION_SWITCH` sang X:68, Y:-10, Z:15 và comment out `[tools_calibrate]` để tránh xung đột `probe_multi_axis`.

### Sao lưu
- [calibration.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-z-offset-switch-20260809-180500/calibration.cfg)
- [toolchanger-config.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-z-offset-switch-20260809-180500/toolchanger-config.cfg)

---

## 2. Đồng bộ cấu hình printer.cfg mới từ máy in

### Mục tiêu
Đồng bộ khối `SAVE_CONFIG` mới nhất từ máy in thực tế vào kho mã nguồn (chứa các hệ số Cartographer scan model, Cartographer touch threshold mới `1819`, reference_temperature `42.44`, PID calib, tool offsets).

### File đã sửa đổi
- `config/printer.cfg` — Cập nhật khối `SAVE_CONFIG` đồng bộ từ máy in.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-printer-cfg-20260809-180830/printer.cfg)

---

## 3. Cập nhật chân tín hiệu Z-Offset Switch sang PF2 (GND + PF2)

### Mục tiêu
Người dùng đã đấu nối dây công tắc microswitch Z-offset vào cổng PF2 và GND (G) trên board Manta M8P V2 thay vì PF4. Cập nhật pin cấu hình trong Klipper thành `^PF2`.

### File đã sửa đổi
- `config/Printer-Setup/calibration.cfg` — Đổi `pin: ^PF4` thành `pin: ^PF2` trong section `[axiscope]`.
- `config/toolchanger/toolchanger-config.cfg` — Đổi chú thích pin trong `_CALIBRATION_SWITCH` và `[tools_calibrate]` thành `PF2`.
- `config/README.md` — Cập nhật bảng pinout phần cứng: Z-Offset sensor kết nối Manta M8P `PF2`.

### Sao lưu
- [calibration.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-switch-pin-pf2-20260809-181000/calibration.cfg)
- [toolchanger-config.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-switch-pin-pf2-20260809-181000/toolchanger-config.cfg)

---

## 4. Phân tích 3 lần đo Z-Offset (Axiscope Switch) và Cập nhật Giá trị Trung bình

### Mục tiêu
Tổng hợp kết quả đo từ 3 lần chạy hiệu chuẩn Z-offset tự động bằng công tắc Axiscope, so sánh với cấu hình gốc và cập nhật giá trị trung bình vào `printer.cfg`.

### Bảng tổng hợp dữ liệu đo

| Tool | Lần 1 (mm) | Lần 2 (mm) | Lần 3 (mm) | Trung bình mới (mm) | Bản gốc cũ (mm) | Độ lệch (Delta) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **T0 (Ref)** | 6.392 | 6.391 | 6.417 | **6.400** (Ref) | 0.000 (Ref) | — |
| **T1** | +0.088 | +0.079 | +0.071 | **+0.079** | +0.228 | -0.149 mm |
| **T2** | -0.294 | -0.316 | -0.310 | **-0.307** | -0.295 | -0.012 mm |
| **T3** | -0.156 | -0.114 | -0.131 | **-0.134** | -0.268 | +0.134 mm |
| **T4** | -0.064 | 0.000 | -0.039 | **-0.034** | +0.086 | -0.120 mm |

---

## 5. Khôi phục Z-Offset In Thực Tế Đẹp & Loại Bỏ File README.md Khi Đồng Bộ Sang Máy In

### Mục tiêu
1. Khôi phục lại bộ giá trị `gcode_z_offset` in thực tế đẹp (`T1: 0.228, T2: -0.295, T3: -0.268, T4: 0.086`) theo yêu cầu người dùng sau khi đánh giá chất lượng lớp in đầu tiên.
2. Cập nhật các script `install.sh` và `update.sh` để thêm quy tắc `--exclude "README.md"` và `--exclude "*.md"`, đảm bảo thư mục cấu hình vận hành `~/printer_data/config` trên máy in hoàn toàn sạch sẽ, không bị lẫn các file tài liệu hướng dẫn markdown của Git.

### File đã sửa đổi
- `config/printer.cfg` — Khôi phục `gcode_z_offset`: T1=0.228, T2=-0.295, T3=-0.268, T4=0.086.
- `config/scripts/install.sh` — Thêm `--exclude "README.md" --exclude "*.md"`.
- `config/scripts/update.sh` — Thêm `--exclude "README.md" --exclude "*.md"`.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-restore-live-z-offsets-and-exclude-readme-20260809-201500/printer.cfg)
- [install.sh (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-restore-live-z-offsets-and-exclude-readme-20260809-201500/install.sh)
- [update.sh (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-restore-live-z-offsets-and-exclude-readme-20260809-201500/update.sh)

---

## 6. Rà Soát Toàn Diện và Viết Lại Tài Liệu Dự Án & Hệ Thống Quy Tắc AI

### Mục tiêu
Đọc lại từng phần của dự án, cập nhật và đồng bộ hóa toàn bộ các file hướng dẫn, sơ đồ phần cứng, quy tắc sao lưu đám mây, nhật ký quyết định và tài liệu kỹ thuật sau thời gian dài vận hành.

### File đã sửa đổi
- `.agents/PROJECT.md` — Cập nhật chuẩn xác phần cứng: Manta M8P V2 + CM4, Cartographer V3 fw6.1.0, Axiscope microswitch trên chân PF2.
- `.agents/DIRECTORY.md` — Cập nhật cấu trúc thư mục, làm rõ cơ chế loại trừ markdown của script triển khai và chính sách lưu trữ backup trên Git.
- `.agents/BACKUP.md` — Cập nhật chính sách đồng bộ sao lưu đám mây Git.
- `.agents/GIT_RULE.md` — Cập nhật quy tắc commit, loại bỏ các file nhạy cảm.
- `.agents/DECISIONS.md` — Bổ sung các quyết định kỹ thuật ngày 2026-08-09 (PF2 switch, chiến lược Z-offset kết hợp, loại trừ markdown).
- `.agents/CHANGELOG.md` — Thêm phiên bản `[1.4.0] — 2026-08-09`.
- `.agents/TODO.md` — Cập nhật các tác vụ đã hoàn thành trong phiên.
- `Voron 5 Tool/README.md` — Viết lại tài liệu tổng quan tiếng Anh: sơ đồ phần cứng Manta M8P V2, pinout PF2, hướng dẫn cài đặt sạch, quy trình hiệu chuẩn.
- `Voron 5 Tool/config/README.md` — Cập nhật tài liệu kỹ thuật của thư mục cấu hình và bảng tra cứu chân tín hiệu.

### Sao lưu
- [pre-doc-and-rules-refresh-20260809-202500](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-doc-and-rules-refresh-20260809-202500/README.md)

---

## 7. Đại Tu Toàn Diện File README.md Chính Của Dự Án

### Mục tiêu
Nâng cấp file `Voron 5 Tool/README.md` thành một tài liệu kỹ thuật tổng thể, chuyên nghiệp và chuẩn xác 100% với toàn bộ phần cứng, sơ đồ mạng CAN bus, hệ thống StealthChanger 5 đầu in, hệ thống probe Cartographer V3, quy trình vệ sinh đầu phun Bambu A1 và chiến lược Z-offset 2 tầng.

### File đã sửa đổi
- `Voron 5 Tool/README.md` — Bổ sung sơ đồ kiến trúc Mermaid, bảng chi tiết 5 toolhead CAN UUID, tọa độ dock thực tế, quy trình QGL và Axis Twist Compensation, công thức Z-offset, và hướng dẫn OrcaSlicer.

### Sao lưu
- [pre-master-readme-overhaul-20260809-203000](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-master-readme-overhaul-20260809-203000/README.md)

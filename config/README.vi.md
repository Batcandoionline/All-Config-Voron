# Cấu hình Vận hành Klipper (Production Payload)

[English](README.md) | [Tiếng Việt](README.vi.md)

Thư mục này chứa toàn bộ cấu hình Klipper đang hoạt động, được đồng bộ sang `~/printer_data/config` trên máy in. Các file tài liệu (`*.md`) tự động được loại trừ khi triển khai.

---

## 1. Chuỗi nạp module (`printer.cfg`)

File gốc `printer.cfg` đóng vai trò điều phối trung tâm và nạp các module theo thứ tự:

```ini
[include mainsail.cfg]                                          # Macro giao diện Mainsail Web
[include toolchanger/readonly-configs/toolchanger-include.cfg]  # KTC-Easy core (symlink)
[include Printer-Setup/calibration-probe.cfg]                   # Đầu dò Cartographer & Bed mesh
[include Printer-Setup/ktamv.cfg]                               # Camera kTAMV đối chiếu XY
[include Printer-Setup/hardware.cfg]                            # Khai báo stepper, TMC, heater
[include Printer-Setup/fans-leds.cfg]                           # Quạt thùng, quạt bed, LED
[include Printer-Setup/input-shaper.cfg]                        # Bộ lọc chống rung Shaper hợp nhất
[include Printer-Setup/nozzle-clean.cfg]                        # Vệ sinh đầu phun cọ silicon
[include Printer-Setup/prime-lines.cfg]                         # Đường đùn mồi nhựa từng tool
[include Printer-Setup/print-macros.cfg]                        # Macro bắt đầu/kết thúc bản in
[include Printer-Setup/filament-dryer.cfg]                      # Sấy cuộn nhựa trên bàn nhiệt
[include Printer-Setup/test-speed.cfg]                          # Macro TEST_SPEED & TEST_Z_SPEED
[include Printer-Setup/tool-crash.cfg]                          # Cảm biến phát hiện rơi/kẹt tool
```

---

## 2. Phân cấp & Chủ thể quản lý thư mục

| Đường dẫn | Chủ thể quản lý | Mô tả & Quy tắc |
| :--- | :--- | :--- |
| `printer.cfg` | Người dùng / Git | Cấu hình động học, giới hạn, MCU UUID, include. Chứa khối `#*# <SAVE_CONFIG>`. |
| `Printer-Setup/*.cfg` | Người dùng / Git | Các module tính năng, macro bảo vệ và định nghĩa chân phần cứng. |
| `toolchanger/toolchanger-config.cfg` | Người dùng / Git | Tọa độ dock StealthChanger, tốc độ gắp/thả tool, hook đèn LED. |
| `toolchanger/tools/T0.cfg` ... `T4.cfg` | Người dùng / Git | Thông số động cơ extruder, offset đầu in và nhiệt độ chờ từng tool. |
| `toolchanger/readonly-configs/` | **KTC-Easy** | **KHÔNG SỬA.** Symlink do installer của `klipper-toolchanger-easy` quản lý. |
| `scripts/*.sh` | Người dùng / Git | Script triển khai (`install.sh`), cập nhật (`update.sh`), bảo trì (`cleanup-voron.sh`). |
| `moonraker.conf` | Moonraker / Git | Thiết lập API server, quyền bảo mật và Update Manager. |
| `crowsnest.conf`, `KlipperScreen.conf` | Hệ thống / Git | Cấu hình stream camera WebRTC và màn hình cảm ứng KlipperScreen. |

---

## 3. Bản đồ Phần cứng & Động học thực tế

| Chức năng | Khai báo Phần cứng / Chân Pin | Giới hạn vận hành |
| :--- | :--- | :--- |
| **MCU Chính** | BTT Manta M8P V2.0 (`19b203d75137`) | CANbus 1 Mbps |
| **Đầu dò / Homing Z** | Cartographer V3 (`da13d909ce34`) | Touch homing + Bed Mesh quét adaptive 55×55 |
| **Cảm biến Input Shaper**| Onboard ADXL345 trên Cartographer | Gắn trên shuttle; X: MZV 43.6 Hz, Y: MZV 33.4 Hz |
| **Động cơ CoreXY** | Stepper X: `PE6` / PF0 endstop; Stepper Y: `PE2` / PF1 endstop | Vận tốc max: 350 mm/s (test 500), Gia tốc: 7000 mm/s² (test 15k) |
| **Khung Z 4 góc (QGL)** | Z0: `PG9`, Z1: `PB4`, Z2: `PG13`, Z3: `PB8` | Vận tốc Z: 70 mm/s (test 80), Gia tốc Z: 900 mm/s² (test 1k) |
| **Bàn nhiệt AC** | Heater `PA1`, Sensor `PB0` (NTC 100K) | 220V 1000W AC qua SSR, max 120 °C |
| **Nhiệt độ vỏ / Quạt bed**| Cảm biến vỏ: `PB1` (Generic 3950); Quạt bed: `PF8` | Điều khiển nhiệt độ buồng in tự động |
| **Quạt CM4 / Vỏ máy** | Quạt CM4: `PF7`, Quạt vỏ máy: `PF9`, LED buồng in: `PD15` | Làm mát tự động theo ngưỡng nhiệt driver & MCU |
| **Extruder & Quạt Tool** | 5 bo mạch CAN BTT EBB36 V1.2; Quạt tản nhiệt `PA0`, Quạt part `PA1` | Extruder: TMC2209 dòng 0.6A; Quạt part điều hướng tự động qua `M106` |

---

## 4. Cập nhật 1-Click trên Mainsail & Tối ưu Bộ nhớ

### 4.1. Khởi tạo 1 lần trên máy in (Sparse Checkout — Tiết kiệm 97.7% dung lượng)
Để tránh tải hơn 600 MB backup máy tính và lịch sử git cũ, chạy lệnh SSH một lần duy nhất:
```bash
git clone --depth=1 --filter=blob:none --sparse https://github.com/IDcrazy123/All-Config-Voron.git ~/All-Config-Voron
cd ~/All-Config-Voron
git sparse-checkout set config
sudo systemctl restart moonraker
```

### 4.2. Vận hành hàng ngày
- Đẩy code mới từ máy tính lên GitHub: `git push origin main`.
- Trên web **Mainsail > Cài đặt > Trình quản lý cập nhật**, bấm nút **Update** tại mục `All-Config-Voron`.
- Moonraker tự động kéo code, chạy `install.sh` (kiểm tra an toàn symlink, dọn sạch file `.md`, tự động giữ tối đa 5 bản backup gần nhất, rsync sang `~/printer_data/config`) và khởi động lại Klipper.

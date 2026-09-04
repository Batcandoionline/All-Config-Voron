# Voron 2.4 StealthChanger — Cấu hình Vận hành 5 Tool

[English](README.md) | [Tiếng Việt](README.vi.md) | [Tài liệu cấu hình](config/README.vi.md) | [Chỉ mục tài liệu](extras/docs/README.vi.md)

Cấu hình Klipper sản xuất, script triển khai và profile OrcaSlicer cho máy in 3D **Voron 2.4 350 mm CoreXY** trang bị hệ thống đổi đầu in **StealthChanger 5 tool** (KTC-Easy).

---

## 1. Thông số Kỹ thuật & Bản đồ Phần cứng

| Hệ thống | Thông số phần cứng thực tế | Cấu hình & Chân Pin |
| :--- | :--- | :--- |
| **Bo mạch chính & Host** | BTT Manta M8P V2.0 + BTT CM4 | Giao tiếp CANbus `can0` (1 Mbps), UUID `19b203d75137` |
| **Cơ cấu Toolchanger** | StealthChanger qua KTC-Easy | 5 dock phía sau (T0–T4), shuttle có cảm biến rơi tool OptoTap |
| **Bo mạch Toolhead** | 5x BTT EBB36 V1.2 qua CAN | CAN UUID riêng từng tool, quạt tản nhiệt (`PA0`), quạt part (`PA1`) |
| **Extruder & Hotend** | 5x WW BMG (TMC2209 dòng 0.6A) + TZ V6 2.0 | Đầu phun 0.4 mm, thanh nhiệt 50W 24V, thermistor NTC 100K |
| **Động cơ CoreXY** | 0.9° 400 bước (TMC2209 dòng 0.8A) | X: `PE6`/`PE5`, endstop `PF0` (348 mm); Y: `PE2`/`PE1`, endstop `PF1` (336 mm, min -10 mm) |
| **Khung Z 4 góc (QGL)** | 4 động cơ dẫn động đai (GT2 16T / tỉ số 80:16) | Z0: `PG9`, Z1: `PB4`, Z2: `PG13`, Z3: `PB8` (TMC2209 dòng 0.8A) |
| **Giới hạn Động học** | Giới hạn vận hành an toàn | Vận tốc max: `350 mm/s` (test `500`), Gia tốc: `7000 mm/s²` (test `15k`), Vận tốc Z: `70 mm/s` (test `80`), Gia tốc Z: `900 mm/s²` (test `1k`) |
| **Đầu dò & Homing Z** | Cartographer V3 CAN (`da13d909ce34`) | Touch homing tại tâm bàn (174, 168) + Bed Mesh quét adaptive 55×55 |
| **Input Shaper** | Shaper Hợp nhất Shuttle (Cartographer ADXL345) | Trục X: `mzv` @ 43.6 Hz ($\zeta = 0.124$); Trục Y: `mzv` @ 33.4 Hz ($\zeta = 0.080$) |
| **Bàn nhiệt AC** | Tấm nhiệt silicon 220V 1000W + Rơ-le bán dẫn SSR | Heater `PA1`, Sensor `PB0` (NTC 100K MGB18), nhiệt độ max 120 °C |
| **Vỏ máy & Làm mát** | Cảm biến buồng in `PB1` (Generic 3950) | Quạt bed `PF8`, Quạt CM4 `PF7`, Quạt vỏ `PF9`, LED buồng in `PD15` |
| **Vệ sinh Đầu phun** | Khay xả nhựa & Cọ silicon Bambu A1 | Khay xả tại X=320, Y=-8.0; Cọ chà silicon tại X=277..320, Y=-8.0 |

---

## 2. Sơ đồ 5 Tool StealthChanger & Tọa độ Offset

Tọa độ dock và offset cơ khí XYZ (được lưu tại khối `#*# <SAVE_CONFIG>` trong `config/printer.cfg`):

| Tool | CANbus UUID | Tọa độ Dock (X, Y, Z) | Offset cơ khí (X, Y, Z) | Vai trò & Trạng thái |
| :---: | :---: | :---: | :---: | :--- |
| **T0** | `441e1484ac41` | `(30.2, 1.3, 343.0)` | `(0.000, 0.000, 0.0000)` | **Tool tham chiếu chuẩn** (Gốc 0 cho toàn bộ offset) |
| **T1** | `6475b5b9e028` | `(104.0, 1.1, 343.0)` | `(-0.159, -0.195, 0.2360)` | Toolhead vận hành đã hiệu chuẩn |
| **T2** | `4ad9d622a836` | `(176.0, 1.6, 343.0)` | `(0.820, 0.240, -0.3160)` | Toolhead vận hành đã hiệu chuẩn |
| **T3** | `c2465b7c36f8` | `(249.5, 2.5, 343.0)` | `(0.326, 0.524, -0.1896)` | Toolhead vận hành đã hiệu chuẩn |
| **T4** | `28650279df58` | `(321.5, 2.6, 343.0)` | `(0.168, 0.268, 0.1200)` | Toolhead vận hành đã hiệu chuẩn |

> [!NOTE]
> Khi đổi tool, lệnh `pickup_gcode` của KTC giữ đầu phun tì trên đệm silicon của dock trong lúc nung nhiệt (`M109`) để chống rỉ nhựa trước khi hạ Z. Để rút ngắn thời gian chờ tại dock, hãy cài đặt **Pre-heating time** trong OrcaSlicer khoảng 15–20 giây.

---

## 3. Bảng Tra cứu Macro Vận hành Cốt lõi

| Phân nhóm | Lệnh Macro | Chức năng chi tiết |
| :--- | :--- | :--- |
| **Quy trình In** | `PRINT_START [BED=..] [HOTEND=..]` | Homing, ngâm nhiệt buồng, cân bàn QGL, Touch Z, quét lưới bàn in, lau đầu phun, gắp T0. |
| | `PRINT_END` | Rút sợi nhựa, nâng Z an toàn, trả tool về dock, tắt nhiệt/quạt, chuyển LED về idle. |
| | `PAUSE` / `RESUME` / `CANCEL_PRINT` | Điều khiển tạm dừng/hủy in với vị trí đỗ an toàn và phục hồi dòng đùn nhựa. |
| **Kiểm tra Động học**| `TEST_SPEED [SPEED=..] [ACCEL=..]` | Kiểm tra tốc độ/gia tốc CoreXY; đối chiếu vi bước qua `GET_POSITION` tại endstop. |
| | `TEST_Z_SPEED [SPEED=..] [ACCEL=..]` | Kiểm tra nâng hạ trục Z đa chu kỳ (Z=10 đến 320 mm); kiểm chứng đồng bộ 4 động cơ Z. |
| **Bảo trì Đầu phun** | `CLEAN_NOZZLE [WIPES=5] [TEMP=150]` | Gia nhiệt đầu phun, gạt phôi nhựa và chà xoay tròn trên cọ silicon Bambu A1. |
| | `PRIME_LINES [TOOL=..]` | Đùn đường mồi nhựa sạch dọc mép bàn in cho tool được chọn trước khi in. |
| **Sấy cuộn nhựa** | `START_DRYER [TEMPERATURE=..] [TIME=..]` | Sấy cuộn nhựa trên bàn nhiệt (`DRY_PLA`, `DRY_PETG`, `DRY_ABS`). Tự động trả tool an toàn. |
| | `STOP_DRYER` / `DRYER_STATUS` | Dừng sấy và làm nguội bàn in; hiển thị thời gian sấy còn lại. |
| **Chẩn đoán** | `CHECK_OFFSETS` | Hiển thị bảng offset XYZ của toàn bộ 5 tool mà không gây chuyển động máy. |
| | `CALIBRATION_STATUS` | Báo cáo trạng thái backend hiệu chuẩn đang hoạt động (kTAMV đối chiếu camera XY). |

---

## 4. Cấu trúc Thư mục Dự án

```text
All-Config-Voron/
├── config/                     # Cấu hình Klipper vận hành (đồng bộ sang ~/printer_data/config)
│   ├── printer.cfg             # Cấu hình gốc, động học, include, khối SAVE_CONFIG
│   ├── moonraker.conf          # Cấu hình API Moonraker & tích hợp Update Manager
│   ├── crowsnest.conf          # Cấu hình stream camera WebRTC
│   ├── KlipperScreen.conf      # Giao diện màn hình cảm ứng KlipperScreen
│   ├── mainsail.cfg            # Macro giao diện Mainsail
│   ├── Printer-Setup/          # Các module phần cứng, quạt, LED, test tốc độ, sấy nhựa...
│   ├── toolchanger/            # Cấu hình StealthChanger, tools/T0..T4.cfg, readonly symlinks
│   └── scripts/                # Script triển khai (install.sh), cập nhật, bảo trì
├── Orca Config/                # Profile máy in, quy trình và nhựa in OrcaSlicer
└── extras/                     # Tài liệu, nhật ký công việc hàng ngày, bản backup, dữ liệu ShakeTune
```

---

## 5. Cập nhật 1-Click trên Mainsail & Tối ưu Dung lượng

### 5.1. Khởi tạo 1 lần trên máy in (Sparse Checkout)
Để tránh tải hơn 600 MB backup máy tính và lịch sử git cũ làm nặng thẻ nhớ Pi, chạy qua SSH một lần duy nhất:
```bash
git clone --depth=1 --filter=blob:none --sparse https://github.com/IDcrazy123/All-Config-Voron.git ~/All-Config-Voron
cd ~/All-Config-Voron
git sparse-checkout set config
sudo systemctl restart moonraker
```
*Kết quả: Dung lượng chiếm dụng trên máy in giảm từ **610 MB xuống chỉ còn 14 MB (Tiết kiệm 97.7%)**.*

### 5.2. Cập nhật thường nhật bằng 1 cú Click
1. Đẩy các thay đổi cấu hình từ máy tính lên GitHub (`git push origin main`).
2. Trên giao diện **Mainsail Web** tại mục **Cài đặt > Máy in / Trình quản lý cập nhật**, bấm nút **Update** tại **`All-Config-Voron`**.
3. Moonraker tự động kéo code, chạy `config/scripts/install.sh` (kiểm tra an toàn symlink, dọn sạch file `.md`, tự động giữ tối đa 5 bản backup gần nhất, rsync file) và khởi động lại Klipper. Hoàn toàn không cần SSH.

---

## 6. Quy tắc An toàn Tuyệt đối

1. **Tuyệt đối không sửa file trong `config/toolchanger/readonly-configs/`:** Đây là các symlink do plugin `klipper-toolchanger-easy` sở hữu.
2. **Bảo vệ khối `printer.cfg` `#*# <SAVE_CONFIG>`:** Chứa toàn bộ dữ liệu hiệu chuẩn PID và Cartographer. Luôn đối chiếu trước khi push thay đổi từ máy tính.
3. **Nút dừng khẩn cấp (Emergency Stop):** Luôn để tay sẵn sàng nút Emergency Stop trong lần chuyển động đầu tiên sau khi can thiệp cơ khí hoặc tọa độ dock.

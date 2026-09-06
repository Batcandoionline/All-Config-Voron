# Bảng đối chiếu cấu hình máy in & Hướng dẫn cập nhật 1-Click qua Mainsail

> **Ngày thực hiện:** 04/09/2026  
> **Trạng thái:** Đã clone toàn bộ 51 file từ máy in (`192.168.1.43`) về PC (`extras/Config download/config-20260904-205500/`), kiểm tra mã băm SHA-256 đối chiếu 1:1, cấu hình `moonraker.conf` tích hợp Update Manager.

---

## Phần 1: Giải pháp cập nhật 1-Click trực tiếp trong Mainsail (Không cần SSH)

### 1.1. Thực trạng trước đây
- Trước đây, máy in cập nhật cấu hình qua SSH bằng lệnh:
  ```bash
  bash ~/printer_data/config/scripts/update.sh
  ```
- Script `update.sh` tải một file nén tạm thời từ GitHub `archive/refs/heads/main.tar.gz`, giải nén vào `/tmp`, rồi chạy `install.sh` để `rsync` vào `~/printer_data/config/`.
- Nhược điểm: Bắt buộc người dùng phải mở phần mềm terminal SSH mỗi khi muốn cập nhật máy in.

### 1.2. Tại sao không nên biến trực tiếp `~/printer_data/config` thành Git repo?
Nhiều người nghĩ đến việc khởi tạo Git trực tiếp tại `~/printer_data/config`. Tuy nhiên, trong Klipper sản xuất, điều này gây ra lỗi nghiêm trọng:
1. **Lỗi Dirty Tree & Khóa Update:** Klipper liên tục tự động ghi đè các tham số hiệu chuẩn vào cuối file `printer.cfg` (khối `#*# <SAVE_CONFIG>`) sau mỗi lần PID tune, Z-offset calibrate, Bed Mesh. Moonraker cũng tự sinh file `.moonraker.conf.bkp`, ShakeTune sinh ảnh trong `Generated-Data/`.
2. Khi đó, Moonraker sẽ đánh dấu trạng thái Git là **`DIRTY` (màu đỏ)** và **KHÓA nút cập nhật**.
3. Nếu người dùng bấm "Hard Recovery" trong Mainsail, Git sẽ xóa sạch các giá trị `SAVE_CONFIG` thực tế của máy in.

### 1.3. Giải pháp chuẩn xác: Tích hợp Moonraker Update Manager với `~/All-Config-Voron`
Mô hình này là mô hình chuẩn nhất mà Moonraker thiết kế (tương tự như cách KlipperScreen, Sonar, Crowsnest hoạt động):

```
GitHub (IDcrazy123/All-Config-Voron)
                 │
                 ▼  (Mainsail 1-click Update / git pull)
     ~/All-Config-Voron  (Git Repo sạch, không có runtime files)
                 │
                 ▼  (install_script: config/scripts/install.sh)
        Kiểm tra an toàn (KTC symlinks, kTAMV patches)
        Tạo bản backup timestamped trong config_backups/
        Rsync file sạch sang ~/printer_data/config
                 │
                 ▼  (managed_services: klipper)
        Tự động Restart Klipper an toàn
```

#### Cấu hình đã thêm vào `moonraker.conf`:
```ini
[update_manager All-Config-Voron]
type: git_repo
path: ~/All-Config-Voron
origin: https://github.com/IDcrazy123/All-Config-Voron.git
primary_branch: main
managed_services: klipper
install_script: config/scripts/install.sh
```

#### Bước thiết lập trên máy in (Chỉ làm 1 lần duy nhất qua SSH):
Mở terminal SSH vào máy in (`ssh voron@192.168.1.43`) và chạy chuỗi lệnh thiết lập chuẩn để đảm bảo Moonraker nhận diện đầy đủ lịch sử commit và quyền thực thi script:

```bash
# 1. Nếu chưa clone hoặc clone cũ bị lỗi, xóa thư mục cũ và clone lại chuẩn
rm -rf ~/All-Config-Voron
git clone https://github.com/IDcrazy123/All-Config-Voron.git ~/All-Config-Voron
cd ~/All-Config-Voron

# 2. Đảm bảo cấp quyền thực thi cho các script cài đặt & triển khai
chmod +x config/scripts/*.sh

# 3. Chạy thử nghiệm script cài đặt lần đầu để kiểm tra an toàn và đồng bộ
bash config/scripts/install.sh

# 4. Khởi động lại Moonraker để nhận diện Update Manager trong Mainsail
sudo systemctl restart moonraker
```

> [!IMPORTANT]
> **Lưu ý kỹ thuật quan trọng về Moonraker Update Manager:**
> - **Quyền thực thi Script (`chmod +x`):** Moonraker yêu cầu file `install_script` phải có cờ thực thi (`100755`). Toàn bộ script trong `config/scripts/` đã được cấp quyền trực tiếp trong Git.
> - **Tránh dùng `--depth=1` (Shallow clone):** Moonraker Update Manager liên tục thực hiện lệnh `git rev-list --count HEAD..origin/main` để tính số commit đứng sau. Nếu dùng shallow clone (`--depth=1`), Moonraker sẽ báo lỗi `error in object: unshallow clone needed` hoặc đánh dấu repo là `INVALID`.
> - **Quy trình hoạt động an toàn:** Khi bấm **Update** trên Mainsail, Moonraker sẽ tải commit mới về `~/All-Config-Voron`, tự động gọi `config/scripts/install.sh` để kiểm tra an toàn (KTC-Easy symlinks, kTAMV patches), tạo bản sao lưu trong `printer_data/config_backups/`, đồng bộ sạch vào `printer_data/config/`, và khởi động lại Klipper.

**Kể từ sau bước này:**
- Trong Mainsail (mục **Settings > Machine / Update Manager**), bạn sẽ thấy mục **All-Config-Voron** hiển thị trạng thái sạch sẽ.
- Khi đẩy code mới lên GitHub từ PC (`git push`), Mainsail sẽ hiện thông báo cập nhật kèm nút **Update**.
- Bấm **Update** trên web Mainsail: máy in sẽ tự tải code, tự backup (chỉ giữ tối đa 5 bản gần nhất), tự động dọn dẹp các file `.md`, kiểm tra an toàn, đồng bộ file và khởi động lại Klipper. Hoàn toàn không cần gõ lệnh SSH.


---

## Phần 2: Bảng đối chiếu & Phân loại quản lý toàn bộ 51 file trên máy in

Đã tải và đối chiếu toàn bộ cây thư mục `/home/voron/printer_data/config` về máy tính tại:  
`extras/Config download/config-20260904-205500/`.

### Bảng phân loại chi tiết:

| Nhóm | Tên file / Thư mục | Phần mềm / Chủ thể quản lý | Trạng thái đồng bộ từ Git / PC | Ghi chú an toàn & Hướng dẫn |
| :--- | :--- | :--- | :--- | :--- |
| **Nhóm 1: Cấu hình lõi & Kinematics** | `printer.cfg` | **Git Repo (`All-Config-Voron`) & Người dùng** | **Được cập nhật từ Git** | Chứa định nghĩa MCU CAN UUID, Stepper X/Y/Z, Cartographer, Input Shaper include. **Chú ý:** Phần `#*# <SAVE_CONFIG>` ở cuối file lưu PID, Cartographer touch/scan model. Khi sửa file này trên PC, luôn đối chiếu khối SAVE_CONFIG với máy in trước khi commit. |
| **Nhóm 1: Phần cứng & Cảm biến** | `Printer-Setup/hardware.cfg` | Git Repo & Người dùng | **Được cập nhật từ Git** | Khai báo TMC2209/5160, dòng điện chạy, pinout Manta M8P V2. |
| **Nhóm 1: Quạt & Đèn LED** | `Printer-Setup/fans-leds.cfg` | Git Repo & Người dùng | **Được cập nhật từ Git** | Quạt CPAP, quạt vỏ chamber, đèn LED Stealthburner / NeoPixel. |
| **Nhóm 1: Macro in & Điều khiển** | `Printer-Setup/print-macros.cfg` | Git Repo & Người dùng | **Được cập nhật từ Git** | Chứa `PRINT_START`, `PRINT_END`, `PAUSE`, `RESUME`, `CANCEL_PRINT`. |
| **Nhóm 1: Test tốc độ & Gia tốc** | `Printer-Setup/test-speed.cfg` | Git Repo & Người dùng | **Được cập nhật từ Git** | Chứa `TEST_SPEED` (X/Y) và `TEST_Z_SPEED` (Z gantry) độc lập. |
| **Nhóm 1: Sấy nhựa (Filament Dryer)** | `Printer-Setup/filament-dryer.cfg` | Git Repo & Người dùng | **Được cập nhật từ Git** | Macro sấy nhựa trên bàn in (`DRYER_START`, `DRY_PETG`, `DRY_ABS`). |
| **Nhóm 1: Vệ sinh đầu phun & Prime** | `Printer-Setup/nozzle-clean.cfg`<br>`Printer-Setup/prime-lines.cfg` | Git Repo & Người dùng | **Được cập nhật từ Git** | Cọ silicon Bambu A1, xả nhựa từng tool T0–T4. |
| **Nhóm 1: Input Shaper & Tool Crash** | `Printer-Setup/input-shaper.cfg`<br>`Printer-Setup/tool-crash.cfg` | Git Repo & Người dùng | **Được cập nhật từ Git** | Tần số rung và bộ lọc Shaper; cấu hình cảm biến chống rơi tool. |
| **Nhóm 1: Đầu dò Cartographer** | `Printer-Setup/calibration-probe.cfg` | Git Repo & Người dùng | **Được cập nhật từ Git** | Cấu hình probe Cartographer CANbus, bed mesh 350x350. |
| **Nhóm 2: Toolchanger User Configs** | `toolchanger/toolchanger-config.cfg`<br>`toolchanger/tools/T0.cfg`<br>`toolchanger/tools/T1.cfg`<br>`toolchanger/tools/T2.cfg`<br>`toolchanger/tools/T3.cfg`<br>`toolchanger/tools/T4.cfg` | Git Repo & Người dùng | **Được cập nhật từ Git** | Tọa độ dock X/Y/Z, offset cơ khí T0–T4, nhiệt độ chờ (Standby), thông số extruder từng đầu in. |
| **Nhóm 3: KTC-Easy Plugin (Readonly)** | `toolchanger/readonly-configs/calibrate-offsets.cfg`<br>`toolchanger/readonly-configs/crash-detection.cfg`<br>`toolchanger/readonly-configs/homing.cfg`<br>`toolchanger/readonly-configs/toolchanger-include.cfg`<br>`toolchanger/readonly-configs/toolchanger-macros.cfg`<br>`toolchanger/readonly-configs/toolchanger.cfg` | **Plugin `klipper-toolchanger-easy`** | **KHÔNG CẬP NHẬT TỪ GIT THỦ CÔNG** | Đây là các symlink trỏ về `~/klipper-toolchanger-easy/`. Plugin tự quản lý cập nhật qua mục `[update_manager klipper-toolchanger-easy]`. `install.sh` sẽ từ chối chạy nếu các symlink này bị hỏng. |
| **Nhóm 4: kTAMV Service & Patches** | `Printer-Setup/ktamv.cfg`<br>`scripts/ktamv/ktamv-server.service`<br>`scripts/patches/*.patch` | **kTAMV Local Service** | **Cấu hình & patch quản lý bởi Git** | Runtime `~/kTAMV` được ghim ở commit `72421f2d` với các patch tùy biến. Không bật update tự động cho kTAMV để tránh xung đột thuật toán camera. |
| **Nhóm 5: Cấu hình dịch vụ hệ thống** | `moonraker.conf`<br>`crowsnest.conf`<br>`KlipperScreen.conf`<br>`mainsail.cfg` | **Dịch vụ hệ thống & Moonraker** | **Quản lý bởi Git, đồng bộ sang máy in** | Cấu hình camera Crowsnest (WebRTC), giao diện KlipperScreen, macro Mainsail, cổng API Moonraker. |
| **Nhóm 6: Dữ liệu động & Chẩn đoán runtime** | `Generated-Data/ShakeTune/input_shaper/*.png`<br>`.moonraker.conf.bkp`<br>`printer.cfg` (khối `SAVE_CONFIG`) | **Klippain-ShakeTune, Moonraker, Klipper Runtime** | **KHÔNG cập nhật từ Git lên máy in** (Được loại trừ bằng `.gitignore` và `install.sh`) | Biểu đồ rung ShakeTune do máy in tự tạo khi đo. Bản sao lưu `.moonraker.conf.bkp` do Moonraker tự lưu. Máy tính chỉ kéo về để lưu trữ tham khảo, không đẩy ngược lên đè máy in. |
| **Nhóm 7: Scripts cài đặt & triển khai** | `scripts/install.sh`<br>`scripts/update.sh`<br>`scripts/cleanup-voron.sh` | **Git Repo (`All-Config-Voron`)** | **Được cập nhật từ Git** | `install.sh` là script thực thi cho Update Manager, tự động kiểm tra symlink, tạo backup trước khi triển khai. |

---

## Phần 3: Tóm tắt kết quả đối chiếu SHA-256 (Repo vs Máy in thực tế)
- **44 files trùng khớp 100% (Identical byte-for-byte / normalized line-endings)** bao gồm: toàn bộ phần cứng, quạt, LED, macro in, toolchanger T0–T4, readonly-configs, patch kTAMV, scripts.
- **Khối `SAVE_CONFIG`:** 179 dòng dữ liệu hiệu chuẩn Cartographer touch/scan và PID trên repo khớp chính xác 100% với trên máy in thật.
- **Tách module thành công:** `filament-dryer.cfg` và `test-speed.cfg` đã được đồng bộ lên máy in và Klipper đang chạy ở trạng thái `ready`.
- **Cấu hình Moonraker:** Đã tích hợp sẵn section `[update_manager All-Config-Voron]` vào `moonraker.conf`.

# Cấu hình Voron 2.4 StealthChanger 5-Tool

Bộ cấu hình Klipper/Moonraker tối ưu cho hệ thống máy in **Voron 2.4 StealthChanger** trang bị 5 đầu phun độc lập.

## 🛠️ Phần cứng hệ thống
*   **Bo mạch chính:** BTT Manta M8P V2.0 + CM4.
*   **Mạch đầu phun:** 5x EBB36 V1.2 (CAN bus).
*   **Cảm biến bàn in (Probe):** Cartographer V3 CAN bus.
*   **Cân chỉnh lệch đầu in:** Cảm biến cơ khí SexBolt/SexBall (chân `PF4`/M1-STOP).
*   **Đầu phun & đùn:** Hotend TZ V6 2.0 + WW BMG Extruder.

---

## 📂 Cấu trúc Repository
*   `config/`: Thư mục cấu hình hoạt động chính. Sẽ được đồng bộ về `~/printer_data/config` trên máy in.
*   `extras/`: Các tài liệu hướng dẫn, hình ảnh, file G-code mẫu và file backup (không copy lên máy in).

---

## 🚀 Hướng dẫn Cài đặt & Cập nhật

> [!WARNING]
> Không sao chép trực tiếp thư mục gốc của repository vào `~/printer_data/config`. Hãy sử dụng các script cài đặt/cập nhật dưới đây để đảm bảo an toàn.

### 1. Cài đặt lần đầu (SSH vào máy in)
```bash
cd /tmp
git clone git@github.com:Batcandoionline/All-Config-Voron.git
cd All-Config-Voron
bash config/scripts/install.sh
```
*(Sau khi chạy xong, mở giao diện Mainsail/Fluidd và thực hiện `FIRMWARE_RESTART`)*

### 2. Cập nhật cấu hình (Sau khi sửa đổi trên GitHub)
```bash
cd ~/printer_data/config
bash scripts/update.sh
```
*(Script sẽ tự động tạo bản sao lưu tại `~/printer_data/config_backups/config-YYYYMMDD-HHMMSS` trước khi kéo mã nguồn mới về)*

---

## 📐 Quy trình Cân chỉnh nhanh (SexBolt / SexBall)

Để thiết lập lại sai số XYZ (offsets) giữa các đầu phun khi có thay đổi cơ khí:

1.  **Làm sạch đầu phun:** Lau sạch đầu in T0 và các đầu phun khác (tránh để bám nhựa thừa làm lệch cảm biến).
2.  **Homing & Cân bằng Gantry:**
    ```gcode
    G28
    QUAD_GANTRY_LEVEL
    ```
3.  **Chạy đo offset tự động:**
    ```gcode
    CALIBRATE_ALL_OFFSETS
    ```
    *(Hệ thống sẽ lần lượt đo T0, T1, T2, T3, T4 và tự động lưu kết quả)*
4.  **Khởi động lại & Kiểm tra:**
    ```gcode
    FIRMWARE_RESTART
    CHECK_OFFSETS
    ```

---

## 🛡️ Nguyên tắc Vận hành & Phát triển (Dành cho AI/Người sửa code)
*   **Bắt buộc sao lưu:** Luôn tạo bản backup trong `extras/backups/pre-...` trước khi thay đổi bất kỳ tệp cấu hình nào.
*   **Giữ sạch Git:** Không đẩy file log, dữ liệu quét rung `ShakeTune_results`, hay file cấu hình tạm `printer-*.cfg` lên GitHub.

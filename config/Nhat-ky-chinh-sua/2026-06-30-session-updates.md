# Nhật ký chỉnh sửa - 2026-06-30

## Mục tiêu
* Cập nhật gcode_z_offset cho các đầu in T1, T2, T3, T4 và ngưỡng Cartographer touch model threshold theo thông số cấu hình mới từ người dùng.
* Cập nhật lại các thông số hiệu chuẩn (coefficients, mesh points, touch threshold) mới của Cartographer sau khi thực hiện chạy lại lệnh hiệu chuẩn `CARTOGRAPHER_TOUCH_CALIBRATE`.
* Nâng cao tính bảo mật khi mở public kho lưu trữ lên GitHub.

---

## 1. Điều chỉnh cấu hình printer.cfg và đồng bộ (Phiên 1)
*   **Chi tiết thay đổi:**
    *   Sao lưu cấu hình cũ sang [printer.cfg (Backup 1)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/backups/pre-update_toolhead_offsets-20260630-170045/printer.cfg).
    *   Cập nhật ngưỡng touch threshold của `[cartographer touch_model default]` từ `1789` lên **`1968`**.
    *   Điều chỉnh giá trị bù trục `gcode_z_offset` cho các cụm đầu in:
        *   `[tool T1]`: từ `0.19799999999127493` thành **`0.20799999999127493`**.
        *   `[tool T2]`: từ `-0.22000000002525155` thành **`-0.21000000002525155`**.
        *   `[tool T3]`: từ `-0.1880000000428268` thành **`-0.1780000000428268`**.
        *   `[tool T4]`: từ `0.055999999939054135` thành **`0.065999999939054135`**.
    *   Thực hiện commit và push các thay đổi cấu hình lên kho lưu trữ GitHub chính thức.

## 2. Cập nhật dữ liệu hiệu chuẩn Cartographer Touch mới (Phiên 2)
*   **Chi tiết thay đổi:**
    *   Sao lưu cấu hình trước khi cập nhật sang [printer.cfg (Backup 2)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/backups/pre-cartographer-touch-calib-20260630-181633/printer.cfg).
    *   Cập nhật ngưỡng touch threshold của `[cartographer touch_model default]` từ `1968` lên **`2594`**.
    *   Cập nhật lại toàn bộ ma trận lưới `[bed_mesh default]` points mới thu được sau khi đo.
    *   Cập nhật các tham số mô hình `[cartographer scan_model default]` (coefficients, domain, v.v.) và hệ số cuộn dây `[cartographer coil]` calibration mới.

## 3. Cập nhật cơ chế bảo mật .gitignore trước khi Public
*   **Chi tiết thay đổi:**
    *   Cập nhật file [.gitignore ở thư mục gốc](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/.gitignore) và [config/.gitignore](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/config/.gitignore).
    *   Thêm các mẫu chặn tự động bao gồm: `*.secrets`, `moonraker.secrets`, và `wpa_supplicant.conf` để ngăn chặn các dữ liệu nhạy cảm cá nhân bị push lên GitHub trong tương lai.


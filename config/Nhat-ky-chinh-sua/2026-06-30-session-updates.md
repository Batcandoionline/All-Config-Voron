# Nhật ký chỉnh sửa - 2026-06-30

## Mục tiêu
Cập nhật gcode_z_offset cho các đầu in T1, T2, T3, T4 và ngưỡng Cartographer touch model threshold theo thông số cấu hình mới từ người dùng.

---

## 1. Điều chỉnh cấu hình printer.cfg và đồng bộ
*   **Chi tiết thay đổi:**
    *   Sao lưu cấu hình cũ sang [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/backups/pre-update_toolhead_offsets-20260630-170045/printer.cfg).
    *   Cập nhật ngưỡng touch threshold của `[cartographer touch_model default]` từ `1789` lên **`1968`**.
    *   Điều chỉnh giá trị bù trục `gcode_z_offset` cho các cụm đầu in:
        *   `[tool T1]`: từ `0.19799999999127493` thành **`0.20799999999127493`**.
        *   `[tool T2]`: từ `-0.22000000002525155` thành **`-0.21000000002525155`**.
        *   `[tool T3]`: từ `-0.1880000000428268` thành **`-0.1780000000428268`**.
        *   `[tool T4]`: từ `0.055999999939054135` thành **`0.065999999939054135`**.
    *   Thực hiện commit và push các thay đổi cấu hình lên kho lưu trữ GitHub chính thức.

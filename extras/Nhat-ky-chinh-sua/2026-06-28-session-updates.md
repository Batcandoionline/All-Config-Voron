# Nhật ký chỉnh sửa - 2026-06-28

## Mục tiêu
Cập nhật bù sai lệch trục Z (gcode_z_offset) cho các đầu in T1 và T2 sau khi người dùng thực hiện độn chiều cao các cụm công cụ lên từ 1mm đến 1.3mm và chạy căn chỉnh lại.

---

## 1. Điều chỉnh bù trục Z cho T1 và T2
*   **Chi tiết thay đổi:**
    *   Sao lưu cấu hình cũ sang [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/backups/pre-tool-offsets-adj-20260628-081900/printer.cfg).
    *   Tăng giá trị `gcode_z_offset` của `[tool T1]` thêm **+0.03mm**: Từ `0.19799999999127493` thành **`0.22799999999127493`**.
    *   Tăng giá trị `gcode_z_offset` của `[tool T2]` thêm **+0.01mm**: Từ `-0.22000000002525155` thành **`-0.21000000002525155`**.

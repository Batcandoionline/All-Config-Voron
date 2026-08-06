# Bản ghi sao lưu

- **Ngày:** 2026-08-05 20:15:00
- **Tác vụ:** Sửa lỗi Move out of range (Y = -10.041 vượt giới hạn position_min: -10 trong stepper_y) khi chạy CLEAN_NOZZLE
- **File đã sao lưu:**
  - `nozzle-clean.cfg` — Giảm nhẹ bán kính vòng quét `circle_r` từ 2.0 xuống 1.5mm và đặt `brush_cy = -8.0` để Y hoàn toàn $\ge -9.5\text{mm}$, không bao giờ vượt giới hạn $Y = -10\text{mm}$.
- **Nhật ký liên quan:** [2026-08-05-session-updates.md](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/Nhat-ky-chinh-sua/2026-08-05-session-updates.md)

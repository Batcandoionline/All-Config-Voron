# Nhật ký — 2026-09-03

## 1. Nâng giới hạn tốc độ và gia tốc máy in để thử nghiệm hiệu năng

### Mục tiêu
Cập nhật các tham số giới hạn chuyển động trong section `[printer]` của `printer.cfg` để thử nghiệm khả năng tăng tốc, rút ngắn thời gian di chuyển và in ấn theo yêu cầu của người vận hành.

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — Điều chỉnh các giới hạn kinematics: `max_velocity`, `max_accel`, `max_z_velocity`, `max_z_accel`.

### Sao lưu
- [printer.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-tune-velocity-accel-limits-20260903-073100/printer.cfg)

### Chi tiết thay đổi
- Tham số `max_velocity`: `300` → `350` (mm/s)
- Tham số `max_accel`: `4000` → `7000` (mm/s²)
- Tham số `max_z_velocity`: `60` → `70` (mm/s)
- Tham số `max_z_accel`: `700` → `900` (mm/s²)

### Lý do
1. **Rút ngắn thời gian di chuyển (Travel):** Tốc độ travel 350 mm/s khớp với cấu hình trong OrcaSlicer (`travel_speed = 350`), cho phép đầu in khai thác tối đa tốc độ khi di chuyển giữa các đầu in và tháp lau (wipe tower).
2. **Thử nghiệm gia tốc cao:** Nâng gia tốc tối đa lên 7000 mm/s² để thử nghiệm khả năng đáp ứng cơ khí của khung máy Voron 2.4 CoreXY.
3. **Lưu ý kỹ thuật & Giám sát:** Tần số cộng hưởng trục Y đo thực tế của các tool là ~35 Hz (MZV). Ở gia tốc 7000 mm/s², thuật toán Input Shaper có thể làm mượt (smoothing) biên dạng góc nhọn trên sản phẩm in. Đồng thời, trục Z tăng lên 70 mm/s và 900 mm/s² cần giám sát chặt chẽ trong quá trình pick/drop tool ở dock StealthChanger để đảm bảo không bị trượt bước.

### Kiểm tra
- Kiểm tra cú pháp Klipper: Đạt chuẩn cú pháp Klipper ini.
- Trạng thái các section include và khối SAVE_CONFIG: Được giữ nguyên vẹn 100%.

### Kết quả
Đã áp dụng thông số mới vào file cấu hình `printer.cfg` sẵn sàng cho người dùng nạp và kiểm tra thực tế.

### Vấn đề còn lại
- Chạy `FIRMWARE_RESTART` trên Mainsail để nạp cấu hình mới.
- Theo dõi quá trình dock/undock tool và kiểm tra chất lượng góc in xem có bị bo tròn do smoothing không.

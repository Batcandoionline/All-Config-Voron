# Nhật ký — 2026-07-12

## 1. Đưa tool về dock và đỗ shuttle an toàn khi kết thúc in

### Mục tiêu
Cất đầu in đang sử dụng về dock của nó khi kết thúc lệnh in (thay vì tự động load T0) và đỗ shuttle trống ở vị trí Y an toàn để tránh kịch khung khi Home Y ở lần in tiếp theo.

### File đã sửa đổi
- `config/Printer-Setup/print-macros.cfg` — Sửa đổi các bước 4 và 5 trong macro `PRINT_END` để gọi lệnh `UNSELECT_TOOL` thay vì `T0`, và đổi tọa độ Y đỗ shuttle từ `th.axis_maximum.y - 2` thành `th.axis_maximum.y - 20`.

### Sao lưu
- [print-macros.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-dock-tools-on-print-end-20260712-160215/print-macros.cfg)

### Chi tiết thay đổi
- Step 4 trong `PRINT_END`: chuyển đổi từ việc tự động chọn `T0` khi `active_tool > 0` sang gọi `UNSELECT_TOOL` nếu `active_tool >= 0` (cất bất kỳ tool đang hoạt động nào về dock).
- Step 5 trong `PRINT_END`: đổi tọa độ đỗ từ `Y{th.axis_maximum.y - 2}` thành `Y{th.axis_maximum.y - 20}`.

### Lý do
- Hạn chế việc shuttle luôn mang theo tool T0 sau khi in xong. Cất toàn bộ tool giúp đầu in gọn gàng, giảm hao mòn cơ cấu lò xo trên carriage khi không in.
- Tránh tình trạng đỗ quá gần giới hạn tối đa trục Y (336mm), điều này dễ gây lỗi cơ học hoặc kịch khung gầm khi máy bắt đầu quá trình homing Y ở lượt in mới (do không đủ không gian rút lui/giảm tốc).

### Kiểm tra
- Kiểm tra cú pháp: đạt.
- Khởi động lại Klipper: (người dùng thực hiện trên máy in thực tế)
- Thử in: (người dùng thực hiện trên máy in thực tế)

### Kết quả
Chờ người dùng khởi động lại Klipper và chạy thử macro kết thúc in.

### Vấn đề còn lại
Không có.

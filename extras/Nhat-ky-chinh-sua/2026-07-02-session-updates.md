# Nhật ký xử lý sự cố - 2026-07-02

## Mục tiêu
* Ghi nhận sự cố mất kết nối MCU Cartographer (cảm biến probe) gây treo máy in ở trạng thái khởi động (`STARTUP`) và hướng xử lý thành công để làm tài liệu tra cứu/sửa chữa về sau.

---

## 1. Chi tiết sự cố kết nối MCU Cartographer
* **Hiện tượng**: Máy in bị treo, Mainsail báo lỗi Klipper ở trạng thái `STARTUP` và không thể chuyển sang sẵn sàng (Disconnect). 
* **Phân tích nhật ký**:
    * Theo [klippy.log](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/logs/klippy.log), trước khi sự cố xảy ra, Klipper hoạt động bình thường. Phiên làm việc cũ dừng đột ngột mà không có log crash (nhiệt độ chip Cartographer lúc đó ở mức khá cao là `66.1°C`).
    * Khi hệ thống khởi động lại, Klipper kết nối thành công với các MCU của toolhead (`EBB2`, `EBB3`, `EBB4`) nhưng liên tục gặp lỗi timeout với `cartographer` (UUID: `da13d909ce34` trong [hardware.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/config/Printer-Setup/hardware.cfg#L44-L46)):
      ```text
      mcu 'cartographer': Timeout on connect
      serialhdl.error: mcu 'cartographer': Serial connection closed
      ```
* **Nguyên nhân dự đoán**:
    1. **Kẹt trạng thái MCU**: Khi máy chủ Klipper hoặc hệ thống bị khởi động lại đột ngột nhưng nguồn 24V cấp cho Cartographer chưa được ngắt hẳn, MCU của Cartographer không được reset vật lý và bị kẹt giao tiếp cũ, dẫn tới không nhận diện được tín hiệu bắt tay mới từ Klipper.
    2. **Quá nhiệt**: Nhiệt độ chip Cartographer khá cao trước lúc treo có thể làm tê liệt IC CAN hoặc MCU tạm thời.

## 2. Hướng xử lý đã thực hiện thành công
* **Giải pháp**: Tiến hành tắt nguồn điện chính của máy in hoàn toàn (ngắt điện nguồn cấp 24V), đợi 1 phút để toàn bộ tụ điện xả hết điện tích và reset cứng lại tất cả các MCU (bao gồm Cartographer).
* **Kết quả**: Sau khi bật lại nguồn, Klipper đã nhận diện được Cartographer bình thường, máy in khởi động thành công và trở lại trạng thái sẵn sàng (`Ready`).

# Nhật ký chỉnh sửa - 2026-06-26

## Mục tiêu
Tối ưu hóa quy trình ngâm nhiệt (Heat Soak) trong macro `PRINT_START` để giảm thiểu thời gian chờ đợi khi bắt đầu một bản in mới ngay sau khi bản in trước vừa hoàn thành (khi bàn in vẫn còn nóng).

---

## 1. Tối ưu hóa thời gian ngâm nhiệt động (Dynamic Heat Soak)
*   **Vấn đề:** Trước đây, cơ chế ngâm nhiệt chỉ kiểm tra nếu sự chênh lệch nhiệt độ bàn in hiện tại và nhiệt độ mục tiêu lớn hơn 5°C thì sẽ tiến hành ngâm nhiệt toàn bộ thời gian đã cấu hình (ví dụ: 90 giây đối với ABS). Điều này dẫn đến việc nếu vừa in xong và bàn in vẫn còn rất nóng (chỉ giảm khoảng 6°C), máy in vẫn bắt đầu ngâm nhiệt lại từ đầu 90 giây, gây lãng phí thời gian không cần thiết.
*   **Thay đổi cấu hình:**
    *   Sao lưu cấu hình cũ sang [print-macros.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/backups/pre-soak-optimization-20260626-202800/print-macros.cfg).
    *   Cập nhật logic trong macro `_PRINT_START_HEAT_SOAK` tại [print-macros.cfg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/config/Printer-Setup/print-macros.cfg) để tính toán sự chênh lệch nhiệt độ giữa lúc bắt đầu nhận lệnh in (`BED_START`) và nhiệt độ mục tiêu (`BED_TEMP`):
        *   **Bàn in lạnh (`temp_diff > 15°C`):** Thực hiện ngâm nhiệt toàn bộ thời gian mặc định của vật liệu (PLA/TPU: 30s, PETG: 60s, ABS/ASA/PC/NYLON/PA: 90s).
        *   **Bàn in ấm (`5°C < temp_diff <= 15°C`):** Giảm thời gian ngâm nhiệt xuống còn **20%** so với mặc định (ví dụ: ABS chỉ ngâm 18 giây thay vì 90 giây).
        *   **Bàn in nóng (`temp_diff <= 5°C`):** Bỏ qua hoàn toàn bước ngâm nhiệt vì bàn in và buồng in đã đủ ổn định nhiệt độ từ bản in trước.

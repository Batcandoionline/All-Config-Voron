# Nhật ký — 2026-07-07

## 1. Giải đáp thắc mắc về cách hoán đổi màu in trong Orca Slicer

### Mục tiêu
Giải thích cho người dùng cách hoán đổi các màu sắc (filament/tool) đã được tô (painted) sẵn trên mô hình 3D trong Orca Slicer mà không cần thay đổi vị trí các cuộn nhựa thực tế trên máy in hoặc hệ thống đổi màu (AMS/Toolchanger).

### Phân tích phản hồi
Người dùng phản hồi không tìm thấy nút hoán đổi như miêu tả ban đầu. Nguyên nhân có thể do:
1. Máy in chạy Klipper (Voron 5-Tool) kết nối qua Moonraker API nên khi "Print/Send" không có giao diện map màu tự động của AMS (Bambu Lab).
2. Mô hình là dạng **Multi-part** (nhiều chi tiết ghép lại) được gán màu theo danh sách đối tượng (Object list) chứ không phải vẽ bằng cọ vẽ (Color painting) nên không có nút **Remap Filaments** trong bảng Paint.

### Giải pháp bổ sung
1. **Đối với mô hình Multi-part:** Thay đổi gán Filament Slot trực tiếp cho các Part trong tab **Objects** ở sidebar trái.
2. **Đối với mô hình tô màu (Color Painted):** Dùng mẹo đổ màu trung gian thông qua công cụ **Fill (Đổ đầy)** trong chế độ Paint [N] để hoán đổi màu nhanh chóng mà không làm hỏng thiết kế.

### Kết quả
Đã bổ sung hướng dẫn chi tiết các phương án thay thế phù hợp với thực tế sử dụng của người dùng.

---

## 2. Cập nhật tọa độ đỗ (params_park_y) cho các toolhead T1, T2, T3

### Mục tiêu
Cập nhật tọa độ trục Y của dock đỗ (`params_park_y`) cho các toolhead T1, T2 và T3 theo dữ liệu thực tế đo đạc của người dùng để cải thiện độ chính xác và an toàn khi nhả/nhận tool.

### File đã sửa đổi
- `config/toolchanger/tools/T1.cfg` — thay đổi `params_park_y`
- `config/toolchanger/tools/T2.cfg` — thay đổi `params_park_y`
- `config/toolchanger/tools/T3.cfg` — thay đổi `params_park_y`

### Sao lưu
- Thư mục sao lưu: [pre-update-park-coordinates-20260707-172000](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-update-park-coordinates-20260707-172000/)
  - `T1.cfg` (bản gốc)
  - `T2.cfg` (bản gốc)
  - `T3.cfg` (bản gốc)
  - `README.md` (bản ghi sao lưu chi tiết)

### Chi tiết thay đổi
- **T1.cfg**:
  - `params_park_y: 1.9` $\rightarrow$ `params_park_y: 1.5`
- **T2.cfg**:
  - `params_park_y: 2.3` $\rightarrow$ `params_park_y: 2.1`
- **T3.cfg**:
  - `params_park_y: 2.5` $\rightarrow$ `params_park_y: 2.3`
- *Lưu ý:* Các thông số của T0 và T4 trùng với giá trị hiện tại nên không có sửa đổi.

### Lý do
Tọa độ vật lý của các dock StealthChanger có thể bị xê dịch nhẹ theo thời gian hoặc sau khi hiệu chuẩn lại cơ khí. Việc cập nhật các giá trị này giúp quá trình đỗ toolhead chính xác hơn, tránh va chạm cơ khí và giảm lực cản không cần thiết lên hệ thống chuyển động.

### Kiểm tra
- Kiểm tra cú pháp: ✅ Đạt — cấu hình Klipper cho các toolhead T1, T2, T3 có cú pháp hợp lệ.
- Khởi động lại Klipper: ⏳ Người dùng cần restart Klipper (`FIRMWARE_RESTART`) để cấu hình mới có hiệu lực.

### Kết quả
Đã áp dụng các tọa độ đỗ mới thành công.

---


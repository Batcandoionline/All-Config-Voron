# Nhật ký — 2026-09-01

## 1. Cập nhật Z-offset 5-Tool theo đo đạc Cartographer Touch Accuracy

### Mục tiêu
Đo đạc và hiệu chuẩn lại độ lệch Z-offset giữa 5 tool (T0–T4) bằng đầu dò Cartographer Touch trong điều kiện nhiệt độ ổn định (Bed 60°C, Nozzle 150°C).

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — cập nhật `gcode_z_offset` trong khối `SAVE_CONFIG` cho T1, T2, T3, T4

### Sao lưu
- [printer.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cartographer-touch-z-offsets-20260901-075800/printer.cfg)

### Chi tiết thay đổi

| Toolhead | Giá trị cũ | Giá trị mới | Chênh lệch ($\Delta$) | Dữ liệu đo thực nghiệm (Median) |
|---|---:|---:|---:|---:|
| **T0** | `0.0000` | `0.0000` | `0.0000` | `+0.002552` (Mốc chuẩn sau Touch Home) |
| **T1** | `0.2464` | `0.2240` | `-0.0224` | `+0.226552` |
| **T2** | `-0.2688` | `-0.3160` | `-0.0472` | `-0.313448` |
| **T3** | `-0.1896` | `-0.1920` | `-0.0024` | `-0.189448` |
| **T4** | `0.1028` | `0.0720` | `-0.0308` | `+0.074552` |

### Lý do
Người vận hành đã thực hiện chuỗi đo thủ công bằng lệnh `CARTOGRAPHER_TOUCH_ACCURACY` tại tọa độ $(X=174, Y=168)$ ở nhiệt độ Bed 60°C và Nozzle 150°C. Kết quả đo có độ lặp lại cao, T3 trùng khớp cấu hình trước đó, độ trôi của T0 đạt ngưỡng kiểm soát của Cartographer Touch model.

### Kiểm tra
- **Kiểm tra cú pháp Klipper:** Đạt, đúng cú pháp số thực trong khối `SAVE_CONFIG`.
- **Cấu trúc tool section:** Đạt, giữ nguyên `gcode_x_offset`, `gcode_y_offset` và các section khác.

### Kết quả
Bộ thông số Z-offset đo thực tế đã được đồng bộ an toàn vào `printer.cfg`.

### Vấn đề còn lại
- Người vận hành chạy `FIRMWARE_RESTART` trên Mainsail / máy in.
- Chạy macro `CHECK_OFFSETS` để xác nhận KTC nhận diện đúng bảng offset mới.
- In test first-layer 5 tool để kiểm chứng độ đè lớp in thực tế ở 250°C.

---

## 2. Tinh chỉnh Z-offset 5-Tool theo kết quả in thực tế First Layer

### Mục tiêu
Cập nhật lại bộ thông số Z-offset cho các tool T1–T4 dựa trên đánh giá trực quan và độ ép sợi lớp in đầu tiên (first layer print test).

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — cập nhật `gcode_z_offset` trong khối `SAVE_CONFIG` cho T1, T2, T3, T4

### Sao lưu
- [printer.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-first-layer-z-offset-tune-20260901-092000/printer.cfg)

### Chi tiết thay đổi

| Toolhead | Giá trị đo Touch (Mục 1) | Giá trị in thực tế (Mới) | Điều chỉnh ($\Delta$) | Trạng thái lớp in |
|---|---:|---:|---:|---|
| **T0** | `0.0000` | `0.0000` | `0.0000` | Chuẩn mốc quy chiếu |
| **T1** | `0.2240` | `0.2360` | `+0.0120` | Khắc phục ép quá sát/cào nhẹ, sợi đè đều |
| **T2** | `-0.3160` | `-0.2920` | `+0.0240` | Khắc phục ép quá sát/cào nhẹ, sợi đè đều |
| **T3** | `-0.1920` | `-0.1896` | `+0.0024` | Trả về thông số chuẩn in đẹp đã kiểm chứng |
| **T4** | `0.0720` | `0.1200` | `+0.0480` | Nâng cao độ phù hợp độ giãn nở nhiệt in thực tế |

### Lý do
Sau khi áp dụng bộ Z-offset đo thô từ Cartographer Touch ở $150^\circ\text{C}$ (`0.2240, -0.3160, -0.1920, 0.0720`), bản in thử nghiệm lớp 1 cho kết quả chưa đạt thẩm mỹ (ép quá chặt ở T1, T2 và chưa tối ưu ở T4). Người vận hành đã tinh chỉnh trực tiếp sang bộ giá trị có bù trôi tuyến tính và giãn nở nhiệt ở nhiệt độ in thực tế: `T1: 0.2360, T2: -0.2920, T3: -0.1896, T4: 0.1200`.

### Kiểm tra
- **Kiểm tra cú pháp Klipper:** Đạt, đúng cú pháp trong khối `SAVE_CONFIG`.
- **Tính nhất quán cấu hình:** Đạt, khớp với các quyết định kỹ thuật ưu tiên chất lượng in thực tế trong DECISIONS.md.

### Kết quả
Bộ thông số Z-offset in thực tế đẹp đã được lưu và cập nhật hoàn tất vào `printer.cfg`.

### Vấn đề còn lại
- Chạy `FIRMWARE_RESTART` và xác nhận bảng offset mới bằng `CHECK_OFFSETS`.

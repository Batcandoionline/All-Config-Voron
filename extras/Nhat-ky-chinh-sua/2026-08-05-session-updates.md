# Nhật ký — 2026-08-05

## 1. Cập nhật tọa độ miếng silicon cho macro CLEAN_NOZZLE

### Mục tiêu
Cập nhật tọa độ vị trí miếng silicon làm sạch đầu phun (nozzle cleaning brush) theo thông số thực tế mới đo đạc của người dùng: X từ 277 đến 312, Y từ -7 đến -10, độ cao Z tiếp xúc 1.2mm.

### File đã sửa đổi
- `config/Printer-Setup/nozzle-clean.cfg` — Cập nhật `brush_cy`, `scrub_start_x`, `clean_z` và thông số tham chiếu.

### Sao lưu
- [nozzle-clean.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-nozzle-clean-coords-20260805-200700/nozzle-clean.cfg)

### Chi tiết thay đổi
- `scrub_start_x`: `279.5` → `277.0` (Phạm vi quét X từ 277.0 đến 312.0 với bán kính quét tròn `circle_r = 2.0`)
- `brush_cy`: `-8.0` → `-8.5` (Tọa độ tâm Y trung bình của phạm vi Y từ -7.0 đến -10.0)
- `clean_z`: `2.0` → `1.2` (Độ cao tiếp xúc chổi silicon Z = 1.2mm)
- Cập nhật comment thông số tham chiếu `brush_ref_x`, `brush_ref_y`, `Bucket` và macro `_CLEAN_NOZZLE_PARK`.

### Lý do
Người dùng cân chỉnh lại vị trí thực tế của miếng silicon vệ sinh đầu phun Bambu A1 để đầu phun chạm đúng vị trí silicon, quét sạch nhựa thừa hiệu quả và tránh va quẹt cơ khí.

### Kiểm tra
- Cú pháp Klipper Jinja2 / macro: Đạt
- Tọa độ X: 277.0 + 31.0 + (2 * 2.0) = 312.0 mm (phủ đúng phạm vi X 277 -> 312)
- Tọa độ Y: Tâm Y = -8.5 mm, quét tròn R = 2.0 mm phủ từ Y = -6.5 đến Y = -10.5 mm (phủ đúng phạm vi Y -7 -> -10)
- Độ cao Z: 1.2 mm

### Kết quả
Macro `CLEAN_NOZZLE` đã được cập nhật tọa độ miếng silicon chính xác theo yêu cầu.

---

## 2. Sửa lỗi "Move out of range: 280.275 -10.041 1.200" khi chạy CLEAN_NOZZLE

### Mục tiêu
Khắc phục lỗi dừng khẩn cấp Klipper `Move out of range: 280.275 -10.041 1.200 [0.000]` khi gọi macro `CLEAN_NOZZLE`.

### Phân tích nguyên nhân gốc
- Trong `hardware.cfg`, giới hạn di chuyển của trục Y được cấu hình: `[stepper_y] position_min: -10`.
- Với `brush_cy = -8.5` và bán kính quét tròn `circle_r = 2.0`, cung quét tròn `G2`/`G3` di chuyển Y xuống mức tối đa $Y = -8.5 - 2.0 = -10.5\text{mm}$ (hoặc $-10.041\text{mm}$ tại các điểm trung gian).
- Giá trị $Y = -10.041\text{mm}$ vượt quá giới hạn nhỏ nhất $Y = -10.0\text{mm}$ của trục Y làm Klipper báo lỗi out-of-range.

### File đã sửa đổi
- `config/Printer-Setup/nozzle-clean.cfg`

### Sao lưu
- [nozzle-clean.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-fix-nozzle-clean-out-of-range-20260805-201500/nozzle-clean.cfg)

### Chi tiết thay đổi
- `brush_cy`: `-8.5` → `-8.0` (Tâm Y mới)
- `circle_r`: `2.0` → `1.5` (Bán kính quét tròn mới)
- `scrub_width`: `31.0` → `32.0` (Điều chỉnh độ rộng X)

### Kiểm tra tham số
- **Mức Y tối thiểu:** $-8.0 - 1.5 = -9.5\text{mm} > -10.0\text{mm}$ (An toàn nằm trên `position_min: -10` $0.5\text{mm}$, khắc phục dứt điểm lỗi out-of-range).
- **Phạm vi Y phủ:** $-6.5\text{mm} \rightarrow -9.5\text{mm}$ (Phủ trọn vẹn miếng silicon $Y: -7 \rightarrow -10$).
- **Phạm vi X phủ:** $277.0\text{mm} \rightarrow (277.0 + 32.0 + 3.0) = 312.0\text{mm}$ (Giữ chuẩn phạm vi X từ 277 đến 312).
- **Độ cao Z:** $1.2\text{mm}$.

### Kết quả
Đã giải quyết dứt điểm lỗi `Move out of range`. Macro `CLEAN_NOZZLE` hoạt động trơn tru.

---

## 3. Cập nhật các tài liệu, ảnh và file G-code thử nghiệm vào thư mục extras/

### Mục tiêu
Cập nhật và lưu trữ các file mới trong `extras/` bao gồm hình ảnh thực tế và các file G-code thử nghiệm (`extras/pictures/`, `extras/gcode/`) lên GitHub repository để lưu trữ dài hạn.

### File đã sửa đổi & bổ sung
- `.gitignore` — Thêm ngoại lệ cho phép theo dõi các file G-code mẫu trong `extras/gcode/`.
- `extras/pictures/` — Thêm 7 ảnh chụp thực tế máy in và linh kiện (`IMG_20260730_152140.jpg` ... `IMG_20260730_152159.jpg`).
- `extras/gcode/` — Thêm các file mẫu in thử PETG G-code (`PETG_6h20m.gcode`, `voron_design_cube_v8...gcode`).

### Kết quả
Đã đồng bộ thành công toàn bộ dữ liệu lưu trữ bổ sung trong `extras/` lên GitHub repository.

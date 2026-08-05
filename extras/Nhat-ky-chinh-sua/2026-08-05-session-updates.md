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

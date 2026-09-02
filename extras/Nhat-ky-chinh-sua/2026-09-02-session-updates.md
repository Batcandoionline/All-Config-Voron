# Nhật ký — 2026-09-02

## 1. Cập nhật quản lý Pressure Advance theo Filament Profile trong OrcaSlicer

### Mục tiêu
Cập nhật trạng thái quản lý Pressure Advance (PA) của hệ thống StealthChanger 5-tool: PA được hiệu chuẩn và áp dụng trực tiếp theo từng profile filament trong OrcaSlicer (`Orca Config/`) thay vì cấu hình tĩnh trong file Klipper của từng tool.

### File đã sửa đổi
- `.agents/TODO.md` — Đánh dấu hoàn thành hạng mục tinh chỉnh Pressure Advance theo từng loại nhựa trong OrcaSlicer.
- `.agents/DECISIONS.md` — Bổ sung quyết định kỹ thuật ngày 2026-09-02 về quản lý PA ở tầng Slicer thay vì gán tĩnh trong Klipper.
- `Voron 5 Tool/README.md` — Cập nhật mô tả trạng thái PA sang quản lý động qua OrcaSlicer profile và gỡ khỏi danh sách công việc chờ.
- `Voron 5 Tool/README.vi.md` — Cập nhật bản tiếng Việt tương ứng cho README.

### Chi tiết thay đổi

#### Bảng thông số Pressure Advance trong các profile filament hiện tại:

| Nhóm nhựa | Profile Filament | Giá trị PA (`pressure_advance`) | Kích hoạt PA |
|---|---|---:|---|
| **ABS** | `ABS Tpoimns Pink` | `0.030` | Bật (`1`) |
| **ABS** | `ABS Tpoimns Black` | `0.030` (Kế thừa generic / kích hoạt) | Bật (`1`) |
| **ABS** | `ABS-Pro Tinmory Black` | `0.030` (Kế thừa generic / kích hoạt) | Bật (`1`) |
| **PETG** | `PETG Kabber Blue` | `0.060` | Bật (`1`) |
| **PETG** | `PETG Bambu Basic Black` | `0.066` | Bật (`1`) |
| **PETG** | `PETG TPoimns White` | `0.068` | Bật (`1`) |
| **PETG** | `PETG TPoimns Black` | `0.070` | Bật (`1`) |
| **PETG** | `PETG Noname Antums` | `0.070` | Bật (`1`) |
| **PETG** | `PETG Tinmory Black` | `0.072` | Bật (`1`) |
| **PETG** | `PETG TPoimns Gray` | `0.072` | Bật (`1`) |
| **PETG** | `PETG TPoimns Red` | `0.072` | Bật (`1`) |
| **PETG** | `PETG TPoimns Yellow` | `0.072` | Bật (`1`) |
| **PETG** | `PETG TPoimns Orange` | `0.074` | Bật (`1`) |

### Lý do
1. **Linh hoạt đa vật liệu:** Với 5 toolchanger, bất kỳ đầu in nào cũng có thể được nạp các cuộn nhựa khác nhau (màu sắc, độ chảy, hãng sản xuất) giữa các lần in. Việc gán cứng một giá trị PA tĩnh trong `tools/T0.cfg`...`T4.cfg` của Klipper sẽ làm sai lệch chất lượng in khi đổi loại nhựa.
2. **Tự động hóa hoàn toàn qua G-code:** OrcaSlicer tự động chèn lệnh `SET_PRESSURE_ADVANCE ADVANCE=...` mỗi khi chuyển đổi tool và nạp loại filament tương ứng trong quá trình in.
3. **Phân tách trách nhiệm hệ thống:** Klipper chịu trách nhiệm cơ khí (kinematics, offsets, shaper), Slicer chịu trách nhiệm quản lý đặc tính vật liệu (nhiệt độ, flow ratio, pressure advance).

### Kiểm tra
- **Kiểm tra JSON Profile:** Tất cả 15 profile filament trong `Orca Config/` có cấu trúc JSON chuẩn, parse thành công bởi script `Sync-OrcaProfiles.ps1`.
- **Kiểm tra G-code xuất ra:** Các file G-code đa màu trong `extras/gcode/` đều ghi nhận các lệnh `SET_PRESSURE_ADVANCE` chính xác theo từng filament được nạp cho từng tool.

### Kết quả
Hạng mục Pressure Advance theo từng loại nhựa đã được đóng hoàn tất trong danh sách TODO và tài liệu hóa đầy đủ.

### Vấn đề còn lại
- Tiếp tục theo dõi các hạng mục TODO còn lại: Tối ưu hóa biểu đồ quạt đầu in và cơ chế giám sát nhiệt Cartographer.

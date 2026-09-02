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

---

## 2. Nâng cấp hệ thống hóa macro CLEAN_NOZZLE 2 giai đoạn (Silicone Pad + Brush 2 tốc độ)

### Mục tiêu
Chuyển đổi và hệ thống hóa macro làm sạch đầu in tham khảo từ cộng đồng StealthChanger thành cấu trúc macro tham số hóa toàn diện (`variable_...` & runtime parameters), hỗ trợ tùy biến linh hoạt tọa độ $(X, Y, Z)$, bước quét zíc-zắc, xoay tròn cung $G2$ trên silicon và chải chổi 2 cấp tốc độ ($F2000$ & $F12000$).

### File đã sửa đổi
- `Voron 5 Tool/config/Printer-Setup/nozzle-clean.cfg` — Tái cấu trúc macro `CLEAN_NOZZLE`, `_CLEAN_NOZZLE_PARK`, `PURGE_AND_CLEAN`.
- `Voron 5 Tool/README.md` — Cập nhật bảng thông số và ví dụ gọi macro vệ sinh.
- `Voron 5 Tool/README.vi.md` — Cập nhật bản tiếng Việt cho tài liệu README.

### Sao lưu
- [nozzle-clean.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-parameterized-nozzle-clean-20260902-200100/nozzle-clean.cfg)

### Chi tiết thay đổi

1. **Hệ thống hóa bảng biến cấu hình (`[gcode_macro CLEAN_NOZZLE]`):**
   - **Vùng an toàn & Khay Purge:** `variable_safe_z: 15.0`, `variable_travel_speed: 12000`, `variable_bucket_x: 320.0`, `variable_bucket_y: -8.0`.
   - **Vùng 1 - Miếng đệm Silicon:**
     - Tọa độ: `variable_pad_start_x: 130.0`, `variable_pad_end_x: 140.0`, các đường $Y$: `5.0, 6.0, 8.0`.
     - Độ cao tiếp xúc: `variable_pad_z: 0.1`.
     - Xoay tròn cung `G2`: `variable_pad_swirl_count: 20`, $I = 0.5, J = 0.5$, tốc độ $F600$.
     - Quét zíc-zắc chậm: tốc độ $F200$ bám dính lột mảng nhựa.
   - **Vùng 2 - Chổi kim loại/lông cước (2 cấp tốc độ):**
     - Tọa độ: `variable_brush_start_x: 164.0`, `variable_brush_end_x: 180.0`.
     - 2 đường $Y$: `variable_brush_y_med: 3.0` và `variable_brush_y_fast: 1.0`.
     - Độ sâu ngập chổi: `variable_brush_z: -0.8`, độ nhấc chuyển đường: `variable_brush_hop_z: 0.5`.
     - 2 cấp tốc độ: $F2000$ (quét sạch rãnh nozzle) và $F12000$ (flick nhanh gạt tơ nhựa).
2. **Hỗ trợ tham số ghi đè khi gọi (Runtime Overrides):**
   - `CLEAN_NOZZLE TEMP=... WIPES=... PURGE=... PURGE_TEMP=...`
   - `CLEAN_NOZZLE SKIP_PAD=1` / `CLEAN_NOZZLE SKIP_BRUSH=1`
   - `CLEAN_NOZZLE PAD_Z=... BRUSH_Z=...`
3. **An toàn phần cứng StealthChanger:**
   - Kiểm tra chặt chẽ `printer.toolchanger.tool_number >= 0` trước khi di chuyển.
   - Luôn nâng $Z \ge 15\text{mm}$ khi di chuyển tiếp cận trạm.
   - Thiết kế nhấc Z nhẹ khi chuyển vùng để tránh tì đè lực ngang quá mức lên chốt khóa shuttle.

### Kiểm tra
- **Kiểm tra cú pháp Klipper:** Đạt, cú pháp Jinja2 và Klipper Macro chuẩn xác.
- **Tính tương thích:** Hoàn toàn tương thích với `_CLEAN_NOZZLE_PARK`, `PURGE_AND_CLEAN`, `PRINT_START` và các hiệu ứng LED trạng thái.
- **Giới hạn chuyển động:** Toàn bộ tọa độ mặc định nằm trong hành trình máy in ($X: 0 \dots 348$, $Y: -10 \dots 336$, $Z: -5 \dots 347$).

### Kết quả
Hệ thống macro vệ sinh đầu in mới đã được nạp hoàn chỉnh, cho phép người vận hành dễ dàng căn chỉnh tọa độ trạm $X/Y/Z$ bất kỳ lúc nào ngay trong file cấu hình.

### Vấn đề còn lại
- Người vận hành chạy `FIRMWARE_RESTART` trên Mainsail.
- Khuyến nghị chạy thử nghiệm kiểm tra quỹ đạo không chạm ở $Z$ cao trước khi hạ $Z$ xuống mức tiếp xúc làm sạch thực tế.


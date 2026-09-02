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

## 2. Nâng cấp hệ thống hóa macro CLEAN_NOZZLE theo phương pháp chà trực tiếp trên tấm PEI (PEI Bed Rub & Edge Wipe)

### Mục tiêu
Chuyển đổi hoàn toàn cơ chế làm sạch đầu in sang phương pháp chà miết trực tiếp trên bề mặt mép tấm PEI (PEI Bed Rubbing & Edge Flicking), loại bỏ sự phụ thuộc vào khay/chổi phụ bên ngoài mép bàn in. Cung cấp bảng biến cấu hình tham số hóa đầy đủ và alias `CLEAR_NOZZLE`.

### File đã sửa đổi
- `Voron 5 Tool/config/Printer-Setup/nozzle-clean.cfg` — Tái cấu trúc macro `CLEAN_NOZZLE`, bổ sung `CLEAR_NOZZLE`, `_CLEAN_NOZZLE_PARK`, `PURGE_AND_CLEAN`.
- `Voron 5 Tool/README.md` — Cập nhật tài liệu kỹ thuật và bảng thông số PEI Bed Rub.
- `Voron 5 Tool/README.vi.md` — Cập nhật bản tiếng Việt cho README.

### Sao lưu
- [nozzle-clean.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-pei-bed-rub-clean-20260902-200600/nozzle-clean.cfg)

### Chi tiết thay đổi

1. **Nguyên lý hoạt động 2 giai đoạn trên tấm PEI:**
   - **Giai đoạn 1 — Ép dính & Xoay tròn trên mặt PEI ($Z = 0.1\text{mm}$):**
     - Tiếp cận `X=125, Y=5` $\rightarrow$ hạ xuống tiếp xúc $Z = 0.1\text{mm}$.
     - 3 vòng xoay cung tròn $G2$ ($I=0.5, J=0.5$) ở tốc độ $F600$.
     - Quét zíc-zắc chậm $F200$ qua các đường $Y=5 \rightarrow 6 \rightarrow 8$ ($X=130 \dots 140$) để màng nhựa mềm bám dính chắc vào lớp phủ nhám của PEI.
     - Xoay liên tục 21 vòng cung tròn $G2$ ở $F600$ để cuộn và bóc sạch nhựa bẩn quanh vát đầu phun.
   - **Giai đoạn 2 — Miết mép tấm PEI & Gạt flick tốc độ cao ($Z = -0.8\text{mm}$):**
     - Nhấc lên $Z = 0.2\text{mm}$, di chuyển sang $X=180, Y=3$ ($F12000$).
     - Hạ xuống mép tấm thép PEI tại $Z = -0.8\text{mm}$.
     - Quét qua lại 7 lượt giữa $X164 \leftrightarrow X180$ ở tốc độ vừa $F2000$.
     - Nhấc Z chuyển sang đường $Y=1$, hạ lại $Z=-0.8\text{mm}$.
     - Gạt flick nhanh 7 lượt ở tốc độ cực cao $F12000$ để giật đứt hoàn toàn tơ nhựa thừa.
2. **Hệ thống biến tham số hóa tập trung (`[gcode_macro CLEAN_NOZZLE]`):**
   - `variable_safe_z: 10.0`, `variable_travel_speed: 12000`
   - Vùng PEI Rub: `variable_approach_x: 125.0`, `variable_rub_start_x: 130.0`, `variable_rub_end_x: 140.0`, `variable_rub_y1..3: 5.0, 6.0, 8.0`, `variable_rub_z: 0.1`, `variable_rub_swirl_count: 21`.
   - Vùng Edge Flick: `variable_flick_start_x: 164.0`, `variable_flick_end_x: 180.0`, `variable_flick_y_med: 3.0`, `variable_flick_y_fast: 1.0`, `variable_flick_z: -0.8`, `variable_flick_hop_z: 0.5`.
3. **An toàn phần cứng & Khả năng tương thích:**
   - Kiểm tra `printer.toolchanger.tool_number >= 0` trước mọi chuyển động.
   - Giữ nguyên tích hợp trong `PRINT_START`, `_CLEAN_NOZZLE_PARK`, `PURGE_AND_CLEAN`.
   - Cung cấp alias `CLEAR_NOZZLE` để gọi linh hoạt.

### Kiểm tra
- **Kiểm tra cú pháp Klipper:** Đạt, Jinja2 logic và arc command syntax chuẩn xác.
- **Tính toán hành trình:** Toàn bộ chuyển động ($X: 125 \dots 180$, $Y: 1 \dots 8$, $Z: -0.8 \dots 10.0$) nằm hoàn toàn trong phạm vi an toàn của bàn in và tấm PEI.

### Kết quả
Hệ thống vệ sinh đầu phun bằng phương pháp chà trực tiếp trên tấm PEI đã được triển khai hoàn chỉnh.

### Vấn đề còn lại
- Người vận hành chạy `FIRMWARE_RESTART` trên Mainsail.
- Chạy thử nghiệm `CLEAN_NOZZLE` / `CLEAR_NOZZLE` trên máy in để kiểm chứng chất lượng làm sạch đầu phun.


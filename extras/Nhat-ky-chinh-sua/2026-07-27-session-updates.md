# Nhật ký — 2026-07-27

## Phân tích lỗi bề mặt mẫu Voron khi dùng vật liệu xanh (Extruder 2 / G-code T1)

### Phạm vi
- Chỉ đọc ảnh, G-code và `klippy.log`; không sửa cấu hình máy.
- Ảnh người dùng cung cấp: sáu ảnh mẫu xanh từ `codex-clipboard-*.jpg`.
- G-code đối chiếu: `extras/gcode/voron_design_cube_v8-v1_PETG_2h27m.gcode`.

### Bằng chứng từ ảnh
- Hai mẫu đều lặp lại vùng rỗ/rách ngay sau mép phải của các khe logo và vùng lỗ.
- Phần mặt phẳng bên ngoài vẫn đều, không thấy layer shift, ringing hoặc lỗi Z-offset toàn cục.
- Một số mặt có texture/pillowing trên vùng top nhỏ; thành lỗ và viền ngoài tương đối sạch.
- Mẫu hình phù hợp với hụt lưu lượng khi kết thúc một đoạn ngắn rồi bắt đầu lại, cộng với lớp top/bridge thiếu nâng đỡ; không phù hợp với lỗi cơ khí toàn máy.

### Bằng chứng từ G-code
- Vật liệu xanh là mục thứ hai trong `filament_settings_id`, tương ứng Extruder 2 trong Orca và lệnh vật lý `T1` (không phải `T2`).
- Với mục xanh: `filament_flow_ratio=0.95`, `enable_pressure_advance=0`, `pressure_advance=0.02`, `nozzle_temperature=215°C`, trong khi `nozzle_temperature_range_low` của mục này là `230°C`.
- `retraction_length=0.8mm`, `retract_before_wipe=70%`, `wipe_distance=0.5mm`; `seam_position=nearest`, `seam_gap=10%`.
- `top_surface_speed=100mm/s`, `internal_solid_infill_speed=230mm/s`, top shell 4 lớp và sparse infill 15%.
- Trong các đoạn `;TYPE:Top surface` của T1, đã đếm 93 đoạn đùn; 50 đoạn ngắn hơn 2mm (độ dài trung vị khoảng 1.863mm) và 30 lần retract/unretract. G-code thực tế có chuỗi `E-.8` rồi `E.8` giữa các đoạn ngắn.

### Bằng chứng từ log
- Phiên log mới không có `Lost communication`, MCU shutdown, heater-not-heating, CAN `rx_error/tx_error` khác 0 hoặc lỗi TMC trong vùng in được kiểm tra.
- 750 mẫu nhiệt T1 khi target 215°C nằm trong 210.2–216.6°C, trung bình 214.96°C; do đó không có dấu hiệu lỗi cảm biến/nung mất ổn định.

### Kết luận tạm thời
Nguyên nhân có xác suất cao nhất là tổ hợp cài đặt top-surface của T1: các đoạn rất ngắn bị retract 0.8mm và wipe, sau đó phải phục hồi lưu lượng ở 215°C; PA lại đang bị tắt. Điều này tạo đúng các vết rỗ lặp lại cạnh khe/lỗ. Yếu tố phụ là nhiệt độ thấp hơn ngưỡng profile, flow 0.95 và top/internal-solid speed cao trên sparse infill 15%, gây texture/pillowing ở các vùng top nhỏ.

### Hướng kiểm chứng đề xuất, chưa áp dụng
1. Slice một mẫu chỉ bằng Extruder 2/T1 với cùng hình học, đổi riêng `travel distance threshold` lên 2–4mm để tránh retract các travel nhỏ; giữ lại một bản baseline.
2. Giảm retraction T1 theo test riêng (bắt đầu 0.5–0.6mm), tắt wipe khi kiểm chứng; không tăng `extra length on restart` trước khi đo.
3. Bật/calibrate PA cho đúng spool T1 theo quy trình Klipper/Orca, không dùng mặc định 0.02 nếu chưa đo.
4. In test nhiệt/flow/volumetric speed cho spool xanh; thử vùng 225–235°C và giảm top/internal-solid speed nếu cần.
5. Nếu còn pillowing, tăng top shell từ 4 lên 5–6 lớp hoặc tăng infill hỗ trợ quanh vùng đó; kiểm tra lại bridging/overhang.

### Thay đổi cấu hình
Không có. Chỉ bổ sung nhật ký phân tích.

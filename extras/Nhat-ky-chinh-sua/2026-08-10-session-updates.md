# Nhật ký — 2026-08-10

## 1. Phân tích so sánh Z-Offset: Production vs Axiscope (Chỉ phân tích, không thay đổi cấu hình)

### Mục tiêu
So sánh chất lượng in thực tế giữa 2 bộ giá trị Z-offset:
- **Bộ Production** (T1=+0.228, T2=-0.295, T3=-0.268, T4=+0.086) — in thực tế đẹp
- **Bộ Axiscope đo được** (T1=+0.079, T2=-0.307, T3=-0.134, T4=-0.034) — đo tự động bằng switch

### Dữ liệu đầu vào
- `IMG_20260810_161911.jpg` — Bản in test bằng bộ Production → **đẹp** (sọc đều, bám tốt)
- `IMG_20260810_161925.jpg` + `IMG_20260810_161938.jpg` — Bản in test bằng bộ Axiscope → **kém hơn** (T1 nén, T3 lỏng)

### Bảng so sánh Z-Offset

| Tool | Màu | Production (mm) | Axiscope (mm) | Delta (mm) | Quan sát ảnh Axiscope |
|:---:|:---:|:---:|:---:|:---:|:---|
| T0 | Đỏ | 0.000 (ref) | 0.000 (ref) | 0 | Không đổi |
| T1 | Xanh | +0.228 | +0.079 | -0.149 | Nén mạnh (nozzle quá gần bàn) |
| T2 | Đen | -0.295 | -0.307 | -0.012 | Gần như giống |
| T3 | Trắng | -0.268 | -0.134 | +0.134 | Lỏng, xa bàn |
| T4 | — | +0.086 | -0.034 | -0.120 | Không có ảnh test |

### Kết luận
1. **Bộ Production in đẹp hơn rõ rệt** so với Axiscope — xác nhận qua ảnh thực tế.
2. Axiscope sai nhiều nhất ở T1 (-0.149mm) và T3 (+0.134mm) do lực đàn hồi switch, giãn nở nhiệt (150°C calib vs 210°C PLA), và vị trí đo (Y=-10 ngoài bàn in).
3. T2 là tool Axiscope đo chính xác nhất (delta chỉ 0.012mm).
4. Axiscope nên dùng làm **mốc tham chiếu phần cứng** (baseline) để kiểm tra drift, không nên dùng trực tiếp để in.

### Đề xuất (tham khảo, người dùng tự baby-step)
- Giữ bộ Production hiện tại trong repo.
- Nếu cần micro-tune: T0 baby-step +0.01~0.02mm, T2 baby-step +0.01mm.
- Mỗi lần chỉ chỉnh 1 tool, 0.01mm, rồi in test lại.

### File đã sửa đổi
- Không sửa đổi file cấu hình nào.

### Sao lưu
- Không cần (không thay đổi cấu hình).

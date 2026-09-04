# Tổng hợp Kết quả Đo kiểm TEST_SPEED & Input Shaper (2026-09-04)

> **Mục đích:** Tài liệu tham chiếu kỹ thuật dài hạn ghi nhận toàn bộ dữ liệu thực nghiệm kiểm tra gia tốc/vận tốc (`TEST_SPEED`) và đặc tính cộng hưởng (`ShakeTune`) giữa 2 trạng thái: **Shuttle rỗng (không gài tool)** và **Gài đầu in T0**.

---

## 1. Thông số Phần cứng & Phương pháp Đo

| Thành phần | Đặc điểm kiểm tra |
|---|---|
| **Máy in** | Voron 2.4 CoreXY 350 mm |
| **Cơ cấu đầu in** | StealthChanger 5-Tool |
| **Cảm biến gia tốc** | Cartographer V3 onboard ADXL345 (gắn cố định trên Shuttle carriage) |
| **Phần mềm đo** | Klippain Shake&Tune v6.0.0 (`AXES_SHAPER_CALIBRATION`) |
| **Macro kiểm tra tốc độ** | `TEST_SPEED` (chạy tại $Z = 30\text{ mm}$, tắt crash detection) |
| **Vị trí đo microsteps** | Endstop vật lý góc sau phải (`X: 349, Y: 349`) qua lệnh `GET_POSITION` |

---

## 2. Kết quả Đo kiểm Động học `TEST_SPEED`

### Bảng đối chiếu vi bước (Microsteps) MCU

| Tốc độ ($v$) | Gia tốc ($a$) | Số vòng lặp | Trạng thái | Microsteps trước test | Microsteps sau test | Lệch ($\Delta$) | Kết luận |
|---|---|---|---|---|---|---|---|
| **300 mm/s** | $5.000\text{ mm/s}^2$ | 3 | Shuttle rỗng | X: 85095, Y: 16227 | X: 85106, Y: 16220 | $\Delta X = +11, \Delta Y = -7$ | Đạt (Không mất bước) |
| **400 mm/s** | $7.000\text{ mm/s}^2$ | 3 | Shuttle rỗng | X: 85096, Y: 16228 | X: 85114, Y: 16222 | $\Delta X = +18, \Delta Y = -6$ | Đạt (Không mất bước) |
| **450 mm/s** | $10.000\text{ mm/s}^2$ | 5 | Shuttle rỗng | X: 85101, Y: 16229 | X: 85102, Y: 16228 | $\Delta X = +1, \Delta Y = -1$ | Xuất sắc |
| **500 mm/s** | $15.000\text{ mm/s}^2$ | 5 | Shuttle rỗng | X: 85106, Y: 16226 | X: 85095, Y: 16229 | $\Delta X = -11, \Delta Y = +3$ | Đạt (Không mất bước) |
| **300 mm/s** | $5.000\text{ mm/s}^2$ | 3 | **Gài Tool T0** | X: 85113, Y: 16217 | X: 85089, Y: 16225 | $\Delta X = -24, \Delta Y = +8$ | Đạt (Không mất bước) |
| **400 mm/s** | $7.000\text{ mm/s}^2$ | 3 | **Gài Tool T0** | X: 85097, Y: 16217 | X: 85091, Y: 16213 | $\Delta X = -6, \Delta Y = -4$ | Xuất sắc |
| **450 mm/s** | $10.000\text{ mm/s}^2$ | 5 | **Gài Tool T0** | X: 85080, Y: 16226 | X: 85106, Y: 16200 | $\Delta X = +26, \Delta Y = -26$ | Đạt (Không mất bước) |
| **500 mm/s** | $15.000\text{ mm/s}^2$ | 5 | **Gài Tool T0** | X: 85077, Y: 16229 | X: 85117, Y: 16217 | $\Delta X = +40, \Delta Y = -12$ | Đạt (Không mất bước) |

### Nhận xét kỹ thuật:
1. **Độ ổn định động cơ:** Hoàn toàn không xảy ra hiện tượng stall motor hay mất bước ở mọi mức thử nghiệm từ $300\text{ mm/s}$ đến $500\text{ mm/s}$ và gia tốc lên tới $15.000\text{ mm/s}^2$.
2. **Sai số cơ học lặp lại:** Chênh lệch microstep lớn nhất là $40$ steps ($\approx 0.08\text{ mm}$ với độ phân giải vi bước hiện tại). Đây là quán tính dịch chuyển nhẹ tại công tắc chạm endstop cơ khí sau chuỗi chuyển động tải nặng cực đại, nằm trong ngưỡng cho phép đối với switch vật lý.

---

## 3. Kết quả Đo Rung Động & Cộng Hưởng (ShakeTune Input Shaper)

### Bảng so sánh đặc tính cộng hưởng

| Thông số | Trạng thái 1: Không lắp Tool (Shuttle rỗng) | Trạng thái 2: Có lắp Tool T0 | Cấu hình tham chiếu (03/09/2026) |
|---|---|---|---|
| **Thời điểm đo** | 17:39:48 (2026-09-04) | 18:01:39 (2026-09-04) | 20:55:00 (2026-09-03) |
| **File đồ thị X** | `inputshaper_20260904_173948_axis_X.png` | `inputshaper_20260904_180139_axis_X.png` | `T0_axis_X.png` |
| **File đồ thị Y** | `inputshaper_20260904_173948_axis_Y.png` | `inputshaper_20260904_180139_axis_Y.png` | `T0_axis_Y.png` |
| **Trục X — Tần số chính** | $\mathbf{90.4\text{ Hz}}$ (Peaks: 94.9, 106.0, 131.3 Hz) | $\mathbf{41.1\text{ Hz}}$ (Peak phụ: 104.3 Hz) | $43.6\text{ Hz}$ (Phạm vi 5 tool: 42.6–47.4 Hz) |
| **Trục X — Hệ số cản ($\zeta$)** | $0.047$ | $0.200$ | $0.124$ |
| **Trục X — Shaper đề xuất** | `mzv @ 90.4 Hz` / `ei @ 109.8 Hz` | `3hump_ei @ 84.2 Hz` (hoặc `mzv @ 41.1 Hz`) | `mzv @ 43.6 Hz` |
| **Trục Y — Tần số chính** | $\mathbf{37.9\text{ Hz}}$ (Peaks: 61.7, 87, 98, 110, 123 Hz) | $\mathbf{30.0\text{ Hz}}$ (Peaks: 64.8, 93.2, 123, 132 Hz) | $33.4\text{ Hz}$ (Phạm vi 5 tool: 31.6–35.4 Hz) |
| **Trục Y — Hệ số cản ($\zeta$)** | $0.078$ | $0.094$ | $0.080$ |
| **Trục Y — Shaper đề xuất** | `3hump_ei @ 75.4 Hz` | `2hump_ei @ 47.6 Hz` / `3hump_ei @ 53.8 Hz` | `mzv @ 33.4 Hz` |

---

## 4. Phân tích Bản chất Cơ khí

1. **Sự dịch chuyển tần số do khối lượng ($f \propto \sqrt{k/m}$):**
   - Khi gài tool T0, trọng lượng cụm đầu in tăng thêm $\approx 250 - 350\text{ g}$.
   - Tần số cộng hưởng trục X giảm từ **$90.4\text{ Hz} \rightarrow 41.1\text{ Hz}$** (giảm $\approx 54\%$).
   - Tần số cộng hưởng trục Y giảm từ **$37.9\text{ Hz} \rightarrow 30.0\text{ Hz}$** (giảm $\approx 21\%$).
2. **Hiệu ứng kẹp ngàm StealthChanger:**
   - Hệ số giảm chấn $\zeta$ trục X tăng vọt từ **$0.047 \rightarrow 0.200$** khi có tool. Điều này chứng minh lực hút nam châm và chốt định vị của ngàm kẹp giữ rất chặt cụm toolhead, giúp triệt tiêu rung lắc tự do tần số cao.
3. **Đặc tính trục Y (Khung Voron 2.4 350 mm):**
   - Trục Y kéo toàn bộ thanh ray X beam nên quán tính lớn hơn và xuất hiện hiện tượng đa đỉnh rung ($30.0\text{ Hz}$ và $64.8\text{ Hz}$).
   - Đề xuất bộ lọc `2HUMP_EI @ 47.6 Hz` của ShakeTune có dải bao phủ rộng, giúp dập tắt đồng thời cả hai đỉnh $30\text{ Hz}$ và $65\text{ Hz}$ nếu cần triệt rung tuyệt đối ở gia tốc $> 5.000\text{ mm/s}^2$.

---

## 5. Khuyến nghị Vận hành & Cấu hình

1. **Travel Moves (Đổi đầu in / Di chuyển không đùn):**
   - Vận tốc: **$350 - 450\text{ mm/s}$**.
   - Gia tốc: **$7.000 - 10.000\text{ mm/s}^2$**.
2. **In ấn thông thường (Chi tiết & Bề mặt đẹp):**
   - Vận tốc: **$150 - 250\text{ mm/s}$**.
   - Gia tốc in: **$3.500 - 4.500\text{ mm/s}^2$** (bảo đảm không bo góc và không rung bóng mờ).
3. **Cấu hình Input Shaper trong `input-shaper.cfg`:**
   - Cấu hình dùng chung hiện tại (`shaper_freq_x: 43.6`, `shaper_freq_y: 33.4`, thuật toán `mzv`) vẫn cực kỳ tối ưu và tương thích tốt với kết quả đo thực tế ngày hôm nay.
   - Nếu in tốc độ cao với các chi tiết phẳng dài theo trục Y, có thể cân nhắc chuyển trục Y sang `shaper_type_y: 2hump_ei` và `shaper_freq_y: 47.6`.

# Nhật ký quyết định kỹ thuật

Ghi nhận các quyết định kỹ thuật quan trọng ở đây để các phiên làm việc trong tương lai hiểu **tại sao** một giá trị hoặc cách tiếp cận được chọn.

---

## Mẫu

```markdown
## YYYY-MM-DD — [Tiêu đề quyết định]

**Bối cảnh:** Điều gì dẫn đến quyết định này?
**Đã chọn:** Giá trị/cách tiếp cận được chọn
**Đã loại:** Các phương án thay thế đã xem xét và lý do loại bỏ
**Lý do:** Tại sao đây là lựa chọn tốt nhất?
```

---

## 2026-06-30 — Vị trí tham chiếu Zero cho Bed Mesh

**Bối cảnh:** `zero_reference_position` của bed mesh được đặt thành `170, 203` (vị trí probe), nhưng Klipper định nghĩa đây là vị trí *nozzle*, không phải vị trí probe.
**Đã chọn:** `174, 168` — tâm vật lý của bàn in 350x350 nơi nozzle đứng khi homing Z.
**Đã loại:** `170, 203` — đây là vị trí vật lý của probe, gây sai lệch Z-offset do bề mặt bàn in không đồng nhất.
**Lý do:** Khi nozzle ở `174, 168` và probe Cartographer có Y offset +35mm, probe đo Z0 tại Y=203. Điều này đảm bảo điểm zero của bed mesh khớp chính xác với điểm homing Z, loại bỏ trôi Z-offset.

## 2026-06-28 — Tăng QGL Retry Tolerance lên 0.0075

**Bối cảnh:** Quad Gantry Leveling (QGL) bị hủy với lỗi giả "đánh số motor" (motor numbering).
**Đã chọn:** `retry_tolerance: 0.0075`
**Đã loại:** `retry_tolerance: 0.005` (giá trị gốc) — quá chặt, gây lỗi QGL giả.
**Lý do:** Dung sai gốc quá nghiêm ngặt cho độ chính xác cơ khí của máy in, gây thử lại và hủy QGL không cần thiết. 0.0075 vẫn nằm trong phạm vi độ chính xác cân bằng chấp nhận được.

## 2026-06-23 — Tăng check_gain_time Heater Bed lên 240s

**Bối cảnh:** Nhiễu điện từ SSR gây xung ADC trên thermistor bàn in, kích hoạt shutdown giả "không gia nhiệt đúng tốc độ mong đợi".
**Đã chọn:** `check_gain_time: 240` (4 phút)
**Đã loại:** `check_gain_time: 120` (2 phút gốc) — quá ngắn; xung nhiễu SSR trong giai đoạn gia nhiệt ban đầu kích hoạt shutdown giả.
**Lý do:** Tăng cửa sổ giám sát cho heater đủ thời gian thể hiện tăng nhiệt độ ngay cả khi có xung nhiễu ADC tạm thời từ SSR.

## 2026-06-30 — Điều chỉnh Z-Offset Tool T3 (-0.08mm)

**Bối cảnh:** Khi in thực tế, lớp đầu tiên của T3 quá cao — bám dính bàn in không đủ.
**Đã chọn:** `gcode_z_offset` giảm thêm `0.08mm` (từ `-0.178` xuống `-0.258`)
**Đã loại:** Giữ giá trị gốc — chất lượng in không chấp nhận được.
**Lý do:** Thử nghiệm in thực tế cho thấy nozzle quá xa bàn in. Điều chỉnh 0.08mm được xác định bằng cách tinh chỉnh trực tiếp từ giao diện KlipperScreen trong khi đang in.

## 2026-08-06 — Cho phép đẩy thư mục sao lưu và cấu hình tải về lên GitHub

**Bối cảnh:** Người dùng yêu cầu đồng bộ toàn bộ lịch sử sao lưu (`extras/backups/`) và bản tải cấu hình (`extras/Config download/`) lên GitHub để phòng ngừa rủi ro hỏng máy tính cá nhân.
**Đã chọn:** Bỏ bỏ qua (un-ignore) `extras/backups/` và `extras/Config download/` trong `.gitignore`, tiếp tục bảo mật nghiêm ngặt các file nhạy cảm (`*.secrets`, `moonraker.secrets`, `wpa_supplicant.conf`, `*.key`, `*.pem`, `*.env`).
**Đã loại:** Chỉ giữ sao lưu cục bộ (mất dữ liệu nếu phần cứng hỏng).
**Lý do:** Đáp ứng nhu cầu an toàn dữ liệu trên cloud của người dùng mà vẫn đảm bảo 100% không lộ thông tin nhạy cảm.

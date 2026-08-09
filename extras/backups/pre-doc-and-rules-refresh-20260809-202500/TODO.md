# Công việc đang chờ (TODO)

Theo dõi các công việc đang chờ, cải tiến và điều tra ở đây.
AI assistant nên kiểm tra file này khi bắt đầu mỗi phiên làm việc.

---

## Đang chờ xử lý

- [ ] **Timeout kết nối CAN Cartographer** — Điều tra giải pháp vĩnh viễn cho lỗi timeout kết nối CAN sau khi soft restart (xem KNOWN_ISSUES.md). Cần cân nhắc: đường reset chuyên dụng, cải thiện termination CAN, hoặc làm mát chip Cartographer.
- [ ] **Hiệu chuẩn Input Shaper** — Chạy kiểm tra cộng hưởng (resonance test) và cập nhật `input-shaper.cfg` với giá trị tối ưu cho trọng lượng đầu in hiện tại.
- [ ] **Pressure Advance cho từng tool** — Tinh chỉnh các giá trị pressure advance riêng biệt cho từng đầu in (T0–T4) đối với các loại nhựa khác nhau.
- [ ] **Tối ưu hóa quạt đầu in** — Xem xét biểu đồ quạt và đảm bảo làm mát đầy đủ cho từng đầu phun trong suốt quá trình in nhiều đầu phun.
- [ ] **Giám sát nhiệt độ Cartographer** — Thêm cơ chế giám sát/cảnh báo nhiệt độ cho chip Cartographer để tránh sự cố quá nhiệt.

## Đã hoàn thành

- [x] ~~Cấu hình camera MF-500 ở độ phân giải gốc 2K~~ (2026-06-14) → Hạ xuống 800x600 do camera không load được ở 2K (2026-07-05)
- [x] ~~Cập nhật zero_reference_position khớp với vị trí homing nozzle~~ (2026-06-30)
- [x] ~~Tăng check_gain_time của heater_bed để sửa lỗi tắt máy giả~~ (2026-06-23)
- [x] ~~Điều chỉnh QGL retry_tolerance ngăn chặn hủy lệnh giả~~ (2026-06-28)
- [x] ~~Thêm quy tắc bảo mật .gitignore trước khi public repo~~ (2026-06-30)

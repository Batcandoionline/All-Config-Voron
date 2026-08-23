# Vấn đề đã biết & Cách khắc phục

Ghi nhận các vấn đề tái diễn hoặc đáng chú ý ở đây. AI assistant nên đọc file này khi bắt đầu mỗi phiên để nắm các vấn đề đang tồn tại.

---

## Mẫu

```markdown
## [Thành phần/Khu vực] — [Tiêu đề ngắn]

**Trạng thái:** Đang theo dõi / Đã giải quyết / Đang giám sát
**Phát hiện lần đầu:** YYYY-MM-DD
**Triệu chứng:** Chuyện gì xảy ra?
**Nguyên nhân gốc:** Nguyên nhân là gì? (đã xác nhận hoặc nghi ngờ)
**Giải pháp tạm:** Cách xử lý khi sự cố xảy ra?
**Sửa vĩnh viễn:** Nếu có, hoặc "Đang chờ điều tra"
**Nhật ký liên quan:** Link tới nhật ký hàng ngày hoặc mục klippy.log
```

---

## Printer-Setup — Xung đột dryer/print và crash detector báo sai cạnh sensor

**Trạng thái:** Đã giải quyết
**Phát hiện lần đầu:** 2026-08-22
**Triệu chứng:** Timer dryer có thể tiếp tục điều khiển bed heater/bed fan khi
print mới bắt đầu; RESUME sau tool crash không bật lại detector; cạnh detection
pin của tool đang dock có thể gây pause giả. CLEAN_NOZZLE cũng có thể chạy khi
KTC không có active tool vì `toolhead.extruder` vẫn giữ tên mặc định.
**Nguyên nhân gốc:** Thiếu handoff quyền sở hữu tài nguyên và hủy delayed callback;
upstream `tool_crash.py` dùng cùng callback cho mọi pin rồi crash vô điều kiện;
macro nozzle dùng tên extruder thay cho trạng thái active tool của KTC.
**Giải pháp tạm:** Không áp dụng — đã sửa vĩnh viễn.
**Sửa vĩnh viễn:** Thêm dryer-to-print handoff, hủy callback cũ, nâng Z trước
dock, bật lại detector trong RESUME, kiểm tra cạnh sensor bằng active-tool
watchdog và dùng `toolchanger.tool_number` cho CLEAN_NOZZLE. Patch Python được
lưu tại `config/scripts/patches/tool_crash-active-tool-validation.patch` và được
`install.sh` preflight/backup/apply idempotent.
**Nhật ký liên quan:** `Voron 5 Tool/extras/Nhat-ky-chinh-sua/2026-08-22-session-updates.md`, mục 3.

---

## Cartographer MCU — Timeout kết nối CAN Bus sau Soft Restart

**Trạng thái:** Đang giám sát
**Phát hiện lần đầu:** 2026-07-02
**Triệu chứng:** Sau khi hệ thống khởi động lại hoặc Klipper crash, probe Cartographer (UUID: `da13d909ce34`) không kết nối được. Klipper bị kẹt ở trạng thái `STARTUP`. Mainsail hiển thị "Printer is not ready". Tất cả MCU khác (EBB0–EBB4) kết nối thành công.
**Nguyên nhân gốc:** Nghi ngờ — Khi Raspberry Pi hoặc dịch vụ Klipper khởi động lại nhưng nguồn 24V vẫn bật, MCU Cartographer không được reset phần cứng. Nó kẹt trong trạng thái giao tiếp CAN cũ và từ chối yêu cầu bắt tay mới từ Klipper. Nhiệt độ chip cao (66.1°C quan sát được trước sự cố) có thể góp phần vào việc MCU bị khóa.
**Giải pháp tạm:** Tắt nguồn hoàn toàn — tắt nguồn chính, đợi ít nhất 60 giây để tụ điện xả hết, sau đó bật lại. Điều này buộc reset phần cứng tất cả MCU bao gồm Cartographer.
**Sửa vĩnh viễn:** Đang chờ điều tra. Các giải pháp khả thi:
- Thêm đường reset chuyên dụng cho board Cartographer
- Cải thiện termination/đi dây CAN bus
- Giám sát nhiệt độ chip Cartographer và thêm tản nhiệt nếu luôn cao
**Nhật ký liên quan:** [2026-07-02-session-updates.md](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/Nhat-ky-chinh-sua/2026-07-02-session-updates.md)

---

## Mainsail Config Files — Dữ liệu runtime lẫn root và ShakeTune ghost duplicate

**Trạng thái:** Đã giải quyết
**Phát hiện lần đầu:** 2026-08-22
**Triệu chứng:** Root `config` hiển thị hai dòng `ShakeTune_results` (một dòng
mtime 1970), hai JSON ToolVision và nhiều backup/ZIP không rõ nguồn.
**Nguyên nhân gốc:** Chỉ có một thư mục ShakeTune vật lý. Entry thứ hai là state
frontend cũ sau lần rsync xóa/khôi phục. ToolVision 3.2.1 và ShakeTune đặt output
trực tiếp trong root; backup cũ chưa được chuyển sang `config_backups`.
**Giải pháp tạm:** Refresh widget Config Files hoặc hard refresh Mainsail.
**Sửa vĩnh viễn:** Gom output máy này vào `config/Generated-Data/`, chuyển backup
ra `printer_data/config_backups`, bảo vệ `Generated-Data/` trong installer và
phát hành ToolVision v3.2.2 với default/backup path không làm rối root.
**Nhật ký liên quan:** `Voron 5 Tool/extras/Nhat-ky-chinh-sua/2026-08-22-session-updates.md`, mục 2.

---

## Heater Bed — Shutdown giả "Không gia nhiệt đúng tốc độ"

**Trạng thái:** Đã giải quyết
**Phát hiện lần đầu:** 2026-06-23
**Triệu chứng:** Klipper shutdown với thông báo `Heater heater_bed not heating at expected rate` trong quá trình gia nhiệt bàn in ban đầu.
**Nguyên nhân gốc:** Nhiễu điện từ SSR gây xung ADC trên đọc thermistor bàn in, khiến Klipper nghĩ nhiệt độ không tăng.
**Giải pháp tạm:** Không áp dụng — đã sửa vĩnh viễn.
**Sửa vĩnh viễn:** Tăng `check_gain_time` từ 120s lên 240s trong `[verify_heater heater_bed]` để cho phép thêm thời gian trung bình hóa nhiệt độ làm mượt xung nhiễu.
**Nhật ký liên quan:** [2026-06-23-session-updates.md](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/Nhat-ky-chinh-sua/2026-06-23-session-updates.md)

---

## Camera MF-500 — FPS thực tế chỉ đạt 15-20fps thay vì 30fps

**Trạng thái:** Đã giải quyết
**Phát hiện lần đầu:** 2026-07-05
**Triệu chứng:** Camera MF-500 2K (USB 2.0) cấu hình 1280x720 MJPEG với camera-streamer chỉ đạt 15-20fps khi xem qua MJPG stream trong Mainsail. Xảy ra ở mọi resolution native. Resolution 1920x1080 và 2560x1440 gây màn hình đen khi dùng WebRTC.
**Nguyên nhân gốc:** MJPG stream gửi từng frame JPEG riêng lẻ qua HTTP — tốn bandwidth và CPU. Trên Pi chạy nặng (Klipper + 5 CAN tools + Cartographer), pipeline MJPG bị giới hạn 15-20fps.
**Giải pháp tạm:** Không áp dụng — đã sửa vĩnh viễn.
**Sửa vĩnh viễn:** Đổi Mainsail webcam Service sang **WebRTC (camera-streamer)** với URL Stream `/webcam/webrtc`. WebRTC dùng H.264 hardware encoding trên GPU Pi → streaming mượt mà ở 1280x720. Resolution tối đa ổn định là 1280x720 (1080p/1440p gây màn hình đen do vượt giới hạn USB bandwidth + GPU encoder).
**Nhật ký liên quan:** [2026-07-05-session-updates.md](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/Nhat-ky-chinh-sua/2026-07-05-session-updates.md)

---

## Toolchanger — Lỗi Expected tool tool T3 but active is tool T4 khi đổi đầu in

**Trạng thái:** Đang theo dõi
**Phát hiện lần đầu:** 2026-07-11
**Triệu chứng:** Khi lệnh in đổi đầu phun từ T4 về T3, sau khi hoàn thành nhiệt độ chờ, Klipper báo lỗi `Expected tool tool T3 but active is tool T4` và dừng in khẩn cấp.
**Nguyên nhân gốc:** Cảm biến báo trạng thái đầu phun của T4 (`detection_pin: ^!EBB4:PB6`) vẫn báo đang gắn (Present) sau khi chu trình thả T4 đã hoàn tất. Có thể do cơ khí (T4 bị kẹt không rời khỏi carriage) hoặc do điện/cảm biến (nút bấm switch bị kẹt cơ học hoặc chân tín hiệu bị chập mát).
**Giải pháp tạm:** Kiểm tra thực tế xem đầu in T4 có nằm lại ở dock không. Dùng lệnh `QUERY_ENDSTOP` hoặc các lệnh truy vấn tương đương để đo trạng thái chân `EBB4:PB6`. Vệ sinh microswitch tiếp xúc của T4.
**Sửa vĩnh viễn:** Đang chờ điều tra thêm từ người dùng (loại trừ lỗi chập dây hoặc kẹt cơ khí trên T4).
**Nhật ký liên quan:** [2026-07-11-session-updates.md](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/Nhat-ky-chinh-sua/2026-07-11-session-updates.md)

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

## kTAMV/MF-500 — Cảnh quang học có nhiều blob giống nozzle

**Trạng thái:** Đang theo dõi
**Phát hiện lần đầu:** 2026-08-22
**Triệu chứng:** Camera calibration kTAMV chỉ đạt 6/10 điểm; một scale `0.028`
lệch cụm `0.041–0.044`, marker xử lý nằm trên vùng phản xạ thay vì lỗ nozzle.
**Nguyên nhân gốc:** Cảnh có phản xạ/cháy sáng và nhiều vật thể giống lỗ nozzle;
kTAMV kéo frame 1280×720 thành 640×480 và dùng detector cố định. ToolVision trước
đó cũng từ chối cùng cảnh vì ambiguity.
**Giải pháp tạm:** Không chạy calibration/centering cho tới khi ảnh đã sạch,
focus đúng, ánh sáng mềm và lỗ nozzle ở gần tâm; không tăng tolerance để ép pass.
**Sửa vĩnh viễn:** Chưa xác nhận. Cần test có người giám sát sau khi cải thiện
quang học, đo lặp và giữ emergency stop.
**Nhật ký liên quan:** `Voron 5 Tool/extras/Nhat-ky-chinh-sua/2026-08-22-session-updates.md`, mục 7; `2026-08-31-session-updates.md`.

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

**Trạng thái:** Đã giải quyết (người vận hành xác nhận 2026-08-23)
**Phát hiện lần đầu:** 2026-07-02
**Triệu chứng:** Sau khi hệ thống khởi động lại hoặc Klipper crash, probe Cartographer (UUID: `da13d909ce34`) không kết nối được. Klipper bị kẹt ở trạng thái `STARTUP`. Mainsail hiển thị "Printer is not ready". Tất cả MCU khác (EBB0–EBB4) kết nối thành công.
**Nguyên nhân gốc:** Chưa có bằng chứng đủ để kết luận; các giả thuyết reset CAN và nhiệt độ trước đây không được xem là nguyên nhân đã xác nhận.
**Giải pháp tạm:** Không còn áp dụng.
**Sửa vĩnh viễn:** Người vận hành xác nhận lỗi đã hết ngày 2026-08-23. Nếu tái xuất hiện, lưu `klippy.log`, trạng thái `can0` và nhiệt độ Cartographer trước khi power-cycle để mở điều tra mới.
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

**Trạng thái:** Đã giải quyết (người vận hành xác nhận 2026-08-23)
**Phát hiện lần đầu:** 2026-07-11
**Triệu chứng:** Khi lệnh in đổi đầu phun từ T4 về T3, sau khi hoàn thành nhiệt độ chờ, Klipper báo lỗi `Expected tool tool T3 but active is tool T4` và dừng in khẩn cấp.
**Nguyên nhân gốc:** Sự cố trước đây liên quan trạng thái detection pin T4, nhưng chưa có dữ liệu đủ để ghi nguyên nhân cơ khí hay điện là kết luận cuối cùng.
**Giải pháp tạm:** Không còn áp dụng.
**Sửa vĩnh viễn:** Người vận hành xác nhận cảm biến T4 đã hết lỗi ngày 2026-08-23. Nếu tái xuất hiện, ghi trạng thái detection pin và vị trí cơ khí trước khi can thiệp.
**Nhật ký liên quan:** [2026-07-11-session-updates.md](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/Nhat-ky-chinh-sua/2026-07-11-session-updates.md)

---

## Stepper X — TMC ShortToSupply_A trong G28

**Trạng thái:** Đã xử lý theo xác nhận người vận hành 2026-08-26; xác minh lại 2026-09-06
**Phát hiện lần đầu:** 2026-08-26
**Triệu chứng:** Full `G28` dừng máy với
`TMC 'stepper_x' reports error: DRV_STATUS: c01f0010 s2vsa=1(ShortToSupply_A!)`.
**Nguyên nhân gốc:** Chưa xác nhận; cờ TMC chỉ ra lỗi điện trên pha A
của stepper X, cần kiểm tra dây, connector, motor và driver trước khi quy kết.
**Giải pháp tạm:** Dừng chuyển động, tắt heater, tắt nguồn và kiểm tra
phần cứng. Không chạy tiếp chỉ vì Klipper tự nạp lại thành công.
**Sửa vĩnh viễn:** Nhật ký 2026-08-26 mục 11 ghi người vận hành đã xử lý phần cứng. Phiên 2026-09-06 có DUMP_TMC không còn cờ lỗi và G28 thành công; nguyên nhân điện cụ thể trước đó chưa được xác định.
**Nhật ký liên quan:** `Voron 5 Tool/extras/Nhat-ky-chinh-sua/2026-08-26-session-updates.md`, mục 10–11; `2026-09-06-session-updates.md`, mục 6.


---

## TKC 780a492 — Fallback sai hướng camera và XY chưa ổn định

**Trạng thái:** Lịch sử; đã thử lại bằng b6c3328 bên dưới, chưa áp offset production
**Phát hiện lần đầu:** 2026-09-06
**Triệu chứng:** Fallback MPP giả định trả correction sai chiều trên MF-500; hai vòng XY hoàn chỉnh, vòng thứ ba lỗi ERR_CV_202 tại T2 với burst spread 5 px. API vẫn có thể báo SUCCESS cũ khi đang chạy; KTC mất active tool khi G-code báo lỗi.
**Nguyên nhân:** Hướng trục giả định sai đã xác nhận bằng ±0,5 mm đo thật. Lỗi hội tụ còn cần phân biệt thời gian ổn định sau chuyển động, detector và giới hạn 5 bước; không kết luận lỗi cơ khí từ dữ liệu hiện có.
**Giải pháp tạm:** Dùng ma trận đã đo, TKC_TEST_XY (SAVE_CONFIG=0, CALIBRATE_Z=0, WIGGLE=0), Z40 trước đổi tool. Không dùng fallback để chuyển động hoặc DRY_RUN như phép thử đứng yên. Khi HTTP 504, kiểm tra chuỗi đang chạy trước khi gửi thêm lệnh.
**Sửa vĩnh viễn:** Đang chờ cải thiện bootstrap, frame-quality gates và run-state trong TKC.
**Nhật ký liên quan:** `Voron 5 Tool/extras/Nhat-ky-chinh-sua/2026-09-06-session-updates.md`, mục 6; báo cáo `extras/experiments/tkc-20260906/REPORT.md`.

---

## TKC b6c3328 — XY đạt 3 vòng nhưng abort và bù XY khi dò Z còn lỗi

**Trạng thái:** Thử nghiệm có giám sát; source trên máy có startup-imports.patch, không dùng XYZ tự động
**Phát hiện lần đầu:** 2026-09-06
**Triệu chứng:** Source gốc thiếu import Tuple/Optional, 10/91 tests lỗi; sau bản vá import, 91 tests đạt và ba vòng XY T0–T4 hoàn chỉnh. CALIBRATION_ABORT gửi qua Moonraker tại T1 bị xếp hàng tới hết vòng (156,027 s), sau đó báo không còn lượt chạy. Raw log có một BlockingIOError khi ghi phản hồi G-code; print_stall tăng tới 3.
**Nguyên nhân đã xác nhận:** Abort đi chung G-code mutex với lệnh calibration đồng bộ. Bù trạm Z dùng dấu trừ trong khi offset camera là chênh raw carriage cần cộng; mô phỏng X68 với offset +0,865 cho lệnh X67,135 thay vì X68,865. Scale bỏ qua lỗi acquire_lock; health lỗi sau khi lấy lock không đi qua finally; centering sau scale thất bại vẫn báo SUCCESS. Gate sàn 6 px cho phép dispersion 0,138 mm ở MPP 0,023.
**Giải pháp tạm:** Giữ overlay XY lạnh, SAVE_CONFIG=0, CALIBRATE_Z=0, WIGGLE=0, Z40 trước đổi tool. Không dùng CALIBRATION_ABORT làm nút dừng vận hành; không tự gửi lại calibration sau HTTP timeout. kTAMV không cần gỡ, đã dừng khi đo và bật lại sau đó.
**Cần cải tiến:** Abort ngoài hàng đợi, thống nhất dấu tọa độ, cleanup/lease phiên, trạng thái fit/center riêng, gate theo mm, telemetry tool thực và điều tra buffering/scheduling. Không quy lỗi CAN hoặc cơ khí khi chưa có bằng chứng. Độ lặp ba vòng lớn nhất 0,026 mm X / 0,033 mm Y, chưa chứng minh độ chính xác tuyệt đối.
**Nhật ký liên quan:** `Voron 5 Tool/extras/Nhat-ky-chinh-sua/2026-09-06-session-updates.md`, mục 7; `extras/experiments/tkc-b6c3328-20260906/REPORT.md` và các reproduction offline.

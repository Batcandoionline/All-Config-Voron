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

## 2026-08-22 — Kết thúc thử nghiệm camera và quay về Axiscope PF2

**Bối cảnh:** kTAMV không nhận ổn định lỗ nozzle dưới ánh sáng hiện tại; cả
kTAMV và ToolVision đều gặp nhiều vật thể/phản xạ giống nozzle. Người dùng chọn
quay về công tắc cơ học.
**Đã chọn:** Gỡ toàn bộ kTAMV và kích hoạt `[axiscope]` với `pin: ^PF2`, tọa độ
`X=68, Y=-10, Z=7`, 10 mẫu. Không đặt `config_file_path`; kết quả chỉ được báo
để duyệt vì năm tool được định nghĩa trong năm file riêng.
**Đã loại:** Tăng dung sai detector camera hoặc cho Axiscope tự ghi vào
`printer.cfg`.
**Lý do:** Microswitch đã có dữ liệu lặp lại thực tế, không phụ thuộc ánh sáng;
chế độ báo cáo tránh section tool trùng và giữ nguyên offset production đã kiểm
chứng bằng bản in.

## 2026-08-22 — Dọn clone Home cũ nhưng giữ runtime rollback

**Bối cảnh:** Home của máy còn `~/All-Config-Voron`, `~/axiscope`,
`~/axiscope.bak`, `~/Tool-Vision` và `~/tool-vision-env`, dễ bị hiểu nhầm là
trùng lặp sau khi chuyển sang kTAMV.
**Đã chọn:** Archive rồi xóa `~/All-Config-Voron` và `~/axiscope.bak` vì không
có service, process, symlink, cron hoặc updater sử dụng. Giữ `~/axiscope`,
`~/Tool-Vision` và `~/tool-vision-env` vì service/symlink rollback vẫn trỏ vào
đó. Recovery archive nằm ngoài config active tại
`~/printer_data/config_backups/home-folder-cleanup-20260822-213300/`.
**Đã loại:** Xóa thẳng cả năm folder hoặc giữ hai clone legacy trong Home.
**Lý do:** Làm gọn danh sách Home mà không tạo symlink hỏng hoặc phá khả năng
quay lại Axiscope/ToolVision sau thử nghiệm kTAMV.

## 2026-08-22 — Tạm chuyển backend hiệu chuẩn XY sang kTAMV

**Bối cảnh:** Người dùng cần tạm gỡ ToolVision để thử nghiệm trực tiếp kTAMV với
camera MF-500. Installer kTAMV upstream tại commit `72421f2` đã cũ, tự chạy
`apt`/chỉnh giờ, dùng trùng port 8085 và sinh sai header Moonraker.
**Đã chọn:** Không chạy installer upstream. Cài checkout `~/kTAMV` được pin,
venv riêng, user service port 8086 và cấu hình
`Printer-Setup/ktamv.cfg`; tắt upload cloud. ToolVision service/config/updater
bị vô hiệu hóa tạm, nhưng source, venv, symlink, PF2 state và kết quả được giữ.
**Đã loại:** Purge `~/Tool-Vision`, xóa dữ liệu đã học hoặc cho hai server dùng
chung port 8085.
**Lý do:** Cho phép thử kTAMV có giám sát mà vẫn rollback nhanh, tránh thay đổi
package hệ thống và tránh mất dữ liệu ToolVision.

## 2026-08-22 — Tách runtime ToolVision khỏi cây cấu hình Mainsail

**Bối cảnh:** Installer ToolVision từng tạo `config/Tool-Vision/` để chứa file
cấu hình Klipper, include Moonraker và backup cũ, khiến root cấu hình lộn xộn và
dễ bị hiểu nhầm với repository runtime `~/Tool-Vision`.
**Đã chọn:** Quản lý cấu hình máy tại
`config/Printer-Setup/tool_vision.cfg`, đặt `[update_manager tool-vision]` trực
tiếp trong `moonraker.conf`, lưu backup dưới
`~/printer_data/config_backups/tool-vision/` và dữ liệu sinh tự động dưới
`config/Generated-Data/ToolVision/`.
**Đã loại:** Xóa `~/Tool-Vision` hoặc gom source runtime vào `config/`. Thư mục
`~/Tool-Vision` là Git checkout production mà `tool-vision.service`, Moonraker
Update Manager và các symlink `klippy/extras/tool_vision*.py` sử dụng trực tiếp.
**Lý do:** Mainsail chỉ hiển thị cấu hình cần chỉnh, trong khi runtime Git vẫn
có thể cập nhật độc lập và không làm hỏng service/Klipper module.

## 2026-08-09 — Tự động loại trừ file Markdown khi đồng bộ sang máy in

**Bối cảnh:** Thư mục `config/` chứa file `README.md` hướng dẫn. Khi người dùng chạy script đồng bộ `install.sh` hoặc `update.sh`, các file `.md` bị copy vào `~/printer_data/config/` của Klipper, gây lộn xộn giao diện quản lý file của Mainsail.
**Đã chọn:** Thêm `--exclude "README.md" --exclude "*.md"` vào lệnh `rsync` trong cả `install.sh` và `update.sh`.
**Đã loại:** Xóa hoàn toàn file README khỏi kho Git (làm mất tài liệu hướng dẫn trên GitHub).
**Lý do:** Giữ trọn vẹn tài liệu đẹp trên GitHub cho người phát triển, đồng thời giữ thư mục cấu hình trên máy in hoàn toàn sạch sẽ.

## 2026-08-09 — Chiến lược Z-Offset: Giá trị In Thực Tế + Mốc Tham Chiếu Công Tắc

**Bối cảnh:** Kết quả đo Z-offset bằng công tắc tự động (Axiscope switch) cho thấy độ lặp lại tốt nhưng khi in thực tế lớp 1 không phẳng đẹp bằng bộ thông số đã tinh chỉnh khi in (`T1: 0.228, T2: -0.295, T3: -0.268, T4: 0.086`) do các yếu tố lực đẩy đàn hồi của switch, vị trí đo $Y=-10$ và giãn nở nhiệt ở nhiệt độ in.
**Đã chọn:** Sử dụng bộ giá trị đã kiểm chứng in thực tế đẹp làm cấu hình sản xuất trong `printer.cfg`. Sử dụng giá trị đo của công tắc làm mốc tham chiếu phần cứng (Baseline Delta) để kiểm tra độ trôi sau này.
**Đã loại:** Ép dùng giá trị đo công tắc thô chưa bù lực cản (gây hở sợi ở T1/T4 và cào bàn ở T3).
**Lý do:** Đảm bảo 100% chất lượng bản in lớp đầu tiên hoàn hảo mà vẫn tận dụng được công tắc cơ học để kiểm tra phần cứng nhanh khi thay thế nozzle.

## 2026-08-09 — Cấu hình chân Microswitch Z-Offset sang PF2 (Manta M8P V2)

**Bối cảnh:** Người dùng lắp đặt công tắc vi mô để đo Z-offset giữa các tool tại tọa độ X:68, Y:-10, Z:7 và đấu nối vào cổng PF2 + GND trên bo mạch BTT Manta M8P V2 thay vì PF4.
**Đã chọn:** `pin: ^PF2` trong section `[axiscope]` của `calibration.cfg`.
**Đã loại:** `pin: ^PF4` — không khớp với đấu nối thực tế trên phần cứng.
**Lý do:** Khớp chính xác với sơ đồ chân thực tế, cổng PF2 hoàn toàn độc lập và không trùng với bất kỳ endstop nào của stepper X/Y/Z.

## 2026-08-06 — Đồng bộ thư mục sao lưu và cấu hình tải về lên GitHub

**Bối cảnh:** Người dùng yêu cầu đồng bộ toàn bộ lịch sử sao lưu (`extras/backups/`) và bản tải cấu hình (`extras/Config download/`) lên GitHub để phòng ngừa rủi ro hỏng máy tính cá nhân.
**Đã chọn:** Bỏ bỏ qua (un-ignore) `extras/backups/` và `extras/Config download/` trong `.gitignore`, tiếp tục bảo mật nghiêm ngặt các file nhạy cảm (`*.secrets`, `moonraker.secrets`, `wpa_supplicant.conf`, `*.key`, `*.pem`, `*.env`, `*.log`).
**Đã loại:** Chỉ giữ sao lưu cục bộ (mất dữ liệu nếu phần cứng máy tính hỏng).
**Lý do:** Đáp ứng nhu cầu an toàn dữ liệu trên cloud của người dùng mà vẫn đảm bảo 100% không lộ thông tin nhạy cảm.

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

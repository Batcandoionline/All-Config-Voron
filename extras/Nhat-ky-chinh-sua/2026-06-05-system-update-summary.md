# 2026-06-05 - Tổng hợp cập nhật hệ thống

## Mục tiêu

Tổng hợp các thay đổi lớn đã đưa vào cấu hình Voron/StealthChanger sau đợt ổn định prime line, print-start và quy trình cập nhật từ GitHub.

## Cấu trúc repository

- Sắp xếp lại repository thành 2 nhóm chính:
  - `config/`: cấu hình Klipper/Moonraker thật sự được copy về máy Voron.
  - `extras/`: tệp tham khảo, log, hình ảnh, G-code, tài liệu và project phụ không được copy vào `~/printer_data/config`.
- Xóa thư mục backup cũ `config_full_backup_before_english_comments_...` khỏi repository vì cấu hình hiện tại đã ổn định.
- Di chuyển các phần không cần chạy trên Voron vào `extras/`, giúp thư mục `config/` gọn và dễ đọc hơn.

## Script install/update

- `config/scripts/install.sh` và `config/scripts/update.sh` chỉ copy nội dung trong `config/` về `~/printer_data/config`.
- Thêm cơ chế tạo backup trên máy Voron trước khi cập nhật:
  - Backup được lưu tại `~/printer_data/config_backups/config-YYYYMMDD-HHMMSS`.
  - Mặc định giữ các backup mới nhất, tránh làm đầy thư mục home.
- Thêm `config/scripts/cleanup-voron.sh` để dọn các thư mục cũ/không còn dùng trên máy Voron. Script chạy dry-run mặc định, chỉ xóa khi thêm `--apply`.

## PRINT_START và QGL

- Điều chỉnh `PRINT_START` để tránh toolchange/dock trước khi full `G28`.
- Bỏ lần QGL sớm khi bàn còn đang nóng lên. QGL hiện chỉ chạy sau khi:
  - `M190` đã chờ bàn đạt nhiệt.
  - Heat soak, nếu cần, đã hoàn tất.
- Lý do: Cartographer và bàn đang drift nhiệt có thể làm QGL retry tăng dần, dẫn tới lỗi:
  - `Probed points range is increasing`
  - `Possibly Z motor numbering is wrong`
- Xóa `G28 Z` thừa sau `QUAD_GANTRY_LEVEL` trong `PRINT_START`, vì wrapper `QUAD_GANTRY_LEVEL` đã tự kết thúc bằng `G28 Z`.
- Cập nhật các hướng dẫn calibration cũ từ:
  - `G28 -> QUAD_GANTRY_LEVEL -> G28 Z`
  thành:
  - `G28 -> QUAD_GANTRY_LEVEL`

## Quản lý nhiệt tool trong PRINT_START

- Các tool có dùng trong file in được giữ ở standby khoảng 150 độ C trong giai đoạn chuẩn bị.
- Tool không dùng sẽ tắt nhiệt.
- T0 bị giới hạn ở nhiệt probe/touch-home cho đến khi Cartographer touch home xong.
- Sau touch-home:
  - Tool sắp prime đầu tiên được nâng lên nhiệt in trong lúc mesh đang chạy.
  - Các tool dùng còn lại giữ standby để giảm thời gian chờ nhiệt nhưng hạn chế nhựa chảy ra.

## Prime line nhiều tool

- Thêm/hoàn thiện `PRIME_LINES` cho hệ multi-tool.
- Prime các tool có sử dụng trong G-code slicer, tool in đầu tiên được prime cuối cùng để sau prime đầu in sẵn sàng bắt đầu in.
- Chuyển bố cục prime line về phía trước giữa bàn, tránh quá gần các góc.
- Mỗi tool vẽ 3 đường song song theo trục X, tổng chiều dài khoảng 40 mm để có đủ thời gian ra nhựa.
- Giảm nguy cơ tạo sợi dài khi dock bằng các thao tác retract/wipe/standby trong logic prime.

## Hiệu chỉnh tool offset

- Cập nhật Z offset theo kết quả test first layer thực tế:
  - T1 bù sai lệch khoảng +0.07 mm.
  - T3 bù sai lệch khoảng +0.26 mm.
  - T4 bù sai lệch khoảng +0.26 mm.
  - T2 tạm thời để riêng vì đang nghi ngờ có vấn đề cơ khí/nhiệt đầu in.
- Các giá trị được đưa vào `printer.cfg`/`SAVE_CONFIG` để khớp với thực tế in, không phải lỗi do prime line.

## Moonraker và Tailscale

- Thêm dải Tailscale vào `moonraker.conf`:
  - `100.64.0.0/10`
  - `fd7a:115c:a1e0::/48`
- Mục đích: cho phép truy cập Mainsail/Moonraker qua IP Tailscale từ xa mà không bị chặn authorization/CORS.

## Dọn Axiscope

- Axiscope không còn dùng trong cấu hình chạy chính.
- Phần liên quan được đưa về khu vực tham khảo/backup, không nằm trong payload cập nhật trực tiếp vào máy Voron.

## Lưu ý vận hành

Sau khi cập nhật macro Klipper:

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart klipper
```

Chỉ cần restart Moonraker khi thay đổi `moonraker.conf`.

Khi cập nhật từ GitHub về Voron, script sẽ tự tạo backup trước khi copy file mới.

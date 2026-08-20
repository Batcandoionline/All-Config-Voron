# Nhật ký — 2026-08-20

## 1. Rebuild Tool Vision 2 thành hệ thống đo XYZ độc lập phần cứng

### Mục tiêu
Xóa implementation Tool Vision cũ và xây dựng lại hệ thống đo offset X/Y bằng
camera hướng lên, đo Z bằng microswitch, kế thừa đúng chiều offset và quy trình
từ kTAMV/Axiscope nhưng không cố định độ phân giải hay đường dẫn phần cứng.

### File đã sửa đổi
- `.gitattributes` — ép LF cho source, cấu hình và shell script của Tool Vision.
- `extras/Tool-Vision/.gitignore` — loại cache/test artifact khỏi Git.
- `extras/Tool-Vision/README.md` — viết lại kiến trúc, commissioning và quy tắc an toàn.
- `extras/Tool-Vision/tool_vision.cfg` — cấu hình portable cho camera, detector,
  trạm đo, tốc độ, calibration, probe và workflow hook.
- `extras/Tool-Vision/klippy/extras/tool_vision.py` — viết lại Klipper extension
  điều phối camera, chuyển động an toàn, probe Z và báo cáo XYZ.
- `extras/Tool-Vision/server/` — thay server cũ bằng API versioned, camera I/O
  native-resolution, detector ổn định nhiều frame và affine/quadratic transform.
- `extras/Tool-Vision/install.sh` — viết lại installer tự nhận user/home/path.
- `extras/Tool-Vision/uninstall.sh` — thêm gỡ cài đặt có guard cho virtualenv.
- `extras/Tool-Vision/tests/` — thêm test deterministic cho API, camera/detector,
  transform, dấu offset và thứ tự chuyển động.
- Xóa `server/vision_io.py`, `server/vision_dm.py`, `server/vision_server.py` và
  `server/tool_vision.service` của implementation cũ.

### Sao lưu
- [Tool Vision trước rebuild](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-tool-vision-rebuild-20260820-154154/)

### Chi tiết thay đổi
- Loại bỏ toàn bộ hằng số/resize `640x480`; detector đọc kích thước thật từ
  `frame.shape`, còn target, ROI và blob area được cấu hình bằng tỉ lệ.
- Hỗ trợ HTTP JPEG/MJPEG, RTSP/OpenCV, `/dev/video*` và camera index; width,
  height, FPS bằng `0` để camera tự chọn native/default mode.
- Fit phép biến đổi `machine_delta = transform(pixel_delta)` và buộc recalibrate
  khi độ phân giải camera thay đổi.
- Giữ chiều XY `raw_current - raw_reference` của kTAMV và chiều Z
  `trigger_current - trigger_reference` của Axiscope.
- Luôn nâng Z tới safe height trước khi chạy XY sang camera hoặc microswitch.
- Từ chối safe Z thấp hơn measurement/approach Z và từ chối danh sách tool
  rỗng, âm hoặc trùng lặp ngay khi Klipper đọc cấu hình.
- Chặn chạy khi máy đang print/paused, chặn nhiều job camera đồng thời và chặn
  đổi cấu hình camera giữa lúc một job detection đang chạy.
- Chỉ ghi kết quả atomically vào `tool_vision_results.json`; không tự sửa
  production offset, không gọi `SAVE_CONFIG` hoặc `SAVE_TOOL_PARAMETER`.
- Tọa độ camera mẫu được để comment vì chưa có số đo phần cứng thật. Production
  `[axiscope]` và các file config đang chạy không bị sửa hoặc include Tool Vision.

### Lý do
Implementation cũ chứa giả định 640x480, đường dẫn service/user cố định, quy
trình station chưa đủ an toàn và khả năng ghi trực tiếp offset. Thiết kế mới cần
dùng được trên các máy khác chỉ bằng thay đổi `.cfg`, đồng thời giữ kết quả đo ở
chế độ report-only cho đến khi được kiểm chứng bằng phần cứng và first-layer test.

### Kiểm tra
- Xác minh 7/7 file implementation cũ trong backup khớp Git blob trước rebuild: đạt.
- Python unit/integration tests: `22/22` đạt.
- Native-resolution detector: đạt với `1280x720`, `800x600` và rotation 90 độ.
- Kiểm tra dấu XY/Z theo kTAMV/Axiscope: đạt.
- Kiểm tra safe-Z-before-XY và guard thiếu tọa độ camera: đạt.
- Parse `tool_vision.cfg` strict, một section và không trùng option: đạt.
- Python compile và Ruff `E,F`: đạt.
- Shell parse cho `install.sh` và `uninstall.sh`: đạt.
- Render service template với project/log path chứa khoảng trắng: đạt.
- `git diff --check`: đạt.
- Khởi động lại Klipper/thử phần cứng/thử in: chưa thực hiện vì Tool Vision chưa
  được deploy/include và tọa độ camera thật chưa được cung cấp.

### Kết quả
Hoàn thành codebase Tool Vision 2 độc lập phần cứng ở mức host-side, có cấu hình
camera native-resolution, đo XYZ report-only, tài liệu commissioning và bộ test
logic. Cấu hình production hiện hành được giữ nguyên an toàn.

### Vấn đề còn lại
- Đo và điền `camera_x_pos`, `camera_y_pos`, `camera_z_pos`, `camera_safe_z` thật.
- Cài service trên Klipper host, xác nhận stream camera và switch pin thực tế.
- Chỉ disable `[axiscope]` rồi include `[tool_vision]` khi bắt đầu commissioning.
- Chạy tuần tự T0, một tool phụ, sau đó mới chạy toàn bộ tool và đối chiếu với
  first-layer print trước khi áp dụng bất kỳ offset nào.

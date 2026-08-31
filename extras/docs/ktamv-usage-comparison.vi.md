# Sử dụng kTAMV và đối chiếu phương pháp

[English](ktamv-usage-comparison.en.md) | [Tiếng Việt](ktamv-usage-comparison.vi.md)

Tài liệu này mô tả tích hợp kTAMV cài trên Voron năm tool ngày 2026-08-31 và
đối chiếu workflow vận hành với tích hợp ToolVision đã retired. Upstream đã đọc
là [TypQxQ/kTAMV](https://github.com/TypQxQ/kTAMV) tại commit
`72421f2d54da0de8701c4f84449c6e6b7d060301`. Commit này vẫn là `main`/HEAD và có
ngày 2024-04-02.

## Trạng thái cài đặt

| Hạng mục | Giá trị |
| --- | --- |
| Source | `/home/voron/kTAMV` tại commit `72421f2` đã review |
| Bản sửa local | `ktamv-multi-object-selection.patch` và `ktamv-center-highlight-fallback.patch` |
| Python | `/home/voron/ktamv-env`, dùng OpenCV package hệ thống |
| Service | user unit `ktamv-server.service` |
| Server | `http://192.168.1.43:8086/` |
| Ảnh xử lý | `http://192.168.1.43:8086/image` |
| Camera nguồn | `http://127.0.0.1/webcam/?action=snapshot` |
| Config Klipper | `config/Printer-Setup/ktamv.cfg` |
| Upload cloud | `false` |
| Unit ToolVision cũ | Đã disable/xóa và `daemon-reload` bằng sudo |

Không chạy installer upstream. Script đó đổi giờ hệ thống, chạy `apt` toàn máy,
ghi header Moonraker thừa `]`, sửa config active và restart service. Máy này dùng
bản cài thủ công được pin và user service.

Runtime, venv, symlink, generated data và log ToolVision thuộc user đã được gỡ.
Unit cũ thuộc `root` cũng đã được dọn bằng các lệnh giới hạn sau:

```bash
sudo systemctl disable --now tool-vision.service
sudo rm -f /etc/systemd/system/tool-vision.service
sudo systemctl daemon-reload
```

## kTAMV thực sự làm gì

kTAMV gồm extension Klipper và server ảnh Flask/Waitress. Server ép frame thành
640×480 rồi thử năm pipeline tiền xử lý/detector OpenCV upstream. Bản sửa local
loại keypoint “super relaxed” cách tâm quá 120 pixel và dùng phản xạ sáng gọn
gần tâm làm pipeline fallback thứ sáu. Vị trí nozzle phải lặp ba lần trong
`detection_tolerance`; cấu hình hiện dùng 0 pixel.

Camera calibration lấy mười điểm cách vị trí đầu khoảng tối đa 0.5 mm. Nó cần ít
nhất 75% sample hợp lệ, lọc outlier mm/pixel và tạo transform camera–máy. Lệnh
căn tâm sau đó nhận diện nozzle và jog X/Y đến khi correction bằng 0.

Các sự thật quan trọng từ source:

- kTAMV chỉ đo X/Y, không có workflow Z.
- Camera calibration, transform và origin chỉ nằm trong RAM.
- `KTAMV_GET_OFFSET` báo `raw XY hiện tại - raw XY origin`, không tự lưu.
- `calib_iterations` và `calib_value` được đọc nhưng command path đã review
  không sử dụng.
- `move_speed` được expose thành `printer.ktamv.travel_speed` cho macro, nhưng
  camera calibration native dùng mặc định `F3000`, còn căn tâm dùng `F1000`.
- README nêu `KTAMV_MOVE_TO_ORIGIN`, nhưng Python không đăng ký lệnh này. Repo
  chỉ có macro ví dụ riêng và máy này không include macro đó.
- Guard local cho `statistics.stdev()` trả độ lệch chuẩn 0 khi chỉ còn một
  sample; kiểm tra giữ tối thiểu 75% điểm của caller vẫn buộc calibration lỗi
  rõ ràng thay vì phát exception Python.

## Thiết lập ánh sáng MF-500 hiện tại

- Vòng soi nozzle là WCMCU WS2812B tám LED do ESP32-C3 Mini cấp nguồn/điều
  khiển riêng ở độ sáng 5%; nó không nối Klipper.
- `T0_LED` là ba LED trên toolhead, hoàn toàn khác vòng camera. Ba LED này tạo
  bóng phản xạ dưới nozzle và phải tắt trong lúc dùng camera:

```gcode
SET_LED LED=T0_LED RED=0 GREEN=0 BLUE=0 TRANSMIT=1
```

- `RESTART` chạy `LED_INIT` và có thể bật lại LED toolhead. Luôn gửi lại lệnh
  trên trước `KTAMV_SETUP`.
- Giữ camera MF-500 tại `brightness=0`, `contrast=36`, `gamma=120`. Các phép
  thử giảm brightness/contrast làm detector tệ hơn và đã được hoàn nguyên.
- Ở cảnh này, marker đúng nằm trên phản xạ tròn màu trắng gần `[336,253]` của
  ảnh processed 640×480. Marker `[192,134]` trên góc trên-trái khối nhôm là bắt
  nhầm và không được dùng cho calibration.

## Phân loại an toàn lệnh

### Không chủ động di chuyển máy

| Lệnh | Tác dụng |
| --- | --- |
| `KTAMV_SETUP` / `KTAMV_SEND_SERVER_CFG` | Gửi camera URL và tùy chọn detector sang server |
| `KTAMV_STATUS` | Báo calibrated, mm/pixel và origin |
| `KTAMV_START_PREVIEW` / `KTAMV_STOP_PREVIEW` | Bật/tắt xử lý preview |
| `KTAMV_SIMPLE_NOZZLE_POSITION` | Nhận diện và báo tọa độ pixel nozzle |
| `KTAMV_SET_ORIGIN` | Lưu raw X/Y hiện tại làm reference |
| `KTAMV_GET_OFFSET` | Báo raw X/Y hiện tại trừ origin |
| `KTAMV_APPLY_ACTIVE_TOOL_XY` | Stage mean XY cuối vào KTC; không di chuyển, cần `SAVE_CONFIG` riêng |

### Có di chuyển máy

| Lệnh | Chuyển động |
| --- | --- |
| `KTAMV_CALIB_CAMERA` | Mười move nhỏ X/Y và có thể thêm move cuối tới tâm |
| `KTAMV_FIND_NOZZLE_CENTER` | Correction X/Y lặp; có thể wiggle 0.1–0.2 mm khi mất detection |
| `KTAMV_MEASURE_ACTIVE_TOOL_XY SAMPLES=3` | Trở về origin ở Z40 rồi căn tâm ba lần, báo mean/spread |

Hai lệnh có chuyển động yêu cầu đã home X/Y/Z. Chỉ chạy khi operator đứng tại
máy, camera/dây chắc chắn, đường dock trống và emergency stop sẵn sàng. Khi lỗi,
kTAMV không đảm bảo trở về chính xác tọa độ bắt đầu.

Phiên đo 2026-08-31 dùng Z40 do operator xác nhận, tắt LED của từng tool và
không điều khiển vòng ESP32-C3 5% độc lập. Heater target luôn bằng 0.

## Workflow đối chiếu thủ công

Không bắt đầu chỉ vì kiểm tra cài đặt đạt. Trước tiên làm sạch nozzle, dùng ánh
sáng mềm/đều, focus rõ lỗ nozzle và để đủ margin cho pattern 0.5 mm.

1. Khi máy idle và có người giám sát, home bằng workflow bình thường rồi chọn T0
   có offset X/Y bằng 0.
2. Đưa T0 gần tâm camera ở Z an toàn. Tắt `T0_LED`, giữ vòng ESP32-C3 ở 5%, rồi
   chạy `KTAMV_SETUP`, preview và `KTAMV_SIMPLE_NOZZLE_POSITION`. Chỉ chấp nhận
   khi marker bám đúng phản xạ trung tâm và nhiều lần trả cùng tọa độ.
3. Tắt preview rồi chạy `KTAMV_CALIB_CAMERA`. Chỉ tiếp tục khi `KTAMV_STATUS`
   báo calibrated và mm/pixel hợp lệ.
4. Chạy `KTAMV_FIND_NOZZLE_CENTER`, sau đó `KTAMV_SET_ORIGIN` đúng một lần cho T0.
5. Với từng T1–T4, chọn qua KTC rồi chạy
   `KTAMV_MEASURE_ACTIVE_TOOL_XY SAMPLES=3`. Wrapper tắt `Tn_LED`, giữ Z40,
   đưa nozzle về cùng origin trước mỗi sample và báo raw samples, mean, spread.
6. Chỉ khi active/detected tool khớp, đủ ba sample và spread mỗi trục không quá
   `0.12 mm`, chạy `KTAMV_APPLY_ACTIVE_TOOL_XY`. Ứng viên được tính bằng
   `offset đang nạp + mean residual`; T0 bị chặn vì là reference.
7. Sau khi review tất cả tool, chạy `SAVE_CONFIG` đúng một lần. Lệnh này restart
   Klipper và xóa calibration/origin RAM. Z ngoài phạm vi và luôn giữ nguyên.

## Các bản sửa mã nguồn kTAMV trên máy này

- `ktamv-multi-object-selection.patch`: sửa truy cập keypoint và method binding
  khi pipeline trả nhiều vật thể.
- `ktamv-center-highlight-fallback.patch`: loại keypoint quá xa tâm, thêm
  detector highlight compact cho MF-500/vòng 5%, và guard `stdev` một sample.
- `ktamv-repeat-xy-measurement.patch`: sửa bộ lọc mm/pixel không còn mutate list
  caller, xóa đồng bộ MPP/space/camera, trả tuple nhất quán khi fail, kiểm tra
  thật tỷ lệ giữ 75%; thêm `KTAMV_MEASURE_TOOL_XY` cùng state raw/mean/spread,
  Z40 và guard active/detected tool.

Hai macro user-facing trong `Printer-Setup/ktamv.cfg` tách đo và áp dụng có chủ
ý. Không ghép chúng trong một macro vì Jinja của Klipper render trước khi lệnh
native đo cập nhật status; tách riêng cũng tạo điểm review trước khi stage.

## kTAMV so với ToolVision đã retired

| Mặt so sánh | kTAMV | Tích hợp ToolVision đã retired |
| --- | --- | --- |
| Trục | Chỉ X/Y | X/Y cộng Z bằng switch hoặc Cartographer Touch |
| Mô hình ảnh | Pipeline OpenCV cố định 640×480 | Profile học ở native resolution và kiểm tra ambiguity |
| Workflow | Từng command thủ công | Setup hướng dẫn và batch năm tool |
| Persistence | Mất sau Klipper restart | State, latest result và history trên disk |
| Thống kê | Từng quan sát; operator tự lặp/ghi | Batch attempt và statistic từng tool |
| Áp offset | Chỉ báo số | Máy này cũng cấu hình report-only |
| Recovery | Giới hạn; lệnh native có thể để vị trí lệch | Kiểm tra restore KTC và evidence cleanup |
| Update | Pin/thủ công do có patch local | Trước đây do Moonraker quản lý |

Đây không phải kết luận detector nào luôn tốt hơn. Với MF-500 cụ thể này, cả hai
hệ thống đều gặp vật thể phản xạ mơ hồ. Lần kTAMV 2026-08-22 chỉ nhận 6/10 điểm;
marker nằm trên vùng sáng bên dưới lỗ nozzle thật và một scale hợp lệ `0.028`
lệch cụm `0.041–0.044`. ToolVision cũng từ chối cảnh vì có nhiều vật thể giống
nozzle. Phải cải thiện cảnh quang học trước mọi test chuyển động mới.

## Thêm ảnh xử lý vào Mainsail

Có thể thêm webcam riêng:

- Name: `kTAMV Processed`;
- Stream URL: để trống;
- Snapshot URL: `http://192.168.1.43:8086/image`;
- Service: Adaptive MJPEG-Streamer;
- Target FPS: 2–4.

Dùng IP máy in, không dùng `localhost`, vì Mainsail resolve URL trong trình
duyệt. Đây là output detector, không thay webcam MF-500 gốc.

## Kiểm tra không chuyển động và xử lý lỗi

Trên host:

```bash
systemctl --user status ktamv-server
journalctl --user -u ktamv-server -n 100 --no-pager
curl --fail http://127.0.0.1:8086/
```

Sau khi Klipper nạp config, `KTAMV_STATUS`, `CALIBRATION_STATUS` và
`CHECK_OFFSETS` là kiểm tra không chuyển động. `Camera URL not set` được xử lý
bằng `KTAMV_SETUP`. `No nozzle found` yêu cầu sửa cảnh quang học, không tăng mù
quáng tolerance. Camera calibration mất hơn 25% điểm là điểm dừng: không tiếp
tục căn tâm hay lấy offset.

Restart Klipper làm mất calibration/origin theo thiết kế. Runtime không có cơ
chế persistence hoặc tự ghi offset.

Sau thay đổi ánh sáng 2026-08-31, hai phép nhận diện tĩnh trước/sau `RESTART`
đều trả `[336,253]` sau 5,42/5,09 giây. Chưa chạy lại calibration vì bước đó có
chuyển động và `RESTART` đã xóa trạng thái home.

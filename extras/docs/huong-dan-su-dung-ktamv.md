# Hướng dẫn thử nghiệm kTAMV trên Voron 5 Tool

Tài liệu này áp dụng cho cấu hình kTAMV tạm thời của máy tại ngày 2026-08-22.
Source chính thức được pin tại commit
`72421f2d54da0de8701c4f84449c6e6b7d060301`; đây cũng là HEAD mới nhất của
nhánh `main` khi kiểm tra.

## Giới hạn bắt buộc phải hiểu

- kTAMV chỉ đo/căn **X và Y**. Nó không đo Z và không dùng switch PF2.
- kTAMV không tự ghi `gcode_x_offset` hoặc `gcode_y_offset` vào tool config.
- Camera matrix, mm/pixel và origin chỉ nằm trong RAM. Klipper hoặc kTAMV server
  restart là phải setup/calibrate lại.
- `KTAMV_GET_OFFSET` báo `raw XY hiện tại - raw XY của origin`; chưa được phép
  xem kết quả này là offset production cho đến khi kiểm tra dấu và đo lặp.
- Đây là phần mềm dành cho người dùng nâng cao. Mọi lệnh có chuyển động phải có
  người đứng cạnh máy và sẵn sàng Emergency Stop.

## Trạng thái cài đặt của máy

| Thành phần | Giá trị |
|---|---|
| Source | `/home/voron/kTAMV` |
| Python environment | `/home/voron/ktamv-env` |
| Server | `ktamv-server.service` của user |
| Server URL | `http://192.168.1.43:8086` |
| Ảnh đã xử lý | `http://192.168.1.43:8086/image` |
| Log web | `http://192.168.1.43:8086/` |
| Camera nguồn | `http://127.0.0.1/webcam/?action=snapshot` |
| Cloud upload | Tắt |

Kiểm tra service qua SSH:

```bash
systemctl --user status ktamv-server
journalctl --user -u ktamv-server -f
```

## Thêm ảnh xử lý kTAMV vào Mainsail

Trong **Settings → Webcams → Add Webcam**:

- Name: `kTAMV Processed`
- Stream URL: để trống
- Snapshot URL: `http://192.168.1.43:8086/image`
- Service: `Adaptive MJPEG-Streamer`
- Target FPS: `2` hoặc `4`

Đây là ảnh detector đã xử lý, không thay thế webcam MF-500 gốc. Khi mở Mainsail
từ máy khác, phải dùng IP `192.168.1.43`; không dùng `localhost`.

## Phân loại lệnh

### Không làm máy di chuyển

| Lệnh | Tác dụng |
|---|---|
| `KTAMV_SETUP` | Gửi URL camera và cấu hình hiện tại sang server |
| `KTAMV_STATUS` | Báo calibrated, mm/pixel, origin và last offset |
| `KTAMV_SEND_SERVER_CFG` | Lệnh native tương đương `KTAMV_SETUP` |
| `KTAMV_START_PREVIEW` | Bật xử lý ảnh preview |
| `KTAMV_STOP_PREVIEW` | Dừng preview để giảm tải CPU/camera |
| `KTAMV_SIMPLE_NOZZLE_POSITION` | Chỉ nhận diện và báo pixel; không jog |
| `KTAMV_SET_ORIGIN` | Lưu raw X/Y hiện tại làm mốc T0; không jog |
| `KTAMV_GET_OFFSET` | Báo raw X/Y hiện tại trừ origin; không jog |

### Có làm máy di chuyển

| Lệnh | Chuyển động thực tế |
|---|---|
| `KTAMV_CALIB_CAMERA` | Chạy 10 điểm quanh vị trí đầu, bán kính tối đa khoảng 0.5 mm, rồi có thể dịch tới tâm tính toán |
| `KTAMV_FIND_NOZZLE_CENTER` | Lặp nhận diện và jog X/Y tới tâm; khi mất nozzle có thể wiggle khoảng 0.1–0.2 mm |

Hai lệnh trên yêu cầu đã home đủ X/Y/Z. Nếu nhận diện thất bại, vị trí cuối có
thể lệch nhẹ so với điểm bắt đầu; không mặc định máy đã tự trở về đúng tọa độ cũ.

`KTAMV_MOVE_TO_ORIGIN` có trong mô tả README upstream nhưng không được đăng ký
bởi Python của commit đang cài và không có trong cấu hình máy này. Không sử dụng
lệnh đó.

## Chuẩn bị camera và nozzle

1. Máy phải idle, không in, heater/fan không chạy quy trình tự động.
2. Lắp MF-500 chắc chắn vào gá camera dưới nozzle; kiểm tra dây không cản gantry.
3. Làm sạch đầu nozzle để nhìn rõ lỗ tròn. Dùng ánh sáng mềm, đều, tránh phản xạ.
4. Home đầy đủ XYZ và chọn T0 bằng workflow toolchange bình thường.
5. Jog thủ công với Z an toàn đến gần tâm camera. Hạ dần theo ảnh preview; không
   dùng tọa độ camera cũ nếu gá vừa tháo/lắp lại.
6. Chỉ tiếp tục khi ảnh nét, lỗ nozzle gần tâm và xung quanh còn đủ khoảng trống
   cho chuyển động calibration 0.5 mm.

## Quy trình hiệu chuẩn camera bằng T0

Chạy từng lệnh, chờ lệnh trước kết thúc rồi mới tiếp tục:

```gcode
KTAMV_SETUP
KTAMV_STATUS
KTAMV_START_PREVIEW
```

Jog thủ công cho nozzle T0 gần tâm/focus tốt, sau đó:

```gcode
KTAMV_SIMPLE_NOZZLE_POSITION
KTAMV_STOP_PREVIEW
KTAMV_CALIB_CAMERA
KTAMV_STATUS
```

Chỉ tiếp tục nếu status báo `calibrated=True` và `mm_per_pixel` có giá trị.
Camera calibration cần ít nhất 75% điểm hợp lệ và độ lệch thống kê không quá
ngưỡng nội bộ của kTAMV.

Sau đó căn chính xác T0 và đặt origin **một lần**:

```gcode
KTAMV_FIND_NOZZLE_CENTER
KTAMV_SET_ORIGIN
KTAMV_STATUS
```

T0 là tool tham chiếu và hiện có X/Y offset bằng 0. Không chạy lại
`KTAMV_SET_ORIGIN` cho T1–T4, nếu không sẽ mất mốc so sánh.

## Đo T1 đến T4

Với từng tool, làm riêng từng lượt:

1. Toolchange bằng lệnh `T1`, `T2`, `T3` hoặc `T4` theo đúng quy trình KTC.
2. Jog nozzle về gần tâm camera ở đúng khoảng focus; bảo đảm camera/gá không nằm
   trên đường dock hoặc đường di chuyển tool.
3. Chạy kiểm tra không chuyển động:

   ```gcode
   KTAMV_SIMPLE_NOZZLE_POSITION
   ```

4. Khi nhận diện ổn định, chạy:

   ```gcode
   KTAMV_FIND_NOZZLE_CENTER
   KTAMV_GET_OFFSET
   KTAMV_STATUS
   ```

5. Ghi lại X/Y cùng tên tool. Đo tối thiểu ba lượt để kiểm tra độ lặp.
6. Không chạy `KTAMV_SET_ORIGIN` giữa các tool và không `SAVE_CONFIG` chỉ dựa
   trên một kết quả kTAMV.

Offset production đang lưu để đối chiếu, không phải giá trị cần ghi lại ngay:

| Tool | X hiện tại | Y hiện tại |
|---|---:|---:|
| T0 | 0.000 | 0.000 |
| T1 | -0.243 | -0.252 |
| T2 | 0.746 | 0.086 |
| T3 | 0.304 | 0.449 |
| T4 | 0.041 | 0.352 |

Nếu kết quả kTAMV gần bằng giá trị đối dấu, dao động lớn giữa các lượt hoặc khác
xa offset hiện tại, dừng lại và kiểm tra quy ước dấu trước khi sửa cấu hình.
Offset Z hiện tại phải giữ nguyên vì kTAMV không đo Z.

## Sau khi thử nghiệm

```gcode
KTAMV_STOP_PREVIEW
KTAMV_STATUS
CHECK_OFFSETS
```

Tháo camera chỉ sau khi toolhead đã được jog lên vị trí an toàn. Không để camera
hoặc dây trong vùng chuyển động khi in.

## Xử lý lỗi nhanh

- `Camera URL not set`: chạy `KTAMV_SETUP`.
- `No nozzle found`: đưa nozzle gần tâm hơn, làm sạch nozzle, chỉnh focus/Z và
  ánh sáng; kiểm tra trước bằng `KTAMV_SIMPLE_NOZZLE_POSITION`.
- `Camera is not calibrated`: chạy lại `KTAMV_CALIB_CAMERA` với T0.
- Calibration thất bại quá 25% điểm: không tiếp tục; cải thiện ảnh rồi làm lại.
- Server không phản hồi: kiểm tra `systemctl --user status ktamv-server` và mở
  `http://192.168.1.43:8086/`.
- Klipper/server restart: chạy lại toàn bộ setup, camera calibration và origin.

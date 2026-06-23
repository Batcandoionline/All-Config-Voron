# 2026-06-14 - Cartographer, camera và first layer

## Mục tiêu

Tổng hợp các việc đã kiểm tra và cập nhật gần đây cho hệ Voron StealthChanger:

- Cartographer mới, bù nhiệt và axis twist compensation.
- First layer bị lệch trái/phải trên bản in lớn.
- `PRINT_START`, vật liệu và heat soak.
- Camera/Crowsnest FPS.
- Các điểm cần kiểm chứng trước khi tiếp tục sửa cấu hình.

## Cartographer và SAVE_CONFIG

Đã cập nhật giá trị Cartographer coil calibration mới vào `printer.cfg` sau khi thay Cartographer và calib lại:

```ini
#*# [cartographer]
#*# calibration = -3.0631913588505464e-05,32.154321835673606,0.0,2e-323
```

Đã cập nhật thêm Z offset của T1 theo kết quả in thực tế:

```ini
#*# [tool T1]
#*# gcode_z_offset = -0.11600000001828106
```

## Axis twist và lỗi bên trái bàn in

Hiện tượng: bản in lớn có phía bên trái thấp hơn bên phải; first layer/layer ở bên trái bị hở, trong khi bên phải đẹp hơn.

Giá trị cũ trong repo:

```ini
#*# z_compensations = -0.022155, -0.013439, -0.009776, -0.006336, 0.051706
```

Giá trị đo mới trong log 07:03:

```text
offsets: (-0.148836, -0.003871, 0.027423, 0.059587, 0.065697)
probe X20  = z 2.001393
probe X320 = z 1.800860
chênh lệch gần 0.2005 mm
```

Giá trị `SAVE_CONFIG` mới nhất người dùng gửi sau bản in lớn 16 tiếng ổn định, bề mặt khá đẹp:

```ini
#*# z_compensations = -0.165817, 0.004053, 0.034914, 0.057630, 0.069220
```

Đánh giá: axis twist có khả năng là nguyên nhân lớn làm lệch first layer trái/phải, vì sai lệch phụ thuộc vị trí X trên bàn in. Bộ giá trị trên được ưu tiên làm baseline mới vì đã qua bản in lớn 16 tiếng ổn định.

Các dấu hiệu cần cẩn thận trong log:

- Có lần đo báo `Unable to find 3 samples within 0.010mm in a window of 5 after 10 touches`.
- Có lần báo `Error during axis twist compensation calibration, existing compensation has been cleared`.
- Có giá trị probe bất thường rất lớn quanh `z=509`/`z=511`.
- Một số lần dùng `SET_HEATER_TEMPERATURE` không chờ ổn định nhiệt, khiến bed/nozzle/probe có thể vẫn đang drift.

Quy trình đo lại an toàn để xác nhận:

```gcode
FIRMWARE_RESTART
T0
M109 S150
M190 S70
G4 P600000
G28
QUAD_GANTRY_LEVEL
CARTOGRAPHER_AXIS_TWIST_COMPENSATION USE_TOUCH_BOUNDARIES=no AXIS=x SAMPLE_COUNT=5
```

Chỉ nên `SAVE_CONFIG` nếu lặp lại 2-3 lần ra kết quả gần nhau, sai khác khoảng dưới 0.02-0.03 mm. Nếu macro báo lỗi, nên `FIRMWARE_RESTART` trước khi đo lại và không save kết quả lỗi.

## PRINT_START, MATERIAL và heat soak

Đã kiểm tra file G-code `gridfinity_PETG_7h56m.gcode`. Dòng start G-code thực tế có truyền vật liệu:

```gcode
PRINT_START TOOL_TEMP=230 T1_TEMP=230 BED_TEMP=70 TOOL=1 MATERIAL=PETG
```

Kết luận: biến `MATERIAL={filament_type[initial_tool]}` đang được OrcaSlicer truyền đúng với PETG.

Logic soak hiện tại:

- `MATERIAL=PLA` hoặc `TPU`: soak mặc định 90 giây.
- `MATERIAL=PETG`: soak mặc định 240 giây.
- `MATERIAL=ABS`, `ASA`, `PC`, `NYLON`, `PA`: soak mặc định 600 giây.
- Nếu không truyền `MATERIAL`, hệ thống fallback theo nhiệt bàn: bed từ 90 độ C trở lên và bắt đầu từ trạng thái nguội thì soak 240 giây.

QGL được thực hiện sau khi bed đã đạt nhiệt và sau soak. Wrapper QGL nội bộ đã có `G28 Z` ở cuối, nên `PRINT_START` không cần lặp lại `G28 Z` riêng.

## Prime line

Logic prime line hiện tại:

- Chỉ prime các tool được dùng trong bản in.
- Tool in đầu tiên được prime sau cùng.
- Mỗi tool được nâng lên nhiệt in khi đến lượt prime.
- Sau khi prime xong, tool được đưa về nhiệt chờ để giảm ooze/stringing.
- Đường prime nằm khu vực trước-giữa bàn, theo hướng X, gồm nhiều đường song song để tăng tổng chiều dài extrusion.

Điểm cần theo dõi tiếp: nếu vẫn còn thiếu nhựa lúc bắt đầu in, cần tăng tổng chiều dài prime hoặc lượng extrusion, nhưng phải giữ dưới giới hạn `max_extrude_cross_section`.

## Input shaper khi đổi tool

Đã kiểm tra thông báo `shaper_type_x/y`. Nguồn thông báo là lệnh Klipper `SET_INPUT_SHAPER`, không phải lỗi của Klippain Shake&Tune.

Đã thêm logic nhớ trạng thái input shaper đang active để tránh gọi lại cùng một bộ shaper liên tục. Khi đổi sang tool có shaper khác, Klipper vẫn sẽ hiện thông báo. Điều này là bình thường và cần thiết vì mỗi tool có bộ shaper riêng.

## Camera và Crowsnest

Đã chỉnh `crowsnest.conf` để camera hướng tới 15-20 FPS thay vì thực tế chỉ 2-10 FPS:

```ini
resolution: 800x600
max_fps: 20
v4l2ctl: --set-fmt-video=width=800,height=600,pixelformat=MJPG --set-parm=20
```

Sau khi cập nhật trên máy Voron cần restart Crowsnest:

```bash
sudo systemctl restart crowsnest
tail -n 80 ~/printer_data/logs/crowsnest.log
```

Nếu vẫn FPS thấp, cần kiểm tra camera có hỗ trợ MJPG 800x600@20 hay không:

```bash
v4l2-ctl --list-formats-ext -d /dev/v4l/by-id/usb-BC-250612-ZW_MF500_camera_01.00.00-video-index0
```

## Cập nhật firmware Cartographer

Đã tra cứu tài liệu chính thức Cartographer. Máy hiện tại khai báo Cartographer trên CAN:

```ini
[mcu cartographer]
canbus_uuid: da13d909ce34
```

Hướng cập nhật an toàn:

```bash
cd ~
git clone https://github.com/Cartographer3D/cartographer_firmware.git
git clone https://github.com/Arksine/katapult.git
cd ~/cartographer_firmware
./fw_update.sh
```

Trong script chọn CAN interface `can0`, dùng bản Cartographer V3, và đối chiếu UUID `da13d909ce34` trước khi flash.

## Trạng thái Git

Đã commit và push các thay đổi chính:

- `f217551 Update Cartographer calibration and T1 Z offset`
- `e0f205f Tune Crowsnest camera FPS target`

Một số backup local được tạo trước khi sửa cấu hình, không đưa lên GitHub:

- `extras/backups/pre-apply-calibrated-printer-cfg-20260613-152828/`
- `extras/backups/pre-crowsnest-fps-20260613-161426/`
- `extras/backups/pre-t1-z-offset-20260613-152432/`
- `extras/backups/pre-stable-16h-printer-cfg-20260614-1702/`

## Việc cần làm tiếp

1. Theo dõi thêm 1-2 bản in lớn với bộ `z_compensations` mới đã cập nhật vào repo.
2. In lại patch first layer trái/giữa/phải sau khi axis twist ổn định.
3. Kiểm tra FPS thực tế sau khi restart Crowsnest.
4. Nếu first layer vẫn lệch theo tool, tách tiếp thành vấn đề tool Z offset; nếu lệch theo vị trí X/Y, ưu tiên xử lý gantry/Cartographer/bed mesh.

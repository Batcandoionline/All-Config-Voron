# Nhật ký — 2026-07-28

## 1. Điều tra ToolCrash T0 của bản in 2h24m

### Mục tiêu
Phân tích bản in `voron_design_cube_v8-v1(1)_PETG_2h24m.gcode` bị Klipper shutdown, xác định đúng vị trí G-code, đối chiếu ảnh prime tower, hai preset OrcaSlicer và tài liệu nguồn chính thức.

### Dữ liệu
- `extras/logs/klippy.log`
- `extras/logs/moonraker.log`
- `extras/gcode/voron_design_cube_v8-v1(1)_PETG_2h24m.gcode`
- `extras/Orcasilcer setting/MulticolorPETG.json`
- `extras/Orcasilcer setting/Printersetting.json`
- Ảnh prime tower do người dùng cung cấp sau sự cố.

### Timeline
- Moonraker bắt đầu đúng file lúc `2026-07-28 19:40:48`.
- Klipper shutdown lúc `20:02:28`, sau khoảng 21 phút 39 giây.
- Thông báo trực tiếp là `tool_crash detected tool T0`; đây không phải thông báo watchdog.
- Klipper thoát virtual SD ở `position 348083`.
- Trước sự cố, G-code đã tới `toolchange #22`, chọn tool 23 lần và chọn T0 thành công 8 lần.

### Vị trí lỗi chính xác
- `sd_pos=348083` trùng chính xác byte đầu dòng 11987 của G-code.
- G-code đang ở layer vật thể `Z=1.64 mm`, prime-tower framework `layer #8`.
- Toolchange #22 vừa đổi từ T4 sang T0.
- Trạng thái shutdown ghi vị trí cuối `X=156.076, Y=283.195, Z=1.64`.
- Dòng cuối đã thực hiện là một đường đùn của `TYPE:Prime tower`; dòng kế tiếp tại byte 348083 là `G1 E0.0000`.
- Vì vậy T0 đã rời dock, được chọn thành công, trở về tower, purge/wipe xong và đang in biên/framework của tower. Lỗi không xảy ra trong dock.

### Loại trừ lỗi truyền thông
- Ngay trước shutdown, `mcu`, `EBB0` đến `EBB4` đều có `bus_state=active`.
- Tất cả `rx_error=0`, `tx_error=0`, `tx_retries=0`.
- Các dòng `MCU ... shutdown: Command request` xuất hiện sau khi plugin gọi Klipper shutdown; chúng là hậu quả, không phải nguyên nhân đầu tiên.
- Các lỗi Moonraker `machine.device_power.on/off: Method not found` đã lặp lại trước đó và không trùng cơ chế ToolCrash.

### Bằng chứng nhiệt và preheat
- File được tạo bằng OrcaSlicer 2.4.2.
- Preset và footer G-code đều ghi:
  - `preheat_time = 20`
  - `machine_tool_change_time = 0`
  - `ooze_prevention = 1`
  - `idle_temperature = 150°C`
  - `standby_temperature_delta = -80°C`
  - nhiệt T0 `225°C`, các tool còn lại `220°C`
  - toolchange retract `5 mm`
- T0 nhận target 225°C khoảng `Stats 16190.5`, khi T1 vẫn đang nhả và trước khi T4 được chọn.
- T0 tăng từ khoảng 162.6°C lên vùng 223–225°C trong khoảng 16 giây.
- T4 chỉ được xác nhận selected khoảng `Stats 16211.5`.
- T0 được xác nhận selected khoảng `Stats 16251.6`.
- Như vậy T0 bắt đầu được nung khoảng 61–62 giây trước khi được chọn, và nằm ở khoảng 225°C trong dock khoảng 45–46 giây sau khi đã đạt nhiệt. Con số thực tế dài hơn nhiều so với `preheat_time=20`.
- G-code chứng minh lệnh `M104 S225 T0 ; preheat T0 time: 20s` được đặt ngay trong toolchange #21 trước lệnh `T4`, dù T0 chỉ được dùng ở toolchange #22.

### Thời gian đổi tool thực tế
Phân tích 26 chu kỳ của bản in:
- Toàn bộ chu kỳ: 14–26 giây, trung vị 15 giây, trung bình 15.6 giây.
- Sau các chu kỳ đầu: phần lớn ổn định ở 14–16 giây.
- Giá trị đại diện phù hợp cho OrcaSlicer là `Tool change time = 15 s`, thay vì 0 s.

### Đối chiếu ảnh tower
- Brim của tower còn bám chắc; không có bằng chứng tower bong khỏi bàn.
- Framework/rib vẫn đứng nhưng có nhiều vòng PETG rơi tự do ở mép, sợi kéo chéo và nhiều cục nhựa nằm trên đường quét.
- Có một búi nhiều màu nhô cao ở vùng giữa/phía trên tower và nhiều blob nhỏ ở các vùng purge khác.
- Hình thái này phù hợp với nozzle nóng rỉ nhựa trong dock/hành trình, sau đó mang sợi PETG trở lại tower. Blob tích lũy trở thành chướng ngại ở các lớp tiếp theo.

### Cơ chế shutdown
Mã nguồn `cekim-git/tool_crash` đăng ký edge callback cho tất cả `detection_pin`. Khi detection đang bật và toolchanger không ở trạng thái `CHANGING`/`INITIALIZING`, một cạnh pin sẽ tạo thông báo `tool_crash detected <active tool>` rồi gọi shutdown ngay. Nhánh watchdog có chuỗi thông báo khác: `tool_crash: watchdog detected crash of ...`.

Thông báo hiện tại do nhánh edge trực tiếp. Tên T0 trong thông báo là active tool ở thời điểm cạnh xuất hiện; nó không chứng minh tuyệt đối PB6 nào đã tạo cạnh vì plugin đăng ký chung callback cho mọi detection pin.

### Kết luận nguyên nhân
1. **Nguyên nhân trực tiếp đã xác nhận:** một detection-pin edge xuất hiện khi T0 đang active và đang in framework của prime tower.
2. **Nguyên nhân vật lý có xác suất cao nhất:** T0 hoặc tower bị tác động khi nozzle đi qua vùng nhựa nhô/blob. T0 được nung quá sớm, rỉ PETG trong dock và mang nhựa trở lại tower; ảnh cho thấy hậu quả tích lũy rõ ràng.
3. **Yếu tố phụ cần loại trừ:** preload/latch/magnet của T0 hoặc PB6/connector/umbilical T0 ở trạng thái biên. Nhiều lần trước cũng lỗi khi T0 active nên phải kiểm tra riêng T0, dù tower/blob vẫn là tác nhân kích hoạt có trọng số cao.
4. **Không có bằng chứng:** lỗi CAN, Moonraker, Cartographer, mất nhiệt hoặc tower bong bàn.

### Khuyến nghị sau xác nhận thực tế của người dùng
Người dùng xác nhận `preheat_time=2 s` làm shuttle phải chờ nhiệt dưới 10 giây tại tool kế tiếp, nên đã thử 20 giây để loại thời gian chờ.

Không quay lại 2 giây ngay. Bài thử kế tiếp nên thay đổi một biến thời gian nền:

1. Giữ `Preheat time = 20 s`.
2. Đặt `Tool change time = 15 s` trong Printer Settings → Multimaterial → Advanced.
3. Slice lại và lưu đúng preset.
4. Trước khi in, kiểm tra footer phải có:
   - `preheat_time = 20`
   - `machine_tool_change_time = 15`
5. Kiểm tra một chuỗi T1 → T4 → T0 trong G-code: `M104 ... T0` không được nằm trước lệnh `T4` như file lỗi này; nó cần nằm gần lượt T0 hơn.
6. Chạy bài tower ngắn, đo:
   - thời gian từ T0 bắt đầu tăng target tới `Selected tool 0`;
   - thời gian T0 đã đạt 225°C nhưng vẫn còn nằm trong dock;
   - thời gian đứng chờ M109 tại dock.
7. Mục tiêu: M109 chờ không quá 1–2 giây và thời gian tool nằm đủ nhiệt trong dock không quá khoảng 5 giây.

Nếu sau khi đặt `Tool change time=15 s`, M109 vẫn chờ:
- tăng `Preheat time` từng 2 giây: 20 → 22 → 24;
- không nhảy thẳng lên 40 giây;
- dừng tăng khi không còn chờ hoặc khi quan sát thấy nozzle bắt đầu rỉ đáng kể.

Nếu preheat được đặt đúng thời điểm nhưng T0 vẫn ToolCrash:
- dry-toolchange T0 nhiều vòng, không đùn nhựa;
- cho T0 chạy hành trình dock ↔ tower không đùn;
- theo dõi detection state trong lúc rung nhẹ umbilical;
- kiểm tra preload/latch/magnet, switch PB6 và connector riêng của EBB0.

Không vô hiệu hóa crash detection để tiếp tục in.

### Thiết lập tower giữ nguyên trong bài thử đầu
- `prime_tower_enable_framework = 1`
- `prime_tower_infill_gap = 100%`
- `wipe_tower_bridging = 5 mm`
- `wipe_tower_max_purge_speed = 60 mm/s`
- `retract_length_toolchange = 5 mm`

Chỉ sau khi sửa timing preheat mà tower vẫn sinh blob mới giảm `wipe_tower_max_purge_speed` xuống 40–45 mm/s hoặc thay đổi hình học tower. Không tăng mạnh toolchange retract vì có rủi ro heat creep/kẹt filament.

### Nguồn kiểm tra chéo
- OrcaSlicer Ooze prevention: https://github.com/OrcaSlicer/OrcaSlicer/wiki/multimaterial_settings_ooze_prevention
- OrcaSlicer Prime tower: https://github.com/SoftFever/OrcaSlicer/wiki/multimaterial_settings_prime_tower
- Tool Crash plugin/source: https://github.com/cekim-git/tool_crash
- Klipper CAN status reference: https://www.klipper3d.org/Status_Reference.html#canbus_stats

### Thay đổi cấu hình
Không có. Chỉ đọc log, G-code, preset JSON, ảnh và tài liệu; ghi nhật ký điều tra.

### Vấn đề còn lại
Cần slice và chạy bài ngắn với `preheat_time=20`, `machine_tool_change_time=15`, sau đó kiểm tra lại vị trí M104 và log nhiệt. Nếu timing đã đúng mà vẫn có edge ToolCrash, chuyển trọng tâm sang cơ khí/cảm biến T0.

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

## Khuyến nghị giảm nhựa tích tụ trên prime tower

### Phát hiện bổ sung trong G-code
- Dù `Printersetting.json` ghi `enable_filament_ramming = 0`, footer G-code thực tế ghi `filament_multitool_ramming = 1,1,1,1,1`.
- Mỗi filament đang dùng `filament_multitool_ramming_volume = 10 mm³` và flow `10 mm³/s`.
- Ở toolchange #22, tool đi ra đùn `E3.0639 + E1.0936 = 4.1575 mm` filament trước khi retract 5 mm, tương đương xấp xỉ 10 mm³.
- Với 22 toolchange đã xảy ra trước crash, ramming có thể chủ động đặt khoảng 220 mm³ nhựa lên tower, chưa tính đường wipe, framework và nhựa rỉ ngoài kế hoạch.

### Thứ tự thử được khuyến nghị
1. Sửa timing trước: giữ `preheat_time = 20 s`, đặt `machine_tool_change_time = 15 s`.
2. Trong từng Filament preset của cả 5 tool, giảm **Multi-tool ramming volume** từ `10` xuống `5 mm³`; giữ flow ban đầu hoặc giảm nhẹ xuống `8 mm³/s`.
3. Slice lại và xác nhận footer phải đổi thành volume `5,5,5,5,5`. Nếu muốn thử tắt hoàn toàn, footer phải là `filament_multitool_ramming = 0,0,0,0,0`; không chỉ dựa vào checkbox trong Printer Settings.
4. Giảm `Maximum wipe tower print speed` từ `60` xuống `45 mm/s`. Việc này không làm giảm thể tích thiết kế nhiều, nhưng giảm khả năng kéo bật đường PETG, quấn sợi và lực va vào blob.
5. Giữ `prime_tower_infill_gap = 100%`, bridging `5 mm`, extra flow `100%`, width `40 mm` trong bài thử đầu để không thay đổi quá nhiều biến cùng lúc.
6. Nếu tower vẫn có cục nhô nhưng không còn nhựa rỉ từ dock, thử tắt ramming cho cả 5 filament. Chỉ tăng lại 2–3 mm³ nếu đầu mới bắt đầu in bị thiếu nhựa hoặc áp suất không ổn định.

### Không khuyến nghị ở bước đầu
- Không tăng toolchange retract vượt 5 mm khi chưa kiểm tra heatbreak.
- Không tăng infill gap để tiết kiệm nhựa: khoảng đỡ thưa hơn có thể làm PETG võng và tạo bẫy blob.
- Không giảm extra flow hoặc purge tùy tiện trước khi tách được phần ramming và phần ooze.
- Không vô hiệu hóa ToolCrash.

### Nguồn kiểm tra chéo bổ sung
- OrcaSlicer Material Multimaterial: https://github.com/OrcaSlicer/OrcaSlicer/wiki/material_multimaterial
- OrcaSlicer Prime Tower: https://github.com/SoftFever/OrcaSlicer/wiki/multimaterial_settings_prime_tower

## Đính chính sau khi kiểm tra file slice 5h02

### File
- `extras/gcode/voron_design_cube_v8-v1(1)_PETG_5h2m.gcode`
- OrcaSlicer 2.4.2, tạo lúc `2026-07-28 20:45:26`.

### Vì sao ước tính tăng lên 5h02
- File cũ: `2h 24m 19s`.
- File mới: `5h 1m 59s`.
- Cả hai có đúng 520 block `CP TOOLCHANGE START`; mô hình và số lượt đổi tool không tăng.
- File mới đặt `machine_tool_change_time = 15`.
- Orca cộng `520 × 15 s = 7,800 s = 2h 10m` vào thống kê.
- Chênh lệch tổng giữa hai file là `2h 37m 40s`; 27m40s còn lại là chênh lệch ròng từ các thay đổi khác như tốc độ tower 60 → 45 mm/s, đường chạy/vị trí tower và ramming 10 → 5 mm³.
- Tài liệu Orca ghi `machine_tool_change_time` là thời gian dùng cho thống kê. Nó không chèn `G4 S15` hay làm shuttle cố ý đứng thêm 15 giây.
- Giá trị 15 giây làm dự báo gần thời gian vật lý hơn vì macro đổi tool thực tế vẫn tốn khoảng 15 giây, bất kể footer đặt 0 hay 15.

### Trường hợp T2 → T1 đứng chờ nhiệt
- Đây là lần toolchange thực đầu tiên, tại dòng 502.
- T2 được hạ về 150°C ở dòng 519.
- T1 được chọn tại dòng 529.
- Chỉ sau đó mới có `M109 S230 T1` tại dòng 531.
- Không có `M104 ... T1` trước toolchange này, nên máy bắt buộc lấy T1 xuống rồi mới chờ tăng từ standby lên nhiệt in.
- Phân tích toàn bộ 520 block cho thấy chỉ block đầu T2 → T1 thiếu preheat; block 520 là block kết thúc không chọn tool mới. Mọi toolchange thực còn lại đều có lệnh preheat.
- File 2h24 cũ cũng thiếu M104 cho đúng lần T2 → T1 đầu tiên; do đó hiện tượng này không phải do đặt Tool change time 15 giây.
- Macro M104/M109 hiện tại hỗ trợ đúng tham số `T`, nên không có bằng chứng lỗi chọn heater T1.

### Đính chính khuyến nghị
- Không dùng `machine_tool_change_time` để điều chỉnh thời điểm preheat. Giữ 15 nếu muốn thời gian dự kiến phản ánh thời gian đổi tool thật; đặt 0 chỉ làm số dự kiến ngắn hơn khoảng 2h10, không làm chuyển động thực nhanh hơn.
- `preheat_time = 20 s` vẫn là tham số chính của Orca cho việc chèn M104 trước toolchange.
- Với riêng file này, có thể chấp nhận một lần T1 chờ ở toolchange đầu; các lần sau có preheat.
- Nếu muốn loại bỏ cả lần chờ đầu, cần một lệnh one-shot `M104 S230 T1` trước toolchange #1 hoặc cơ chế tự động nhận diện tool thứ hai. Không nên giữ tất cả tool ở nhiệt in từ lúc PRINT_START vì sẽ làm tăng ooze.

### Nguồn
- Orca Advanced Multi-Material Settings: https://www.orcaslicer.com/wiki/printer_settings/multimaterial/printer_multimaterial_advanced
- Orca Ooze Prevention: https://www.orcaslicer.com/wiki/print_settings/multimaterial/multimaterial_settings_ooze_prevention.html
- Orca 2.4 release notes: https://github.com/OrcaSlicer/OrcaSlicer/releases

## Bổ sung: T0 rỉ nhựa do áp suất dư và lặp điểm vào tower

### Quan sát thực tế
- Mỗi lần T0 được lấy khỏi dock và đi xuống vùng in, nozzle kéo theo một sợi PETG dài gần 5 mm.
- Không thể giải quyết bằng cách hạ nhiệt in vì mẫu bị tách lớp.
- T0 luôn tiếp cận cùng điểm trên prime tower, nên sợi rỉ được dồn vào một vị trí và tạo blob cao dần.

### Bằng chứng trong file 5h02
- T0 được chọn 150 lần.
- G-code cũng cooldown/cất T0 150 lần.
- Trước mỗi lần cất T0, Orca thực hiện multi-tool ramming 5 mm³:
  - ví dụ dòng 3399: đường ramming có `E2.0788`, tương đương khoảng 5 mm³ filament 1.75 mm;
  - sau đó mới `G1 E-5 F1800` và `M104 S150 T0`.
- Như vậy riêng T0 có thể đặt chủ động khoảng `150 × 5 = 750 mm³` nhựa lên tower trong toàn bộ file, chưa tính các đường wipe/framework và nhựa rỉ ngoài kế hoạch.
- Khi T0 được lấy lại, G-code chỉ unretract 5 mm sau khi đã trở về điểm đầu tower. Sợi đã rỉ trong hành trình vì thế được kéo tới đúng điểm nhập tower trước khi đường wipe bắt đầu.

### Cơ chế phù hợp nhất
- PETG nóng và cột nhựa trong melt zone còn đàn hồi/nén sau đường đùn cuối.
- Dừng stepper không làm áp suất và dòng nhớt giảm về 0 ngay; nhựa vẫn có thể chảy do pressure decay, giãn nở nhiệt và trọng lực.
- Ramming ngay trước retract tạo thêm một xung đùn cuối. Retract 5 mm đã lớn nhưng không lấy hết phần nhựa nóng nằm dưới heatbreak/nozzle.
- Hạ nhiệt in không phù hợp vì đã quan sát thấy mất liên kết lớp.

### Thứ tự thử nhắm riêng T0
1. Tắt `Enable ramming for multi-tool setups` chỉ trong filament preset gắn T0. Slice lại và xác nhận footer là `filament_multitool_ramming = 0,1,1,1,1` theo thứ tự T0–T4.
2. Giữ toolchange retract T0 ở 5 mm trong lần thử đầu.
3. Nếu T0 vẫn kéo sợi dài, thử retract riêng T0 `5 → 5.5 → 6 mm`, mỗi lần tăng 0.5 mm; không tăng đồng loạt các tool và không vượt xa 6 mm khi chưa kiểm tra nguy cơ kéo nhựa nóng lên heatbreak.
4. Sau khi loại ảnh hưởng ramming, thử giảm `preheat_time` từ 20 xuống khoảng 16 giây. Dữ liệu trước cho thấy T0 cần khoảng 16–17 giây để đi từ 150°C lên 225°C; mục tiêu là T0 vừa đạt nhiệt lúc được dùng, không nằm đủ nhiệt trong dock nhiều giây.
5. Nếu vẫn còn sợi do PETG chảy tự nhiên, giải pháp tin cậy là một cú flick/wipe cơ khí sau pickup và trước khi vào tower. Máy có brush ở X320/Y-8, nhưng macro `CLEAN_NOZZLE` hiện tại là chu trình đầy đủ, hạ xuống Z=2 và không phù hợp để gọi trực tiếp 150 lần giữa bản in. Cần một macro `TOOLCHANGE_FLICK` ngắn, có nâng Z an toàn và khôi phục vị trí, hoặc lắp wiper nhỏ ngay trên đường rời dock.

### Tower
- Đổi rotation chỉ chuyển blob sang góc khác; không loại nguyên nhân vì T0 vẫn vào lặp một điểm.
- `prime_tower_skip_points=1` không nên được xem là giải pháp chắc chắn: Orca từng có lỗi skip-points không hoạt động đúng với regular printer profiles.
- Giữ `Tool change on wipe tower` để tránh chuyển sợi rỉ sang bề mặt mẫu.
- Không gọi trực tiếp `CLEAN_NOZZLE` hiện tại trong mỗi toolchange vì đường đi và Z=2 có thể va mẫu/tower ở các lớp cao.

### Nguồn bổ sung
- Orca Material Multimaterial / multi-tool ramming: https://github.com/OrcaSlicer/OrcaSlicer/wiki/material_multimaterial
- Orca prime-tower skip-points regression: https://github.com/OrcaSlicer/OrcaSlicer/issues/12684

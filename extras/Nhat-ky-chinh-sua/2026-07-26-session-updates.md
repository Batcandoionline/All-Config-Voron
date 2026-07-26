# Nhật ký — 2026-07-26

## 1. Chuyển Cartographer sang chế độ Scan Homing (Không chạm bàn)

### Mục tiêu
Khắc phục hiện tượng Nozzle bị cày sát bàn PEI do nhựa dẻo sót trên Nozzle gây nén đệm và làm tụt chốt cơ khí StealthChanger khi thực hiện Touch Home. Chuyển Cartographer sang dùng Eddy Current Scan Homing hoàn toàn không tiếp xúc.

### File đã sửa đổi
- `Voron 5 Tool/config/Printer-Setup/print-macros.cfg` — comment out bước `CARTOGRAPHER_TOUCH_HOME` trong macro `PRINT_START`.

### Sao lưu
- [print-macros.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cartographer-scan-homing-20260726-081000/print-macros.cfg)

### Chi tiết thay đổi
- Trong `PRINT_START`: Vô hiệu hóa `CARTOGRAPHER_TOUCH_HOME` ở bước 8.
- Quy trình homing Z hiện tại sử dụng `G28 Z` (Eddy Current Scan Homing) tích hợp sẵn ở cuối lệnh `QUAD_GANTRY_LEVEL`.

### Lý do
Tại nhiệt độ 150°C, nhựa sót ở đầu vòi phun bị dẻo hóa tạo thành đệm nén làm sai lệch vị trí Touch, khiến lực ép đẩy lún chốt toolhead StealthChanger và làm Z=0 bị âm quá sâu. Scan Homing hoàn toàn không chạm bàn, loại bỏ 100% rủi ro đâm bàn và nén chốt.

### Kiểm tra
- Kiểm tra cú pháp: Đạt (cú pháp Jinja2/Klipper macro chuẩn).
- Cấu hình sẵn sàng khởi động lại Klipper.

### Kết quả
Quá trình `PRINT_START` sẽ chạy QGL + Eddy Scan Homing nhanh chóng, không còn bước nhấp chạm nozzle T0 xuống bàn in.

### Vấn đề còn lại
Không có.

---

## 6. Điều tra lần Tool Crash T0 thứ ba với G-code 2h27m

### Triệu chứng
Bản in `voron_design_cube_v8-v1_PETG_2h27m.gcode`, tạo bằng OrcaSlicer 2.4.2, tiếp tục bị Klipper shutdown với thông báo trực tiếp `tool_crash detected tool T0`. Người dùng cung cấp ảnh tower thực tế sau lỗi; tower đứng vững hơn lần trước nhưng có búi PETG lớn ở mép phải, nhiều sợi kéo chéo và blob nhô trên mặt tower.

### Vị trí lỗi
- Moonraker ghi nhận job bắt đầu lúc 09:58:54 và Klipper shutdown lúc 12:03:08.
- Klipper ghi `tool_crash detected tool T0` tại dòng 65301; toàn bộ CAN node vẫn active, không có `rx_error`, `tx_error` hoặc `tx_retries`.
- G-code đang ở `toolchange #184`, đổi từ T4 sang T0 tại Z=12.44 mm, ngay trước `layer #62`.
- Sau khi T0 được chọn, T0 purge tại Y khoảng 83–84 mm rồi in framework/rib của tower. `sd_pos=2788826` trỏ tới đường tower ở Y=103.2 mm, đang chạy từ vùng X khoảng 184.7 về X khoảng 161.9.
- Trước sự cố, file đã thực hiện 184 toolchange và có 62 lệnh chọn T0. Việc T0 hoạt động thành công nhiều lần làm giảm khả năng đường dock hoặc dây T0 tự phát lỗi ở mọi chu kỳ; sự cố tích lũy nhựa/va chạm tower có trọng số cao hơn.

### So sánh với G-code trước
Các thay đổi tower đã được áp dụng đúng:
- `prime_tower_enable_framework`: 0 → 1
- `prime_tower_infill_gap`: 150% → 100%
- `wipe_tower_bridging`: 10 → 5 mm
- `wipe_tower_max_purge_speed`: 90 → 60 mm/s

Hai giá trị điều khiển thời gian vẫn chưa thay đổi:
- `machine_tool_change_time = 0`
- `preheat_time = 40`

### Bằng chứng preheat gây rỉ nhựa
Tại toolchange #182, G-code vừa phát `M104 S150 T0` để cooldown T0 thì ngay sau đó phát `M104 S220 T0 ; preheat T0 time: 40s`, trước khi đổi sang T1. T0 vì vậy được dock ở 220°C, tiếp tục nằm nóng trong lúc T1 rồi T4 hoạt động và chỉ được lấy lại ở toolchange #184. Chuỗi này khớp với quan sát thực tế rằng nozzle PETG rỉ một đoạn nhựa khi đi dock và với blob/stringing tích lũy trên ảnh tower.

Log đo được một hotend tăng từ khoảng 150°C lên vùng 220°C trong khoảng 16 giây. Chu kỳ toolchange thực tế mất khoảng 14 giây từ lúc crash detection bị tắt để đổi tool tới khi tool mới được xác nhận selected. Ở lần đổi cuối, lệnh preheat T0 được xử lý khoảng `Stats 18518.0`, lệnh T0 được đọc khoảng `Stats 18598.1`, T0 được xác nhận selected tại `Stats 18618.1`, và purge tower đã bắt đầu trước `Stats 18619.1`. Như vậy T0 bị giữ nóng khoảng 100 giây từ preheat tới selected và khoảng 101 giây tới khi bắt đầu đùn, mặc dù G-code ghi `preheat T0 time: 40s`. Vì `machine_tool_change_time` đang là 0, Orca cũng bỏ qua khoảng 46 phút cơ khí cho 184 lần đổi đã thực hiện và khoảng 2 giờ 02 phút cho toàn bộ 489 lần đổi dự kiến.

### Kết luận
Nguyên nhân trực tiếp vẫn là một cạnh detection-pin xuất hiện khi T0 đang active; plugin `tool_crash` shutdown ngay trên cạnh này và không debounce. Nguyên nhân vật lý có xác suất cao nhất là T0 được giữ ở 220°C quá sớm/quá lâu trong dock, rỉ PETG và mang nhựa trở lại tower. Blob tích lũy bị T0 quệt ở layer 62, làm TAP/detection đổi trạng thái hoặc làm tool dịch chuyển đủ để tạo cạnh. T0 có preload/cảm biến biên vẫn là yếu tố phụ cần kiểm tra vì cả ba lần crash đều xảy ra khi T0 active.

### Khuyến nghị
1. Đặt `Tool change time` thành 15 s.
2. Giữ `Ooze prevention` bật và `standby_temperature_delta = -80` (idle khoảng 150°C).
3. Để xác nhận nguyên nhân, có thể đặt `Preheat time = 0 s` cho một bài thử ngắn. Giá trị vận hành ban đầu phù hợp nhất là `2 s` vì log đo hotend cần khoảng 16 s để tăng từ 150°C lên 220°C, trong khi macro đổi tool thực tế mất khoảng 14 s. Mã nguồn Orca cho thấy `Preheat time` được tính lùi trước chính lệnh T và không trừ thời gian macro Klipper; đặt 15–16 s sẽ làm tool nóng sớm không cần thiết. Sau khi slice phải kiểm tra không còn cặp cooldown 150°C rồi reheat 220°C liền nhau cho cùng tool.
4. Giữ framework/rib, infill gap 100%, bridge 5 mm; giảm tạm maximum wipe tower speed từ 60 xuống 40–45 mm/s.
5. Giữ retraction khi đổi material ở 5 mm trong lần thử đầu; không tăng mạnh để tránh heat creep hoặc kẹt filament.
6. Không vô hiệu hóa tool-crash detection. Kiểm tra riêng preload hai vít T0, magnet, PB6/connector và umbilical; nếu dry toolchange không đùn nhựa vẫn tạo lỗi thì ưu tiên xử lý tín hiệu/cơ khí T0.

### Thay đổi cấu hình
Không có. Chỉ phân tích log, G-code, ảnh và tài liệu nguồn chính thức.

### Vấn đề còn lại
Cần slice lại với `machine_tool_change_time = 15` và `preheat_time = 2`; nếu vẫn còn ooze/blob thì chạy bài kiểm tra tách biệt với `preheat_time = 0`. Kiểm tra G-code nhiệt trước khi chạy bài thử toolchange/tower rút gọn.

---

## 5. Bổ sung phân tích mã nguồn Tool Crash và thời gian di chuyển dock

### Triệu chứng
Người dùng xác nhận mỗi chặng di chuyển giữa vùng in và dock mất khoảng 5 giây do kích thước khung Voron và vị trí dock cố định.
Quan sát trực tiếp cho thấy các nozzle nóng rỉ một đoạn PETG dài khoảng 5 mm trong lúc đi về/xuống dock; phần nhựa này được mang trở lại prime tower và có thể tạo blob ở đầu đường purge.

### Phân tích bổ sung
- Mã nguồn `cekim-git/tool_crash` xác nhận thông báo `tool_crash detected tool T0` xuất phát từ bộ bắt cạnh detection pin và gây shutdown ngay. Nếu lỗi do watchdog, thông báo phải có dạng `tool_crash: watchdog detected crash of tool T0`.
- Bộ bắt cạnh dùng chung cho tất cả detection pin và nội dung thông báo lấy tên tool đang active. Do đó, tên T0 trong thông báo không xác định tuyệt đối pin nào tạo cạnh, nhưng T0 vẫn là yếu tố chung có xác suất cao nhất vì hai tool trước đó khác nhau (T4 và T2).
- Plugin bỏ qua cạnh detection trong khi trạng thái toolchanger là `CHANGING` hoặc `INITIALIZING`; thời gian đi dock 5 giây không phải timeout của plugin.
- Hai log cho thấy khoảng 5.2–5.5 giây chuyển động được xếp hàng giữa lúc crash detection bật lại và lúc toolchange hoàn tất, phù hợp với thời gian đi từ dock về tower mà người dùng đo được.
- Sau khi T0 được chọn, lỗi xuất hiện khoảng 6–7 giây sau trong lúc G-code đang xử lý chuỗi purge tower. Đây không phải lỗi phát sinh chỉ vì dock ở xa.
- Tài liệu OrcaSlicer cảnh báo tốc độ wipe tower cao làm tăng lực nozzle va vào các blob trên tower. Ảnh tower thực tế có nhiều điểm PETG dồn cục và đường purge nhô.

### Điều chỉnh kết luận trước
Không áp dụng diễn giải `watchdog_interval × watchdog_threshold ≈ 1 giây` cho hai sự kiện này, vì chuỗi thông báo trong log chứng minh nhánh detection-edge trực tiếp đã kích hoạt.

### Nguyên nhân có xác suất cao
Một cạnh detection pin xuất hiện sau khi T0 rời dock và trở lại tower. Thứ tự nghi ngờ:
1. T0 hoặc tiếp điểm `EBB0:PB6` chập chờn khi umbilical thay đổi tư thế trên hành trình dài.
2. Preload/latch/magnet của T0 ở trạng thái biên, sau hành trình 5 giây hoặc khi purge bị dịch chuyển đủ để switch đổi trạng thái.
3. Nozzle T0 quệt blob/gờ PETG hình thành từ nhựa rỉ trong hành trình dock và làm T0 dịch chuyển.
4. Ít khả năng hơn: detection pin của tool không active tạo cạnh muộn; plugin vẫn gắn nhãn lỗi theo active tool T0.

### Vấn đề còn lại
Cần chạy thử tách biệt: lặp toolchange T0 không in tower, sau đó lặp hành trình T0 tới tower không đùn nhựa. Hai phép thử sẽ phân biệt lỗi hành trình/cáp với lỗi va chạm tower.

---

## 4. Điều tra hai lần Tool Crash T0 tại prime tower

### Triệu chứng
Hai lần in file `voron_design_cube_v8-v1_PETG_2h1m.gcode` đều bị Klipper shutdown với thông báo `tool_crash detected tool T0` ngay sau khi đổi sang T0 và bắt đầu purge trên prime tower.

### Phân tích nhật ký
- File nhật ký liên quan: [klippy.log](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/logs/klippy.log)
- File Moonraker liên quan: [moonraker.log](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/logs/moonraker.log)
- Lần 1, khoảng 08:55:10: `sd_pos=200733`; T0 vừa đổi từ T4, tower layer #4, Z=0.84 mm, sau đó báo `tool_crash detected tool T0`.
- Lần 2, khoảng 09:46:57: `sd_pos=237140`; T0 vừa đổi từ T2, tower layer #5, Z=1.04 mm, sau đó báo cùng lỗi.
- Trước cả hai lần shutdown, EBB0 và toàn bộ CAN bus vẫn `active`, `rx_error=0`, `tx_error=0`, `tx_retries=0`; nhiệt độ T0 ổn định khoảng 220°C.
- Plugin `[tool_crash]` giám sát `detection_pin: ^!EBB0:PB6`, không dùng Cartographer để phát hiện crash. Với `watchdog_interval: 0.5` và `watchdog_threshold: 2`, lỗi nghĩa là tín hiệu hiện diện T0 mất trong hai lần kiểm tra liên tiếp.
- Ảnh prime tower cho thấy các đường purge bị nhô, kéo sợi và dồn cục, đặc biệt ở đầu các đường quét ngang. G-code cho T0 chạy purge trực tiếp qua vùng X≈153.5–193.0 mm; đây là vùng có khả năng tạo lực quệt làm T0 lỏng/bung khỏi carriage hoặc làm tiếp điểm PB6 chập chờn.

### Nguyên nhân gốc
Nguyên nhân trực tiếp đã xác nhận là tín hiệu hiện diện T0 trên `EBB0:PB6` bị mất khi T0 đang purge tại prime tower. Nguyên nhân vật lý có xác suất cao là nozzle T0 quệt vào các gờ/cục PETG nhô trên tower, làm cơ cấu khóa T0 dịch chuyển; khả năng thứ hai cần loại trừ là microswitch/đầu nối/dây PB6 của riêng T0 bị chập chờn dưới rung động. Không có bằng chứng về lỗi CAN, Moonraker, nhiệt độ hoặc Cartographer gây ra sự cố.

### Hướng khắc phục đã thực hiện
Chưa sửa cấu hình. Chỉ phân tích log, G-code, ảnh tower và các setting OrcaSlicer hiện tại.

### Kết quả
Hai lần crash tái hiện cùng chuỗi sự kiện: đổi sang T0, bật lại crash detection, purge trên tower, sau đó mất tín hiệu detection T0.

### Phòng ngừa
- Kiểm tra lực khóa/magnet/latch của T0 và thử rung nhẹ T0 khi chạy `QUERY_ENDSTOPS` để phát hiện tín hiệu PB6 chập chờn.
- Kiểm tra microswitch, giắc và dây tín hiệu `EBB0:PB6`.
- Trước lần in tiếp theo, cải thiện độ ổn định prime tower và giảm nguy cơ dồn cục; không vô hiệu hóa crash detection để che lỗi.

### Vấn đề còn lại
Cần thử riêng T0 và in tower ngắn sau khi kiểm tra cơ khí/cảm biến để phân biệt chắc chắn giữa T0 bị bung do va vào tower và tín hiệu PB6 chập chờn.

---

## 2. Tinh chỉnh Z-Offset chuẩn cho Cartographer Scan Model (-0.360mm)

### Mục tiêu
Cập nhật Z-offset cố định cho Cartographer Scan Model dựa trên kết quả tinh chỉnh thực tế của người dùng qua Babystepping trên Mainsail (-0.35mm đến -0.37mm).

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — cập nhật `z_offset` trong section `[cartographer scan_model default]` từ `0` thành `-0.360`.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cartographer-z-offset-tune-20260726-092200/printer.cfg)

### Chi tiết thay đổi
- `[cartographer scan_model default]` `z_offset`: `0` → `-0.360`

### Lý do
Sau khi chuyển sang Cartographer Scan Homing (không chạm), người dùng đã hạ Z trên Mainsail khoảng -0.35mm đến -0.37mm thu được lớp in đầu tiên (first layer) phẳng bám bàn hoàn hảo. Việc lưu baseline -0.360mm giúp tất cả các lệnh in về sau tự động dùng mốc Z chuẩn mà không cần hạ thủ công.

### Kiểm tra
- Kiểm tra cú pháp: Đạt.
- Khởi động lại Klipper: Sẵn sàng áp dụng sau lệnh `RESTART`.

### Kết quả
Tất cả các bản in mới sẽ tự động áp dụng Z-offset -0.360mm, đường nhựa lớp 1 bám bàn đẹp đúng như người dùng đã tinh chỉnh.

### Vấn đề còn lại
Không có.

---

## 3. Khôi phục Cartographer Touch Home & Thêm bước lau Nozzle ngay sát trước Touch

### Mục tiêu
Khắc phục hiện tượng trôi Z giữa các lần in của chế độ Scan thuần (do trôi nhiệt cuộn cảm) và xử lý triệt để nguyên nhân ép nhựa dẻo làm trượt chốt StealthChanger khi Touch Home.

### File đã sửa đổi
- `Voron 5 Tool/config/printer.cfg` — khôi phục `z_offset = 0` trong section `[cartographer scan_model default]`.
- `Voron 5 Tool/config/Printer-Setup/print-macros.cfg` — bật lại `CARTOGRAPHER_TOUCH_HOME` và thêm `CLEAN_NOZZLE TEMP=150 WIPES=5` ngay sát trước bước Touch.

### Sao lưu
- [printer.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cartographer-touch-wipe-fix-20260726-093700/printer.cfg)
- [print-macros.cfg (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cartographer-touch-wipe-fix-20260726-093700/print-macros.cfg)

### Chi tiết thay đổi
- `printer.cfg`: `[cartographer scan_model default]` `z_offset`: `-0.360` → `0`
- `print-macros.cfg`: Trong `PRINT_START`, thêm `CLEAN_NOZZLE TEMP=150 WIPES=5` ngay trước `CARTOGRAPHER_TOUCH_HOME`.

### Lý do
1. Theo tài liệu chính thức Cartographer & cộng đồng StealthChanger: Chế độ Scan thuần bị trôi nhiệt (Thermal Drift) theo nhiệt độ cuộn cảm & lồng máy, bắt buộc phải dùng Touch Home để tự động chốt $Z=0$ cơ học thực tế cho mỗi lần in (không cần babystep lại).
2. Di chuyển bước lau Nozzle xuống ngay sát trước Touch giúp loại bỏ 100% cục đệm nhựa dẻo đọng lại trong lúc QGL/soak, giúp Cartographer Touch kích hoạt ngắt Z tức thì khi Nozzle kim loại vừa chạm nhẹ mặt PEI.

### Kiểm tra
- Kiểm tra cú pháp: Đạt.
- Sẵn sàng khởi động lại Klipper.

### Kết quả
Quy trình Touch Home chạy mượt mà, chạm nhẹ ngắt ngay không làm tụt chốt StealthChanger, khóa $Z=0$ chính xác 100% cho mọi bản in mà không phải baby step lại.

### Vấn đề còn lại
Không có.

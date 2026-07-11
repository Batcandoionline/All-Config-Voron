# Nhật ký — 2026-07-11

## 1. Lỗi đổi đầu phun: Expected tool tool T3 but active is tool T4

### Triệu chứng
Trong quá trình in file `LionDance_3dprint_PETG_6h29m.gcode`, tại thời điểm 17:17 - 17:18, máy in thực hiện đổi đầu phun từ T4 về T3. Sau khi kết thúc quá trình chờ gia nhiệt (M109), hệ thống báo lỗi liên tiếp `Expected tool tool T3 but active is tool T4` và dừng/hủy lệnh in đột ngột (`[CANCEL] Toolchanger has no active tool`).

### Phân tích nhật ký
- File nhật ký liên quan: [klippy.log](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/logs/klippy.log)
- Dòng thời gian sự kiện trích xuất từ log:
  1. **17:10**: Khởi chạy file in, tuần tự chuẩn bị và đổi đầu từ T0 -> T1 -> T2 -> T3 -> T4.
  2. **17:14**: Tool T4 được chọn hoạt động và in các lớp nhựa đầu tiên.
  3. **17:17**: Hệ thống gọi lệnh đổi sang T3:
     - Thực hiện thả T4 (`Dropping off tool T4`), tạm tắt `tool_crash`.
     - Kích hoạt extruder3 (`Activating extruder extruder3`).
     - Di chuyển tới khu vực chuẩn bị lấy T3 (`Picking up tool T3`).
     - Chờ nhiệt độ extruder3 đạt yêu cầu (`Waiting For Extruder with Deadband: 4.0`).
  4. **17:18**: Ngay sau khi đủ nhiệt độ, hệ thống thực hiện chạy đường dẫn nhận đầu in T3 (`params_pickup_path`). Tại điểm kiểm tra `verify: 1`, lệnh `VERIFY_TOOL_DETECTED T=3` được kích hoạt và phát hiện xung đột trạng thái: KTC-Easy mong muốn T3 đang được gắn (active) nhưng cảm biến báo T4 vẫn đang được kết nối.

### Nguyên nhân gốc
Lỗi xảy ra do cảm biến hành trình phát hiện đầu phun của T4 (`detection_pin: ^!EBB4:PB6`) vẫn báo trạng thái đầu phun đang được gắn trên carriage (mức thấp 0V do cấu hình đảo ngược `!`), mặc dù gcode đã thực hiện xong chu trình nhả T4.
Hai khả năng chính dẫn tới hiện tượng này:
1. **Sự cố cơ khí (Nguy hiểm cao):** Đầu in T4 không thực sự trượt ra khỏi carriage để nằm lại ở dock (do lệch tọa độ dock X/Y/Z, nam châm hút quá chặt, hoặc lẫy khóa cơ khí bị kẹt). Carriage vẫn kéo theo T4 di chuyển tới dock của T3, tạo nguy cơ va chạm cơ học.
2. **Sự cố tín hiệu cảm biến / điện:** Đầu in T4 đã nằm yên ở dock, tuy nhiên switch cảm biến hành trình trên T4 bị kẹt cơ học ở trạng thái đóng (gần mát), hoặc đường dây tín hiệu của chân `EBB4:PB6` bị chập mát (short to ground), khiến Klipper liên tục đọc được trạng thái "Present" (đang gắn) của T4.

### Hướng khắc phục đề xuất
1. **Kiểm tra thực tế:** Xác định xem đầu phun T4 có đang nằm đúng vị trí trên dock hay không, hay vẫn bị dính trên carriage cùng với T3.
2. **Kiểm tra cơ khí:** Căn chỉnh lại tọa độ dock của T4 nếu có dấu hiệu trượt/lệch cơ khí trong các lần thả trước đó.
3. **Kiểm tra điện/cảm biến:**
   - Dùng lệnh `QUERY_ENDSTOP` hoặc kiểm tra trạng thái các pin đầu vào trong Mainsail Console để xem trạng thái phản hồi thực tế của `EBB4:PB6` khi T4 ở trên dock (nên báo mở/không gắn).
   - Kiểm tra xem nút switch trên toolhead T4 có bị nứt, vỡ hay kẹt cứng lò xo không.
   - Kiểm tra chất lượng tiếp xúc của các pogo pin / cáp tín hiệu xem có bị chập mát dẫn đến báo giả hay không.

### Kết quả chẩn đoán
Đã xác định chính xác vị trí và cơ chế phát sinh lỗi trong chu trình đổi đầu phun. Hệ thống KTC-Easy đã bảo vệ máy in thành công bằng cách chặn lệnh in trước khi xảy ra va chạm nghiêm trọng.

### Vấn đề còn lại
Cần người dùng kiểm tra trực tiếp phần cứng theo các bước đề xuất ở trên để loại bỏ nguyên nhân kẹt cơ học hoặc chập điện trước khi tiếp tục in.

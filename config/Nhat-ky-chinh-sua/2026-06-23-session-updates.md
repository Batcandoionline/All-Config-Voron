# Nhật ký chỉnh sửa - 2026-06-23

## Mục tiêu
Tổng hợp các chỉnh sửa lớn đã áp dụng trong phiên làm việc ngày 23/06/2026 để tối ưu hóa vận hành, chẩn đoán lỗi phần cứng và đồng bộ hóa cấu hình máy in Voron 2.4 StealthChanger.

---

## 1. Đồng bộ cấu hình từ bản tải về (config-20260623-155127)
Đã đồng bộ hóa các tệp cấu hình được tải về từ máy in thực tế vào kho lưu trữ Git:
*   **Dòng điện Extruder (`run_current`):** Đồng bộ hóa dòng điện chạy động cơ đùn của cả 5 đầu in (T0-T4) về mức an toàn **0.6** (riêng đầu T2 được nâng từ `0.50` lên `0.6`).
*   **Ghi chú shaper:** Cập nhật các ghi chú tần số Input Shaper đã đo đạc mới từ thực tế máy in trong các tệp cấu hình đầu phun `Tx.cfg`.
*   **Cải tiến đo bàn (`toolchanger-macros.cfg`):** Cập nhật macro `_TAP_PROBE_ACTIVATE` để hỗ trợ tham số nhiệt độ `TEMP` động, tự động kiểm soát việc làm nóng/nguội đầu phun về mức an toàn (mặc định 150°C) trước khi chạm đo bàn.
*   **Cải tiến nhỏ khác:** Đồng bộ các thay đổi định dạng ký tự trong `homing.cfg`.

---

## 2. Chẩn đoán sụt áp đèn buồng (Chamber Lights)
*   **Hiện tượng:** Khi gọi macro `LIGHTS_ON`, đèn sáng mờ màu đỏ hoặc xanh lá nhạt, không lên được màu trắng. Nguyên nhân do sụt áp nguồn 5V trên Manta M8P V2.0 khi chạy 100% độ sáng (yêu cầu khoảng 2.4A cho 40 bóng LED).
*   **Thay đổi cấu hình:** Chỉnh sửa tạm thời macro `LIGHTS_ON` trong `fans-leds.cfg` thiết lập độ sáng trắng về mức **30%** (`RED=0.3 GREEN=0.3 BLUE=0.3`) để giảm dòng tiêu thụ và chẩn đoán sụt áp.
*   **Hướng phần cứng:** Đề xuất cấp nguồn 5V ngoài qua Buck Converter riêng và chỉ lấy chân tín hiệu Data (`PD15`) từ bo mạch chính.

---

## 3. Tối ưu thời gian ngâm nhiệt (Heat Soak)
*   **Thay đổi cấu hình:** Rút ngắn thời gian ngâm nhiệt trong `print-macros.cfg` để bắt đầu in nhanh hơn:
    *   `PLA_SOAK` giảm xuống còn **30 giây** (trước đây là 60s).
    *   `PETG_SOAK` giảm xuống còn **60 giây** (trước đây là 90s).
    *   `ABS_SOAK` giảm xuống còn **90 giây** (trước đây là 120s).
    *   `HOT_BED_SOAK` giảm xuống còn **90 giây** (trước đây là 120s).

---

## 4. Tối ưu chất lượng và FPS của Webcam (Chuyển sang camera-streamer)
*   **Chẩn đoán lỗi:** Cờ `v4l2ctl` trước đó thiết lập định dạng video không đúng cú pháp Crowsnest, khiến hệ thống bỏ qua và fallback về định dạng raw YUYV. Điều này làm quá tải băng thông USB 2.0 (chỉ đạt ~2-5 FPS) và tốn tài nguyên CPU CM4 để encode. Ngoài ra, MJPEG stream qua ustreamer tiêu tốn quá nhiều băng thông mạng (15-30 Mbps) gây nghẽn và rớt khung hình trên trình duyệt.
*   **Thay đổi cấu hình:** 
    *   Sao lưu cấu hình sang [crowsnest.conf](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/backups/pre-webcam-streamer-20260623-205200/crowsnest.conf).
    *   Chuyển cấu hình `mode` trong [crowsnest.conf](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/config/crowsnest.conf) từ `ustreamer` sang `camera-streamer`.
    *   Tận dụng giao thức **WebRTC (nén H.264)** bằng phần cứng của Raspberry Pi CM4 để giảm băng thông mạng xuống chỉ còn 1-2 Mbps, đem lại FPS tối đa mượt mà và độ trễ dưới 100ms.
    *   Vô hiệu hóa dòng `v4l2ctl` lỗi cú pháp vì `camera-streamer` tự động thương lượng định dạng/độ phân giải phù hợp nhất với camera.


---

## 5. Khắc phục lỗi sụt nhiệt độ bàn in (ADC out of range)
*   **Hiện tượng:** Khi đang gia nhiệt bàn in, nhiệt độ thỉnh thoảng bị nhảy về giá trị âm gây dừng máy khẩn cấp do nhiễu điện từ đóng cắt SSR AC 220V vào cảm biến `PB0`.
*   **Thay đổi cấu hình:** Cập nhật `[heater_bed]` trong `hardware.cfg`:
    *   Thêm `smooth_time: 3.0` để làm mịn kết quả đo ADC trong 3 giây, lọc bỏ các xung nhiễu điện tức thời nhảy về âm độ.
    *   Thêm `pwm_cycle_time: 0.2` (tần số 5Hz thay vì 10Hz) để giảm 50% số lần đóng cắt của SSR, trực tiếp giảm nhiễu EMI cảm ứng và kéo dài tuổi thọ rơ le.

---

## 6. Chỉ dẫn AI và Quản lý Repo
*   **Bổ sung tệp `.cursorrules`:** Lưu trữ các nguyên tắc vận hành bắt buộc dành cho AI Assistant khi làm việc trên kho cấu hình này (quy tắc tạo file backup trong `extras/backups/`, đối chiếu thực tế và quản lý ngôn ngữ).
*   **Bổ sung tệp `.gitignore`:** Loại trừ thư mục tải về `extras/Config download/` chứa các tệp nén lớn để giữ sạch kho lưu trữ Git.
*   **Dịch `README.md`:** Cập nhật và dịch toàn bộ nội dung tệp hướng dẫn chính sang tiếng Anh hoàn chỉnh để đồng nhất hiển thị trên GitHub.

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

## 4. Tối ưu chất lượng và FPS của Webcam (Chuyển sang camera-streamer & Cấu hình 2K MJPEG)
*   **Chẩn đoán lỗi:** Dựa trên thông số nhà sản xuất cung cấp tại tệp [1782223994046_temp.jpg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/pictures/1782223994046_temp.jpg) và tệp [1782224117773_temp.jpg](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/pictures/1782224117773_temp.jpg), camera MF-500 chỉ hỗ trợ tối đa 1 FPS (ở 2K) khi chạy định dạng YUY2 do băng thông USB 2.0. Để đạt được **30 FPS**, camera bắt buộc phải truyền tín hiệu ở định dạng **MJPEG**. Đồng thời, camera hỗ trợ tính năng khử nhấp nháy đèn (anti-flicker) ở tần số 50Hz/60Hz.
*   **Thay đổi cấu hình:** 
    *   Sao lưu cấu hình sang [crowsnest.conf (Backup)](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/extras/backups/pre-webcam-exact-2k-20260623-211700/crowsnest.conf).
    *   Thiết lập độ phân giải gốc của nhà sản xuất lên **`2560x1400` (độ phân giải 2K thực tế)** trong [crowsnest.conf](file:///c:/Users/batca/OneDrive/Desktop/All-Config-Voron-main/All-Config-Voron-work/config/crowsnest.conf).
    *   Sử dụng cờ cấu hình `custom_flags: --camera-format=MJPEG` trong chế độ `camera-streamer` nhằm ép phần cứng camera xuất ảnh chuẩn MJPEG 30 FPS.
    *   Cấu hình `v4l2ctl: power_line_frequency=1` (thiết lập tần số khử nháy là 50Hz cho phù hợp với điện lưới Việt Nam).




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

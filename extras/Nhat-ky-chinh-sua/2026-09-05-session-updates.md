# Nhật ký chỉnh sửa & vận hành — 2026-09-05

## 1. Rà soát, lọc và loại bỏ tài liệu cũ/sai lệch trong `extras/docs/`

### Mục tiêu
- Đối chiếu toàn bộ 16 tài liệu trong `extras/docs/` với mã nguồn Klipper và kTAMV đang vận hành thực tế (`printer.cfg`, `moonraker.conf`, `config/scripts/install.sh`, `Printer-Setup/*.cfg`).
- Loại bỏ các tài liệu cũ, hướng dẫn sai lệch hoặc đề xuất không thuộc phạm vi máy in.
- Đồng bộ hóa hướng dẫn vận hành StealthChanger và chỉ mục tài liệu với kiến trúc hệ thống hiện tại.

### File đã xóa (Loại bỏ 7 file cũ/sai)
- `Voron 5 Tool/extras/docs/toolvision-integration-guide.vi.md` (Hướng dẫn sai: nạp `tool-vision.cfg` và chạy `tool-vision.service` vốn đã bị gỡ)
- `Voron 5 Tool/extras/docs/toolvision-integration-guide.en.md` (Bản tiếng Anh của hướng dẫn ToolVision đã retired)
- `Voron 5 Tool/extras/docs/toolvision-v4-greenfield-rewrite-prompt.vi.md` (Prompt 23KB cho AI viết lại repo bên ngoài `Tool-Vision`, không thuộc máy in)
- `Voron 5 Tool/extras/docs/toolvision-xy-repeat-average-proposal.vi.md` (Đề xuất cho codebase ToolVision cũ)
- `Voron 5 Tool/extras/docs/toolvision-xy-repeat-average-proposal.en.md` (Bản tiếng Anh của đề xuất lặp XY)
- `Voron 5 Tool/extras/docs/toolvision-z-calibration-ux-proposal.vi.md` (Đề xuất UX đo Z cho nhánh ToolVision cũ)
- `Voron 5 Tool/extras/docs/toolvision-z-calibration-ux-proposal.md` (Bản tiếng Anh của đề xuất UX đo Z)

### File đã sửa đổi (Đồng bộ theo mã nguồn thực tế)
- `Voron 5 Tool/extras/docs/huong-dan-he-thong-stealthchanger.md`:
  - Bổ sung 2 file include đang nạp thực tế vào mục 2: `filament-dryer.cfg` và `test-speed.cfg`.
  - Bổ sung liên kết tới báo cáo đo kiểm `danh-gia-input-shaper-va-test-speed-2026-09-04.md` tại mục 9.
  - Bổ sung phương thức cập nhật 1-Click trực tiếp từ giao diện web Mainsail (Update Manager) tại mục 10.
  - Bỏ liên kết trỏ tới tài liệu ToolVision cũ.
- `Voron 5 Tool/extras/docs/huong-dan-he-thong-stealthchanger.en.md`:
  - Đồng bộ các cập nhật tương ứng cho bản tiếng Anh.
- `Voron 5 Tool/extras/docs/README.vi.md` & `README.md`:
  - Cập nhật bảng chỉ mục tài liệu hiện hành: thêm 2 tài liệu thực nghiệm mới ngày 04/09/2026 (`danh-gia-input-shaper-va-test-speed-2026-09-04.md` và `danh-sach-doi-chieu-va-huong-dan-update-mainsail.md`).
  - Cập nhật mục nội dung lịch sử ghi nhận việc dọn dẹp các tài liệu ToolVision cũ đã được bảo toàn trong Git và backup ngày 31/08/2026.

### Lý do
- Mã nguồn thực tế của máy in Voron 5 Tool đã loại bỏ hoàn toàn ToolVision từ ngày 31/08/2026 để chuyển sang kTAMV căn tâm XY được ghim commit và bảo vệ an toàn trong `install.sh`.
- Việc giữ lại các tài liệu ToolVision với hướng dẫn nạp `tool-vision.cfg` gây mâu thuẫn trực tiếp với `printer.cfg` và gây hiểu lầm cho người vận hành.
- Cơ cấu include đã mở rộng thêm 2 module `filament-dryer.cfg` và `test-speed.cfg`, cùng cơ chế Update Manager 1-Click trên Mainsail vừa được tích hợp ngày 04/09/2026, do đó tài liệu vận hành cần phản ánh chuẩn xác 100% hiện trạng code.

### Kiểm tra
- Đối chiếu code: 100% khớp với `printer.cfg` (12 module), `moonraker.conf` (Update Manager), `install.sh`.
- Kiểm tra liên kết: Không còn bất kỳ liên kết chết (broken link) nào trong thư mục `extras/docs/`.
- Toàn vẹn cấu hình: Không có bất kỳ file cấu hình Klipper (`.cfg`, `.conf`) nào bị ảnh hưởng.

### Kết quả
- Thư mục `extras/docs/` từ 16 file đã được làm sạch gọn gàng còn đúng 9 file chuẩn xác, bao gồm:
  1. `BIGTREETECH MANTA M8P V2.0 User Manual.pdf`
  2. `danh-gia-input-shaper-va-test-speed-2026-09-04.md`
  3. `danh-sach-doi-chieu-va-huong-dan-update-mainsail.md`
  4. `huong-dan-he-thong-stealthchanger.md`
  5. `huong-dan-he-thong-stealthchanger.en.md`
  6. `ktamv-usage-comparison.vi.md`
  7. `ktamv-usage-comparison.en.md`
  8. `README.vi.md`
  9. `README.md`

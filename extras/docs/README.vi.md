# Chỉ mục tài liệu và chính sách ngôn ngữ

[English](README.md) | [Tiếng Việt](README.vi.md)

Chỉ mục này tách tài liệu hiện hành khỏi bằng chứng bất biến. Tài liệu do dự án
sở hữu và đang dùng được duy trì theo cặp Anh–Việt. Journal lịch sử, snapshot
backup và snapshot tải từ máy phải giữ nguyên nội dung tại thời điểm ghi; viết
lại sẽ làm mất ý nghĩa rollback/audit.

Baseline của lần cập nhật này là config production hiện tại, toàn bộ Markdown
trong repository và commit upstream kTAMV `72421f2`, review ngày 2026-08-31.

## Tài liệu hiện hành

| Chủ đề | English | Tiếng Việt |
| --- | --- | --- |
| Tổng quan project/hệ thống | [README](../../README.md) | [README](../../README.vi.md) |
| Payload config hoạt động | [README](../../config/README.md) | [README](../../config/README.vi.md) |
| Đồng bộ/profile OrcaSlicer | [README](../../Orca%20Config/README.md) | [README](../../Orca%20Config/README.vi.md) |
| Vận hành StealthChanger | [Hướng dẫn](huong-dan-he-thong-stealthchanger.en.md) | [Hướng dẫn](huong-dan-he-thong-stealthchanger.md) |
| Sử dụng kTAMV và đối chiếu phương pháp | [Hướng dẫn](ktamv-usage-comparison.en.md) | [Hướng dẫn](ktamv-usage-comparison.vi.md) |
| Đo kiểm TEST_SPEED & Input Shaper (04/09/2026) | — | [Báo cáo](danh-gia-input-shaper-va-test-speed-2026-09-04.md) |
| Cập nhật 1-Click Mainsail & Đối chiếu 51 file (04/09/2026) | — | [Hướng dẫn](danh-sach-doi-chieu-va-huong-dan-update-mainsail.md) |

## Nội dung lịch sử và retired

- `extras/Nhat-ky-chinh-sua/`: lịch sử kỹ thuật append-only. Entry cũ không được
  dịch hoặc hiện đại hóa sau thời điểm ghi. Nhóm tài liệu hiện hành bên trên cung
  cấp điều hướng song ngữ và mô tả trạng thái mới.
- [`axiscope-cartographer/`](../axiscope-cartographer/README.md): bằng chứng fork
  local không còn active, giữ cho rollback/tham khảo. Trạng thái local được tóm
  tắt song ngữ trong [`FORK_INFO.md`](../axiscope-cartographer/FORK_INFO.md).
- [`retired-configs/2026-08-20-config-merge/`](../retired-configs/2026-08-20-config-merge/README.md):
  file không còn được `printer.cfg` include; README có cả hai ngôn ngữ.
- [`retired-configs/2026-08-31-toolvision-removal/`](../retired-configs/2026-08-31-toolvision-removal/README.md):
  CFG ToolVision cuối cùng của máy, giữ nguyên byte sau khi chuyển sang kTAMV.
- **ToolVision docs & proposals:** Toàn bộ các hướng dẫn cài đặt và đề xuất cũ liên quan tới ToolVision
  đã được loại bỏ khỏi `docs/` để tránh sai lệch cấu hình; dữ liệu lịch sử được bảo toàn trong Git và bản
  sao lưu [`pre-replace-toolvision-with-ktamv-20260831-113047`](../backups/pre-replace-toolvision-with-ktamv-20260831-113047/README.md).
- `extras/Config download/`: snapshot tải từ máy, không phải tài liệu repository
  hiện hành và không được sửa.

## Snapshot rollback được theo dõi gần đây

Chỉ thêm liên kết và context hiện tại ở đây; nội dung snapshot giữ bất biến.

1. [`pre-replace-toolvision-with-ktamv-20260831-113047`](../backups/pre-replace-toolvision-with-ktamv-20260831-113047/README.md) — trước khi gỡ tích hợp ToolVision active và cài kTAMV được pin.
2. [`pre-move-toolvision-to-printer-setup-20260823-220605`](../backups/pre-move-toolvision-to-printer-setup-20260823-220605/README.md) — trước khi chuyển config ToolVision riêng của máy vào `Printer-Setup/` và định tuyến JSON dưới `Generated-Data/ToolVision/`.
3. [`pre-toolvision-z-canary-20260823-211530`](../backups/pre-toolvision-z-canary-20260823-211530/README.md) — trước khi bật canary ToolVision PF2 chỉ báo cáo.

Đây là snapshot được Git repository theo dõi, không phải tuyên bố các thư mục đó
hiện tồn tại trên CM4. Hành động retention phía máy được ghi trong journal bất
biến theo ngày tương ứng.

## Quy tắc cập nhật tài liệu sau này

1. Đọc config và script đang nạp trước khi đổi mô tả hiện trạng.
2. Gắn nhãn sự thật là active, observed, development/planned hoặc unknown.
3. Cập nhật cả hai bản ngôn ngữ trong cùng commit.
4. Không biến kế hoạch thành tuyên bố đã triển khai.
5. Không viết lại journal cũ, README backup hoặc snapshot tải về; thêm guide/
   index hiện hành mới.
6. Khi code, path hoặc hành vi macro đổi, cập nhật cặp tài liệu liên quan và
   journal ngày trong cùng thay đổi.

# Chỉ mục tài liệu và chính sách ngôn ngữ

[English](README.md) | [Tiếng Việt](README.vi.md)

Chỉ mục này tách tài liệu hiện hành khỏi bằng chứng bất biến. Tài liệu do dự án
sở hữu và đang dùng được duy trì theo cặp Anh–Việt. Journal lịch sử, snapshot
backup và snapshot tải từ máy phải giữ nguyên nội dung tại thời điểm ghi; viết
lại sẽ làm mất ý nghĩa rollback/audit.

Baseline đọc source của lần cập nhật này: All-Config commit `9d848f04`, bằng
chứng ToolVision đã deploy `2b3bf2c6`, nhánh UX ToolVision đang phát triển
`2d936f3`, review ngày 2026-08-24.

## Tài liệu song ngữ hiện hành

| Chủ đề | English | Tiếng Việt |
| --- | --- | --- |
| Tổng quan project/hệ thống | [README](../../README.md) | [README](../../README.vi.md) |
| Payload config hoạt động | [README](../../config/README.md) | [README](../../config/README.vi.md) |
| Đồng bộ/profile OrcaSlicer | [README](../../Orca%20Config/README.md) | [README](../../Orca%20Config/README.vi.md) |
| Vận hành StealthChanger | [Hướng dẫn](huong-dan-he-thong-stealthchanger.en.md) | [Hướng dẫn](huong-dan-he-thong-stealthchanger.md) |
| Tích hợp ToolVision trên máy | [Hướng dẫn](toolvision-integration-guide.en.md) | [Hướng dẫn](toolvision-integration-guide.vi.md) |
| Trạng thái UX đo Z ToolVision | [Bằng chứng/trạng thái](toolvision-z-calibration-ux-proposal.md) | [Bằng chứng/trạng thái](toolvision-z-calibration-ux-proposal.vi.md) |

## Nội dung lịch sử và retired

- `extras/Nhat-ky-chinh-sua/`: lịch sử kỹ thuật append-only. Entry cũ không được
  dịch hoặc hiện đại hóa sau thời điểm ghi. Nhóm tài liệu hiện hành bên trên cung
  cấp điều hướng song ngữ và mô tả trạng thái mới.
- [`axiscope-cartographer/`](../axiscope-cartographer/README.md): bằng chứng fork
  local không còn active, giữ cho rollback/tham khảo. Trạng thái local được tóm
  tắt song ngữ trong [`FORK_INFO.md`](../axiscope-cartographer/FORK_INFO.md).
- [`retired-configs/2026-08-20-config-merge/`](../retired-configs/2026-08-20-config-merge/README.md):
  file không còn được `printer.cfg` include; README có cả hai ngôn ngữ.
- `extras/Config download/`: snapshot tải từ máy, không phải tài liệu repository
  hiện hành và không được sửa.

## Ba snapshot rollback được theo dõi gần đây

Chỉ thêm liên kết và context hiện tại ở đây; nội dung snapshot giữ bất biến.

1. [`pre-move-toolvision-to-printer-setup-20260823-220605`](../backups/pre-move-toolvision-to-printer-setup-20260823-220605/README.md) — trước khi chuyển config ToolVision riêng của máy vào `Printer-Setup/` và định tuyến JSON dưới `Generated-Data/ToolVision/`.
2. [`pre-toolvision-z-canary-20260823-211530`](../backups/pre-toolvision-z-canary-20260823-211530/README.md) — trước khi bật canary ToolVision PF2 chỉ báo cáo.
3. [`pre-ktc-ownership-and-doc-sync-20260823-083206`](../backups/pre-ktc-ownership-and-doc-sync-20260823-083206/README.md) — trước khi đồng bộ quyền sở hữu KTC và tài liệu.

Đây là snapshot được Git repository theo dõi, không phải tuyên bố ba thư mục
hiện tồn tại trên CM4. Việc dọn retention trên máy và ba recovery point được giữ
đã ghi trong journal bất biến
[`2026-08-23-session-updates.md`](../Nhat-ky-chinh-sua/2026-08-23-session-updates.md).

## Quy tắc cập nhật tài liệu sau này

1. Đọc config và script đang nạp trước khi đổi mô tả hiện trạng.
2. Gắn nhãn sự thật là active, observed, development/planned hoặc unknown.
3. Cập nhật cả hai bản ngôn ngữ trong cùng commit.
4. Không biến kế hoạch thành tuyên bố đã triển khai.
5. Không viết lại journal cũ, README backup hoặc snapshot tải về; thêm guide/
   index hiện hành mới.
6. Khi code, path hoặc hành vi macro đổi, cập nhật cặp tài liệu liên quan và
   journal ngày trong cùng thay đổi.

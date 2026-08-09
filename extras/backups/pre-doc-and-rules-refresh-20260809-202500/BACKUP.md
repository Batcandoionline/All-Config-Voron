# Quy tắc sao lưu

## Quy tắc sao lưu bắt buộc

> **Trước khi sửa đổi BẤT KỲ file cấu hình nào (`.cfg`, `.conf`), bạn PHẢI tạo bản sao lưu.**
>
> Không ngoại lệ. Không tắt.

## Vị trí sao lưu

```
Voron 5 Tool/extras/backups/pre-[tên_tác_vụ]-[YYYYMMDD]-[HHmmss]/
```

### Quy ước đặt tên

| Thành phần | Định dạng | Ví dụ |
|-----------|-----------|-------|
| Tiền tố | Luôn `pre-` | `pre-` |
| Tên tác vụ | Chữ thường, dấu gạch ngang, mô tả | `input-shaper-tune` |
| Ngày | `YYYYMMDD` | `20260702` |
| Giờ | `HHmmss` | `210300` |

### Ví dụ

```
pre-input-shaper-tune-20260702-210300/
pre-z-offset-calibration-20260702-153045/
pre-pressure-advance-t3-20260630-183036/
pre-cartographer-touch-calib-20260630-181633/
```

## Nội dung bản sao lưu

Mỗi thư mục sao lưu **phải** chứa:

1. **File gốc** — Bản sao chính xác của file sắp bị sửa đổi, giữ nguyên tên file gốc.
2. **README.md** — File tóm tắt ngắn gọn:

```markdown
# Bản ghi sao lưu

- **Ngày:** YYYY-MM-DD HH:mm:ss
- **Tác vụ:** Mô tả ngắn gọn những gì sắp thay đổi
- **File đã sao lưu:**
  - `filename.cfg` — lý do sửa đổi
- **Nhật ký liên quan:** `extras/Nhat-ky-chinh-sua/YYYY-MM-DD-session-updates.md`
```

## Quy tắc chi tiết

1. **Một bản sao lưu cho mỗi tác vụ** — Nếu sửa nhiều file cho cùng một tác vụ, đặt tất cả vào một thư mục sao lưu duy nhất.
2. **Không bao giờ ghi đè** — Mỗi thư mục sao lưu có timestamp riêng. Không bao giờ xóa hoặc sửa đổi bản sao lưu hiện có.
3. **Đã gitignore** — Thư mục `extras/backups/` nằm trong `.gitignore`. Bản sao lưu chỉ lưu cục bộ.
4. **Sao lưu trước khi đọc? Không.** — Sao lưu chỉ bắt buộc trước khi *ghi*. Đọc file cấu hình không cần sao lưu.

## Sao lưu nhận biết quyền hạn

- **Nếu assistant có quyền ghi** vào `extras/backups/`: Tạo sao lưu tự động và không cần hỏi.
- **Nếu quyền ghi bị giới hạn hoặc không có**: Thông báo người dùng rằng không thể tạo sao lưu tự động, và cung cấp nội dung file hoặc lệnh shell chính xác để tạo sao lưu thủ công. **Không tiến hành sửa đổi cho đến khi người dùng xác nhận bản sao lưu đã tồn tại.**

## Quy trình hoàn tác (Rollback)

Nếu một thay đổi gây ra vấn đề:

1. Tìm thư mục sao lưu cho tác vụ liên quan trong `extras/backups/`.
2. Sao chép file sao lưu về vị trí gốc trong `config/`.
3. Khởi động lại Klipper để áp dụng hoàn tác.
4. Ghi nhận việc hoàn tác vào nhật ký hàng ngày.

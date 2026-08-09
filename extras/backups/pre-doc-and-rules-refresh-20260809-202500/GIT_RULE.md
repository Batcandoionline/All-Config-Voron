# Quy tắc Git

## Thông tin kho lưu trữ

- **Thư mục gốc git:** `Voron 5 Tool/`
- **Remote:** `origin` → GitHub (`IDcrazy123/All-Config-Voron`)
- **Nhánh:** `main`

## Định dạng commit message

```
<loại>: <mô tả ngắn gọn bằng tiếng Anh>
```

### Các loại commit

| Loại | Sử dụng khi |
|------|-------------|
| `config` | Thay đổi giá trị cấu hình máy in (nhiệt độ, offset, tốc độ...) |
| `feat` | Thêm tính năng mới (macro mới, cấu hình tool mới, chức năng mới) |
| `fix` | Sửa lỗi hoặc giải quyết vấn đề |
| `refactor` | Tái cấu trúc cấu hình mà không thay đổi hành vi |
| `docs` | Thay đổi tài liệu (README, nhật ký hàng ngày, changelog) |
| `chore` | Tác vụ bảo trì (dọn dẹp, format, cập nhật .gitignore) |

### Ví dụ commit message

```
config: tune pressure advance for tool T3
config: update Cartographer touch threshold to 2594
feat: add nozzle cleaning macro for T4
fix: resolve idle timeout macro conflict
docs: add troubleshooting log for cartographer connection timeout
chore: update .gitignore for security before public release
```

### Quy tắc

1. **Ngôn ngữ:** Commit message phải bằng tiếng Anh.
2. **Tiền tố chữ thường:** Luôn viết thường (`config:` không phải `Config:`).
3. **Không chấm cuối** message.
4. **Thì hiện tại:** "add" không phải "added", "fix" không phải "fixed".
5. **Mô tả rõ:** Message phải giải thích *cái gì* đã thay đổi, không chỉ *rằng* có gì đó thay đổi.

---

## Quy tắc Auto-Push

### Nếu môi trường cho phép truy cập terminal và người dùng không cấm:

Sau khi hoàn tất tất cả sửa đổi và ghi nhật ký, tự động thực thi:

```bash
git add <các file đã thay đổi>
git commit -m "<loại>: <mô tả>"
git push
```

### Nếu không có quyền truy cập terminal:

Chuẩn bị danh sách đầy đủ lệnh git và trình bày cho người dùng chạy thủ công:

```bash
# Sao chép và chạy các lệnh sau:
cd "Voron 5 Tool"
git add config/path/to/changed/file.cfg
git add extras/Nhat-ky-chinh-sua/YYYY-MM-DD-session-updates.md
git commit -m "config: mô tả thay đổi"
git push
```

---

## Quy tắc Gitignore

Các mục sau bị loại khỏi kho lưu trữ (định nghĩa trong `.gitignore`):

- `extras/backups/` — File sao lưu cục bộ
- `*.secrets` — File thông tin nhạy cảm
- `moonraker.secrets` — API key Moonraker
- `wpa_supplicant.conf` — Thông tin WiFi

**Không bao giờ commit** các file khớp với các mẫu trên.

---

## Quy tắc Staging

1. **Chỉ stage file liên quan** — Không stage thay đổi không liên quan vào cùng một commit.
2. **Bao gồm nhật ký hàng ngày** — Khi commit thay đổi cấu hình, luôn bao gồm file nhật ký tương ứng.
3. **Không stage file log** — `extras/logs/klippy.log` và `moonraker.log` lớn và thay đổi thường xuyên. Không stage trừ khi được yêu cầu rõ ràng.

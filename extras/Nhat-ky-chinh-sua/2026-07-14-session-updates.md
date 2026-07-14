# Nhật ký — 2026-07-14

## 1. Cập nhật tên người dùng GitHub (Batcandoionline → IDcrazy123)

### Mục tiêu
Người dùng đã đổi tên tài khoản GitHub từ `Batcandoionline` sang `IDcrazy123`. Cần cập nhật tất cả tham chiếu trong kho lưu trữ để phản ánh tên mới.

### File đã sửa đổi
- `.agents/GIT_RULE.md` — cập nhật thông tin remote
- `Voron 5 Tool/README.md` — cập nhật URL git clone
- `Voron 5 Tool/config/README.md` — cập nhật URL git clone
- `Voron 5 Tool/config/scripts/install.sh` — cập nhật REPO_URL
- `Voron 5 Tool/config/scripts/update.sh` — cập nhật REPO_URL
- `Voron 5 Tool/extras/axiscope-cartographer/README.md` — cập nhật 2 URL (git clone + moonraker origin)
- `Voron 5 Tool/extras/axiscope-cartographer/FORK_INFO.md` — cập nhật URL maintained fork
- `Voron 5 Tool/extras/axiscope-cartographer/install.sh` — cập nhật REPO_URL

### Sao lưu
Không có file cấu hình máy in (.cfg) nào bị thay đổi. Chỉ thay đổi tài liệu và script. Không cần sao lưu theo quy trình BACKUP.md.

### Chi tiết thay đổi
- `Batcandoionline` → `IDcrazy123` (tất cả URL GitHub trong dự án)
- Git remote local cũng đã được cập nhật: `git remote set-url origin git@github.com:IDcrazy123/All-Config-Voron.git`

### Lý do
Người dùng đổi tên tài khoản GitHub. Tên cũ trong nhật ký lịch sử (2026-05-16, 2026-05-18) được giữ nguyên vì đó là dữ liệu lịch sử.

### Kiểm tra
- Kiểm tra cú pháp: không áp dụng (không phải file .cfg)
- Git remote đã xác nhận cập nhật đúng

### Kết quả
Tất cả tham chiếu URL đang hoạt động (README, scripts, FORK_INFO) đã được cập nhật sang tên GitHub mới `IDcrazy123`.

### Vấn đề còn lại
- Cần đảm bảo repo `Axiscope-cartographer` trên GitHub cũng đã được cập nhật URL (GitHub tự chuyển hướng khi đổi tên user, nhưng nên cập nhật URL trong moonraker.conf trên máy in).
- Kiểm tra `moonraker.conf` trên máy in — nếu có `[update_manager axiscope]` với URL cũ, cần cập nhật thủ công.

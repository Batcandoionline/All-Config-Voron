# Cấu hình OrcaSlicer (Orca Config)

Thư mục này lưu trữ các profile tùy chỉnh (custom profiles) của OrcaSlicer dùng cho máy in **Voron 2.4 StealthChanger (5-Tool)**, bao gồm cấu hình máy in (`machine`), cấu hình nhựa (`filament`) và cấu hình tiến trình in (`process`).

---

## ⚡ Đồng bộ tự động (Automatic Synchronization)

Sau khi chỉnh sửa hoặc tạo preset mới trong phần mềm OrcaSlicer, bạn có thể đồng bộ nhanh bằng cách nhấp đúp file:

```text
Sync-OrcaProfiles.cmd
```

Hoặc chạy dòng lệnh PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\Orca Config\Sync-OrcaProfiles.ps1"
```

**Cơ chế hoạt động của `Sync-OrcaProfiles.ps1`:**
1. Tự động phát hiện tài khoản OrcaSlicer được sử dụng gần nhất dưới đường dẫn `%APPDATA%\OrcaSlicer\user`.
2. Kiểm tra và xác thực các file JSON profile (`machine`, `process`, `filament`).
3. Tạo bản sao lưu tự động tại `extras/backups/pre-orcaslicer-profile-sync-<timestamp>/`.
4. Sao chép các file JSON active vào thư mục `Orca Config/`.
5. Tạo commit Git và thực hiện `git push` tự động lên GitHub repository.

---

## 📂 Danh sách các Profile chính hiện có

### 1. Cấu hình máy in (Machine Profiles)
- `Voron Stealthchanger.json` — Profile máy in Voron 2.4 StealthChanger 5 đầu đùn (T0–T4)
- `Stealthchanger.json` — Preset máy in StealthChanger tham chiếu
- `VoronStealthchanger.json` — Variant profile máy in

### 2. Cấu hình tiến trình in (Process Profiles)
- `0.20mm ABS.json` — Tiến trình in ABS tiêu chuẩn 0.20mm
- `0.20mm ABS TPmoins.json` — Tiến trình in ABS tối ưu cho nhựa TPmoins
- `0.20mm PETG Multimaterial.json` — Tiến trình in nhiều màu / nhiều đầu phun PETG
- `0.20 Tinmory.json` — Tiến trình in PETG/ABS Tinmory

### 3. Cấu hình nhựa (Filament Profiles)
- **ABS:** `ABS Tpoimns Black.json`, `ABS Tpoimns Pink.json`, `ABS-Pro Tinmory Black.json`
- **PETG:** `PETG Bambu Basic Black.json`, `PETG Bambu Basic.json`, `PETG Kabber Blue.json`, `PETG Noname Antums.json`, `PETG TPoimns Black.json`, `PETG TPoimns Gray.json`, `PETG TPoimns Orange.json`, `PETG TPoimns Red.json`, `PETG TPoimns White.json`, `PETG TPoimns Yellow.json`, `PETG Tinmory Black.json`, `PETG Tinmory.json`

---

## 🔄 Khôi phục thủ công về OrcaSlicer (Restore Profiles)

Nếu bạn vừa clone repository về máy tính mới và muốn đưa các profile này vào OrcaSlicer:

**Đường dẫn tài khoản OrcaSlicer trên Windows:**
```cmd
%APPDATA%\OrcaSlicer\user\<user_id>\
```

**Thao tác copy bằng PowerShell:**
```powershell
# Copy các file .json từ repo vào thư mục OrcaSlicer user
$orcaUser = Get-ChildItem "$env:APPDATA\OrcaSlicer\user" | Select-Object -First 1
Copy-Item -Path ".\Orca Config\Voron Stealthchanger.json" -Destination "$orcaUser.FullName\machine\" -Force
Copy-Item -Path ".\Orca Config\PETG*.json" -Destination "$orcaUser.FullName\filament\" -Force
Copy-Item -Path ".\Orca Config\0.20*.json" -Destination "$orcaUser.FullName\process\" -Force
```

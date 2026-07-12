# Cấu hình OrcaSlicer (Orca Config)

Thư mục này lưu trữ các profile tùy chỉnh (custom profiles) của OrcaSlicer dùng cho máy in **Voron 2.4 StealthChanger (5-Tool)**, bao gồm cấu hình máy in (`machine`), cấu hình nhựa (`filament`) và cấu hình tiến trình in (`process`).

---

## 📂 Danh sách các file cấu hình quan trọng

- **Máy in (Machine):**
  - `Voron Stealthchanger.json` — Cấu hình máy in Voron Stealthchanger 5 đầu đùn
- **Tiến trình in (Process):**
  - `0.20mm ABS.json` — Cấu hình in ABS chiều cao lớp 0.20mm
  - `0.20mm PETG Multimaterial.json` — Cấu hình in nhiều màu PETG
  - `0.20 Tinmory.json` — Cấu hình in cho nhựa Tinmory
- **Nhựa (Filament):**
  - Các cấu hình nhựa ABS, PETG chuyên dụng cho từng hãng (`Tinmory`, `TPoimns`, `Bambu Basic`...).

---

## 🔄 Hướng dẫn đồng bộ và sao chép cấu hình

Khi bạn cập nhật các profile trong OrcaSlicer và muốn lưu trữ chúng lên GitHub, hoặc muốn khôi phục chúng từ GitHub về máy tính:

### 1. Vị trí lưu trữ profile của OrcaSlicer trên Windows
OrcaSlicer lưu trữ các profile tùy chỉnh của người dùng tại đường dẫn:
```cmd
%APPDATA%\OrcaSlicer\user\<user_id>\
```
*(Trong đó `<user_id>` là một chuỗi mã định danh duy nhất của tài khoản của bạn, ví dụ: `838ce884-12ee-416b-9e1b-1c7503cf6b5f`)*

Trong thư mục này sẽ có các thư mục con:
- `machine/` — Cấu hình máy in
- `filament/` — Cấu hình nhựa
- `process/` — Cấu hình tiến trình in

---

### 2. Cách sao chép tự động (Bằng dòng lệnh PowerShell)

Để tự động sao chép toàn bộ các file `.json` từ OrcaSlicer vào thư mục này để chuẩn bị commit lên GitHub:

1. Mở PowerShell.
2. Chạy câu lệnh sau (đường dẫn đã được cấu hình tự động cho tài khoản của bạn):
```powershell
Get-ChildItem -Path "$env:APPDATA\OrcaSlicer\user\838ce884-12ee-416b-9e1b-1c7503cf6b5f" -Filter *.json -Recurse | Copy-Item -Destination "C:\Users\batca\OneDrive\Desktop\All-Config-Voron-main\Orca Config" -Force
```

Nếu bạn muốn copy ngược lại từ GitHub vào OrcaSlicer (sau khi clone repo hoặc pull code mới về máy):
1. **Sao chép cấu hình Máy in:**
```powershell
Copy-Item -Path "C:\Users\batca\OneDrive\Desktop\All-Config-Voron-main\Orca Config\Voron Stealthchanger.json" -Destination "$env:APPDATA\OrcaSlicer\user\838ce884-12ee-416b-9e1b-1c7503cf6b5f\machine\" -Force
```
2. **Sao chép cấu hình Nhựa (Filament):**
```powershell
# Ví dụ copy file PETG TPoimns Black.json
Copy-Item -Path "C:\Users\batca\OneDrive\Desktop\All-Config-Voron-main\Orca Config\PETG TPoimns Black.json" -Destination "$env:APPDATA\OrcaSlicer\user\838ce884-12ee-416b-9e1b-1c7503cf6b5f\filament\" -Force
```
3. **Sao chép cấu hình Tiến trình in (Process):**
```powershell
# Ví dụ copy file 0.20mm ABS.json
Copy-Item -Path "C:\Users\batca\OneDrive\Desktop\All-Config-Voron-main\Orca Config\0.20mm ABS.json" -Destination "$env:APPDATA\OrcaSlicer\user\838ce884-12ee-416b-9e1b-1c7503cf6b5f\process\" -Force
```

---

### 3. Cách sao chép thủ công (Giao diện đồ họa)
Nếu bạn không muốn sử dụng dòng lệnh:
1. Nhấn tổ hợp phím `Windows + R`, gõ `%APPDATA%\OrcaSlicer\user` và nhấn **Enter**.
2. Truy cập vào thư mục ID người dùng của bạn.
3. Vào các thư mục `filament`, `machine`, `process` copy các file `.json` bạn muốn và dán vào thư mục `Orca Config` trong thư mục Git này.
4. Ngược lại, khi muốn khôi phục, bạn copy các file `.json` từ thư mục này dán vào các thư mục tương ứng trong AppData của OrcaSlicer.

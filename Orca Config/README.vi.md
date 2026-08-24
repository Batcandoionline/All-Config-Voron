# Profile OrcaSlicer

[English](README.md) | [Tiếng Việt](README.vi.md)

Thư mục này chứa bản sao trong repository của các profile OrcaSlicer dùng cho
máy Voron năm tool: ba profile machine, bốn profile process và 15 profile
filament. File JSON là artifact nguồn; README không suy diễn setting không tồn
tại trong JSON.

## Hành vi đồng bộ

Nhấp đúp `Sync-OrcaProfiles.cmd` sẽ chạy:

```powershell
Sync-OrcaProfiles.ps1 -IncludeDiagnostics -Commit -Push
```

Đây là đường tự động hoàn toàn: chọn Orca user profile được sửa gần nhất, kiểm
tra JSON, đồng bộ profile thay đổi, lấy diagnostic được script chọn, ghi nhật ký
ngày, tạo commit Git đúng phạm vi và push.

Chạy PowerShell trực tiếp phù hợp hơn khi muốn review vì commit, push và
diagnostic đều là tùy chọn:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File ".\Orca Config\Sync-OrcaProfiles.ps1"
```

Các switch hữu ích:

| Switch | Hành vi trong code |
| --- | --- |
| `-ProfileId <id>` | Chọn đúng thư mục Orca user thay vì profile được sửa gần nhất |
| `-SkipAnalysisAliases` | Không cập nhật hai alias phân tích trong `extras/Orcasilcer setting/` |
| `-IncludeDiagnostics` | Đưa diagnostic do script chọn vào phạm vi commit |
| `-Commit` | Chỉ stage đường dẫn do đồng bộ sở hữu và tạo commit |
| `-Push` | Tự bật `-Commit`, rồi push nhánh hiện tại |

Script đọc `%APPDATA%\OrcaSlicer\user`, tìm JSON trong `machine`, `process` và
`filament`, parse mọi file được chọn và từ chối tên destination phẳng bị trùng.
Nó chỉ copy file thay đổi. Trước khi thay một destination đã tồn tại, script
lưu file cũ vào
`extras/backups/pre-orcaslicer-profile-sync-<timestamp>/`. File được copy lần
đầu không có destination cũ để backup.

Hai alias phân tích tùy chọn là:

- `extras/Orcasilcer setting/Printersetting.json`
- `extras/Orcasilcer setting/MulticolorPETG.json`

Tên thư mục có lỗi chính tả được giữ vì đây là đường dẫn đã tồn tại trong
repository.

## Danh sách profile

Machine:

- `Stealthchanger.json`
- `Voron Stealthchanger.json`
- `VoronStealthchanger.json`

Process:

- `0.20 Tinmory.json`
- `0.20mm ABS TPmoins.json`
- `0.20mm ABS.json`
- `0.20mm PETG Multimaterial.json`

Filament:

- ABS: `ABS Tpoimns Black.json`, `ABS Tpoimns Pink.json`,
  `ABS-Pro Tinmory Black.json`
- PETG: `PETG Bambu Basic Black.json`, `PETG Bambu Basic.json`,
  `PETG Kabber Blue.json`, `PETG Noname Antums.json`,
  `PETG Tinmory Black.json`, `PETG Tinmory.json`,
  `PETG TPoimns Black.json`, `PETG TPoimns Gray.json`,
  `PETG TPoimns Orange.json`, `PETG TPoimns Red.json`,
  `PETG TPoimns White.json`, `PETG TPoimns Yellow.json`

## Khôi phục vào OrcaSlicer

Orca user profile thường nằm tại:

```text
%APPDATA%\OrcaSlicer\user\<profile-id>\
```

Đóng OrcaSlicer trước khi phục hồi. Copy JSON machine vào `machine`, JSON
process vào `process` và JSON filament vào `filament` của đúng profile ID. Khi
có nhiều tài khoản Orca, không chọn thư mục đầu tiên một cách mù quáng; dùng
đúng profile ID mà script đồng bộ đã ghi.

Ví dụ với một profile directory đã biết:

```powershell
$profile = Join-Path $env:APPDATA 'OrcaSlicer\user\<profile-id>'
Copy-Item '.\Orca Config\Voron Stealthchanger.json' `
  (Join-Path $profile 'machine')
Copy-Item '.\Orca Config\0.20mm PETG Multimaterial.json' `
  (Join-Path $profile 'process')
Copy-Item '.\Orca Config\PETG Bambu Basic.json' `
  (Join-Path $profile 'filament')
```

Mở OrcaSlicer và kiểm tra printer, process, mapping filament và số tool trước
khi slice job production.

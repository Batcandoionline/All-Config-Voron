# Axiscope fork information / Thông tin fork Axiscope

## English

This directory preserves a maintained historical fork of Axiscope Cartographer
for a StealthChanger/KTC-Easy printer. It is **not active** in the current
configuration: ToolVision owns PF2, Cartographer owns production Z/mesh, and
the `[axiscope]` section in `calibration-probe.cfg` is commented out.

Sources:

- Upstream: <https://github.com/buddasticks/Axiscope-cartographer>
- Maintained fork: <https://github.com/IDcrazy123/Axiscope-cartographer>
- Original MIT license is preserved in `LICENSE`.

The version list below is a historical observation from Update Manager on
2026-05-16, not the current production stack:

- Axiscope `v0.0.0-13-ga34a956b-inferred`
- Cartographer Plugin `1.6.0`
- Klipper `v0.13.0-650-gca8230d5`
- Moonraker `v0.10.0-20-g90084858`
- Mainsail `v2.17.0`
- klipper-toolchanger-easy `v0.0.0-250-g5f0e5a3f-inferred`

Local fork changes recorded at that time:

- Cartographer Z probing reads `cartographer.touch.last_z_result`.
- The invalid fallback to current toolhead Z was removed to prevent false
  `2.000` Z results.
- The installer defaults to this fork for Moonraker Update Manager.

## Tiếng Việt

Thư mục này lưu fork lịch sử được bảo trì của Axiscope Cartographer cho máy
StealthChanger/KTC-Easy. Nó **không hoạt động** trong cấu hình hiện tại:
ToolVision sở hữu PF2, Cartographer đảm nhiệm Z/mesh production và section
`[axiscope]` trong `calibration-probe.cfg` đã được comment.

Nguồn:

- Upstream: <https://github.com/buddasticks/Axiscope-cartographer>
- Fork được bảo trì: <https://github.com/IDcrazy123/Axiscope-cartographer>
- License MIT gốc được giữ trong `LICENSE`.

Danh sách version bên trên là quan sát lịch sử từ Update Manager ngày
2026-05-16, không phải stack production hiện tại.

Thay đổi local được ghi nhận tại thời điểm đó:

- Probe Z Cartographer đọc `cartographer.touch.last_z_result`.
- Bỏ fallback không hợp lệ về Z hiện tại của toolhead để tránh kết quả giả
  `2.000`.
- Installer mặc định dùng fork này cho Moonraker Update Manager.

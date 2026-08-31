# UX đo Z ToolVision — bằng chứng và trạng thái triển khai

[English](toolvision-z-calibration-ux-proposal.md) | [Tiếng Việt](toolvision-z-calibration-ux-proposal.vi.md)

## Trạng thái ngày 2026-08-24

Tài liệu này ban đầu là đề xuất từ một phiên đo thật trên máy năm tool. Sau khi
đọc lại source, vertical slice được yêu cầu đã được cài đặt trong nhánh
ToolVision độc lập `codex/z-calibration-ux`, commit `2d936f3`
(`feat: make Z runs explicit and preserve history`). Tính năng **chưa được
deploy hoặc HIL trên máy production này**.

Panel All-Config đang hoạt động vẫn là luồng Setup/Calibrate cũ được gom nhóm.
Bằng chứng runtime production ghi ToolVision commit `2b3bf2c6`, version
`3.4.0-rc1`. Tài liệu phải phân biệt hai trạng thái này.

## Bằng chứng máy in tạo ra yêu cầu

Offset Z production hiện cho bản in tốt về hình thức. Hai run ToolVision 150 °C
có người giám sát ngày 2026-08-23 chỉ để chẩn đoán và không được áp dụng.
`Sai khác` bên dưới là `measured - production` chỉ để so sánh, không phải delta
để cộng.

| Tool | Z production | Z PF2 | Sai khác PF2 | Z Cartographer | Sai khác Cartographer |
| --- | ---: | ---: | ---: | ---: | ---: |
| T0 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 |
| T1 | +0.228 | +0.098 | -0.130 | +0.242 | +0.014 |
| T2 | -0.295 | -0.384 | -0.089 | -0.256 | +0.039 |
| T3 | -0.268 | -0.154 | +0.114 | -0.160 | +0.108 |
| T4 | -0.014 | +0.078 | +0.092 | +0.102 | +0.116 |

- T0 return drift của PF2: `+0.028 mm`.
- T0 return drift của Cartographer Touch: `-0.008 mm`.
- Một record PF2 cũ có T1 `+0.092`, T2 `-0.376`, T3 `-0.054`, T4
  `+0.090 mm`; T3 đổi nhiều nhất giữa hai quan sát PF2.
- Run Cartographer ghi đè `results.json` của PF2, khiến phải khôi phục run đầu từ
  console.
- Source tính Z bằng `raw_contact_z(tool) - raw_contact_z(reference)`. Kết quả
  là giá trị absolute ứng viên tương đối T0, không phải correction cộng thêm.

Một run mỗi method không đủ thay baseline đã thử nghiệm in, đặc biệt khi sai
khác T3/T4 vượt 0.10 mm. Offset production vẫn giữ nguyên.

## Vấn đề thao tác đã quan sát

1. Setup và calibration thường xuyên bị gom chung. Teach cơ chế Z khác làm đổi
   default của nút `Z only` chung mà nhãn method cuối chưa đủ nổi bật.
2. Progress ToolVision, dòng từng tool, macro heater/tool và report lặp làm
   console khó đọc.
3. Chỉ có latest result khiến mất ngay kết quả method trước đó.
4. Từ “offset” có thể bị hiểu nhầm là delta phải cộng vào production.

## Implementation xác nhận từ source tại `2d936f3`

| Hành vi yêu cầu | Bằng chứng trong source/test | Trạng thái |
| --- | --- | --- |
| Method tường minh trong mỗi action Z | UI gọi `MODE=Z METHOD=SWITCH` hoặc `METHOD=CARTOGRAPHER_TOUCH` | Đã cài trên nhánh |
| Tách đo thường xuyên và setup | Prompt chính có phép đo theo method; teach nằm trong Advanced Setup | Đã cài trên nhánh |
| Lặp method trước chuyển động | Confirmation có method, reference, tool list, nhiệt độ, readiness và report-only | Đã cài trên nhánh |
| Progress ToolVision ít log | `VERBOSITY=QUIET|NORMAL|DEBUG`; alias `QUIET=1`; UI dùng quiet | Đã cài trên nhánh |
| Giữ mọi run success | JSON exclusive-create có method, latest atomic, suffix khi trùng | Đã cài trên nhánh |
| Retention hữu hạn | Cố định 20 record; `TOOL_VISION_HISTORY LIMIT=` đọc history | Đã cài trên nhánh |
| Semantics rõ | `applied=false`, `configuration_changed=false`, `NOT APPLIED` | Đã cài trên nhánh |
| Tương thích ngược | Z chung không `METHOD` dùng default; explicit method một run không ghi lại default | Đã cài trên nhánh |

File runtime liên quan là `tool_vision.cfg`, `klippy/extras/tool_vision.py` và
`tool_vision_state.py`. Regression test bao phủ chọn method tường minh, method/
mode sai, parse quiet, số message ToolVision tối đa trong fake run năm tool có
nhiệt, collision/retention history, result có method và report/history sau
Klipper restart.

`docs/TESTING.md` của ToolVision ghi 123 test pass và branch coverage tổng 77%,
nhưng phân loại rõ đây là evidence L0–L2/fake. Mainsail, simulator và HIL chưa
chạy; repository không được deploy production cho thay đổi này.

## Giới hạn còn lại

- Quiet chỉ giảm message do ToolVision phát. Nó không chặn output Klipper,
  heater, KTC hoặc macro khác; warning/error luôn được giữ.
- Retention cố định 20, chưa cho người dùng cấu hình.
- So sánh hai run, support bundle, run UUID/phase/duration và evidence raw sample
  phong phú vẫn là planned.
- Rủi ro safety ToolVision còn mở: HTTP đồng bộ trong Klippy, bằng chứng
  preflight/recovery toàn run chưa đủ và chưa HIL đa phần cứng.
- Nhánh vẫn report-only và không áp offset production.

## Gate nghiệm thu trước khi deploy lên máy này

1. Tạo backup tương ứng cho All-Config, commit ToolVision, state và result.
2. Xác nhận commit tính năng đã qua security gate và quyết định cách đưa vào
   nhánh Moonraker updater; không trỏ production vào working branch tùy ý.
3. Review custom `result_file`. History mới phải đi tới
   `Generated-Data/ToolVision/tool-vision-history/` và được bảo vệ khỏi deploy.
4. Chỉ deploy khi idle; kiểm tra service/API/Klipper version không chuyển động.
5. Mở Mainsail, xác nhận chỉ một macro `TOOL_VISION` hiện, Advanced Setup tách
   riêng và confirmation có tên method.
6. Chạy PF2 lạnh hoặc nhiệt được duyệt có người giám sát; chỉ chạy Cartographer
   Touch sau khi xác nhận model/path. Kiểm tra tool/heater/trạng thái cuối.
7. Xác nhận hai run method khác nhau tồn tại thành hai history file, latest vẫn
   tương thích và không file offset/config production nào đổi.
8. Lặp cùng method trước khi kết luận calibration.

Cho đến khi gate này đạt, đây là tính năng đã cài ở nhánh phát triển, không phải
khả năng production của máy.

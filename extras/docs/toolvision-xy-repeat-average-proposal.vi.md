# Đề xuất ToolVision: đo XY lặp trong một lần pickup

## Cơ sở review

Đề xuất này dựa trên Git bundle ToolVision đã retired tại commit `374d5e2`
(`main`, 2026-08-29) và phép đo kTAMV thực tế ngày 2026-08-31. Đây chỉ là thiết
kế cho repository ToolVision độc lập; ToolVision không được cài lại vào máy.

Source hiện tại đã có batch nhiều attempt và lấy median giữa các attempt hợp lệ,
nhưng `_measure_xy()` chỉ center một lần/tool trong mỗi attempt. Candidate hiện
là tọa độ tương đối giữa center của tool và T0; production vẫn report-only.

## Thay đổi đề xuất

1. Thêm `xy_samples_per_tool` mặc định `3` và
   `max_xy_sample_spread_mm` mặc định `0.12`.
2. Trong `_measure_xy()`, trước **mỗi** sample phải gọi lại
   `_move_to_station("camera", tool_number)`. Không center liên tiếp từ vị trí
   đã center vì sample 2/3 khi đó chỉ đo số 0 giả.
3. Lưu mỗi `raw_center_position`, residual so với station/reference và evidence
   detector. Tính mean X/Y, min/max/range từng trục; fail closed khi thiếu sample
   hoặc range vượt giới hạn.
4. Báo riêng:
   - `mean_residual_xy`: correction còn lại khi offset KTC hiện tại đang nạp;
   - `configured_xy`: snapshot offset lúc bắt đầu;
   - `candidate_xy = configured_xy + mean_residual_xy`;
   - raw samples và spread, không chỉ một center cuối.
5. Giữ median giữa nhiều full attempts/pickup cycles làm lớp thống kê ngoài.
   Mean ba sample trong một pickup đo detector/centering repeatability; median
   giữa ít nhất ba pickup cycles đo repeatability của dock. Không trộn hai loại.
6. Dùng lại reference-return T0 sau batch, nhưng bắt buộc threshold thay vì chỉ
   report. HIL máy này thấy T0 return correction tới `Y+0.072 mm`, nên candidate
   phải bị gắn `REVIEW_PICKUP_REPEATABILITY` khi drift vượt ngưỡng cấu hình.
7. Thêm hook ánh sáng trước camera sample. Cấu hình máy này chỉ tắt `Tn_LED`;
   không được giả định hay điều khiển vòng WCMCU WS2812B/ESP32-C3 độc lập 5%.
8. Nếu bổ sung apply, giữ lệnh riêng `TOOL_VISION_APPLY_LAST_XY` và fail closed:
   active/detected tool phải khớp, fingerprint/configured snapshot không đổi,
   batch PASS, tool không phải T0, spread/drift đạt, người dùng xác nhận rõ.
   Stage bằng `SET_TOOL_PARAMETER`/`SAVE_TOOL_PARAMETER`; yêu cầu
   `SAVE_CONFIG` riêng sau khi review tất cả tool. Không auto-apply cuối batch.

## Vị trí sửa trong source

- `klippy/extras/tool_vision.py`: `_measure_xy()`,
  `_measure_reference_return_xy()`, `_aggregate_batch_attempts()`,
  `_production_comparison()` và status/report.
- `klippy/extras/tool_vision_state.py`: schema raw samples, mean residual,
  candidate, within-pickup spread và between-pickup statistic.
- `tool_vision.cfg`: hai option sample/spread, lighting hook và apply guard.
- `tests/test_klipper_logic.py`, `test_klipper_integration.py`,
  `test_results.py`, `test_contracts.py`: test reset origin từng sample, công
  thức dấu, không đổi Z, mismatch tool, stale fingerprint, spread/drift fail và
  không gọi apply ngầm.

## Acceptance HIL đề xuất

- Camera Z40, T0 làm reference X/Y zero, heater target 0, LED tool tắt.
- Mỗi T1–T4: ba raw sample đủ, spread mỗi trục không quá `0.12 mm`.
- Ít nhất ba pickup cycles/tool; lưu riêng mean mỗi pickup và median liên pickup.
- T0 return drift nằm trong threshold đã khai báo; nếu không, kết quả chỉ được
  báo cáo và không cho apply.
- Sau apply thử nghiệm, đo verification report-only phải về gần zero theo độ
  phân giải camera; Z offset phải byte-for-byte không đổi.

## Bài học từ phiên kTAMV

- Bộ lọc calibration không được mutate input trước khi kiểm tra tỷ lệ sample giữ
  lại; mọi list MPP/space/camera phải xóa cùng index.
- API kết quả cần raw samples, mean, spread và tool number để macro không lấy
  nhầm kết quả cũ.
- Detector ổn định trong một pickup không chứng minh dock repeatable. T0 return
  drift là gate bắt buộc trước khi coi candidate là production-ready.

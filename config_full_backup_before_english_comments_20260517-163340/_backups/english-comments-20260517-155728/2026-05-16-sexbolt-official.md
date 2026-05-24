# Nhat ky chinh sua - 2026-05-16

## Muc tieu hien tai

Tam dung huong Axiscope Cartographer de quay ve workflow chinh thuc cua StealthChanger/KTC-Easy dung SexBolt/SexBall probe va `tools_calibrate`.

## Backup da tao

Thu muc backup truoc khi sua:

`config/_backups/sexbolt-official-20260516-210825/`

Backup rieng cho lan chuyen SexBolt sang M1-STOP/PF4:

`config/_backups/sexbolt-m1-stop-20260517-155108/`

Da backup cac file:

- `Printer-Setup/probe-mesh.cfg`
- `toolchanger/toolchanger-config.cfg`
- `Printer-Setup/calibration.cfg`

## Cac thay doi cau hinh hien tai

- Comment toan bo block `[axiscope]` trong `Printer-Setup/probe-mesh.cfg`.
- Bat lai section `[tools_calibrate]` trong `toolchanger/toolchanger-config.cfg`.
- Giu cau hinh SexBolt/SexBall probe:
  - `pin: ^PF4` tren M1-STOP cua Manta M8P V2.0
  - `trigger_to_bottom_z: 0.9`
  - `samples: 5`
  - `samples_result: median`
  - `probe: probe`
- Cap nhat toa do SexBolt/SexBall:
  - `_CALIBRATION_SWITCH.variable_x: 257`
  - `_CALIBRATION_SWITCH.variable_y: 327`
  - `_CALIBRATION_SWITCH.variable_z: 60`
  - `Z55` la cao do cham/dinh ball tham khao, khong dung lam safe approach Z.
- Cap nhat header guide trong `Printer-Setup/calibration.cfg` sang workflow XYZ offset bang `CALIBRATE_ALL_OFFSETS`.
- Them macro public `CHECK_OFFSETS` goi lai `_CHECK_OFFSETS` de dung voi huong dan hien co.

## Tom tat cac viec da lam truoc do trong phien lam viec

- Doc va phan tich `Axiscope-cartographer-main/klippy/extras/axiscope.py`.
- Xac dinh loi Axiscope Cartographer ban dau doc sai ket qua touch probe, tra ve `2.000` thay vi `cartographer.touch.last_z_result`.
- Sua `axiscope.py` de doc `cartographer.touch.last_z_result` va bo fallback sai ve current toolhead Z.
- Test voi log may in: Axiscope da tra ve duoc contact Z that, vi du T1/T2/T3/T4 quanh `0.022`, `-0.114`, `-0.314`, `-0.324`.
- So sanh voi offset first-layer theo Ellis3DP va ket luan Cartographer touch value chua khop truc tiep voi offset in dep theo first-layer.
- Tao repo GitHub `https://github.com/Batcandoionline/Axiscope-cartographer` de luu fork Axiscope Cartographer, co `README.md`, `FORK_INFO.md`, installer/uninstaller va cau hinh Moonraker Update Manager.
- Sau do quyet dinh tam dung huong Axiscope va quay ve workflow chinh thuc cua StealthChanger bang SexBolt/SexBall.

## Workflow khuyen nghi sau khi nap cau hinh

1. Restart Klipper.
2. Chay:

   ```gcode
   G28
   QUAD_GANTRY_LEVEL
   G28 Z
   CALIBRATE_ALL_OFFSETS
   ```

3. Sau khi macro luu offset bang `SAVE_TOOL_PARAMETER`, chay `FIRMWARE_RESTART`.
4. Kiem tra:

   ```gcode
   CHECK_OFFSETS
   ```

## Luu y

- Khong bat `[axiscope]` dong thoi voi `[tools_calibrate]` vi ca hai cung dung helper `probe_multi_axis`.
- Neu SexBolt/SexBall khong trigger dung, kiem tra lai pin `^PF4` bang `QUERY_ENDSTOPS`; neu bi nguoc trang thai thi doi thanh `^!PF4`.
- Neu Z offset SexBolt cho ra khac first-layer Ellis, dung Ellis/first-layer de xac nhan lan cuoi.

## Cap nhat 2026-05-17 - Chuyen wiring SexBolt sang M1-STOP/PF4

- Theo pinout Manta M8P V2.0: `M1-STOP = PF4`, `M3-STOP = PF2`, `M5-STOP = PF0`.
- Giu `stepper_x.endstop_pin: PF0` vi do la M5-STOP, khong trung voi M1-STOP.
- Doi `[tools_calibrate] pin` tu `^PF2` sang `^PF4`.
- Doi toa do macro `CALIBRATE_MOVE_OVER_PROBE`/`_CALIBRATION_SWITCH` sang tam ball moi `X257 Y327`.
- Giu safe Z la `60`; `Z55` chi la moc cham/dinh ball de tham khao khi do lai `trigger_to_bottom_z`.

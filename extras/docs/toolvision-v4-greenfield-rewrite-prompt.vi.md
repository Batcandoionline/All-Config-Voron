# Prompt điều phối: viết lại ToolVision từ đầu dựa trên bằng chứng kTAMV

Sao chép toàn bộ nội dung bên dưới vào một task Codex mới của project
`Tool-Vision`. Chọn model `gpt-5.6-luna`, reasoning `medium` nếu cần tiết kiệm
quota; không dùng nhánh sửa thử nghiệm trước đây làm base.

---

Bạn là lead engineer chịu trách nhiệm **tái cấu trúc và viết lại ToolVision từ
đầu**. Đây là greenfield rewrite có kiểm soát, không phải refactor từng hàm,
không phải vá tiếp mã v3, và không phải mở rộng nhánh
`codex/independent-pickup-evidence`.

Kết quả bắt buộc là một codebase ToolVision mới, nhất quán từ kiến trúc, mã
nguồn, Klipper extension, host service, state schema, installer, tests đến toàn
bộ tài liệu Markdown. Dùng code cũ chỉ như tài liệu khảo sát hành vi; không giữ
kiến trúc cũ chỉ vì đã tồn tại.

## 1. Cách bắt đầu bắt buộc

1. Làm việc trong project Git `D:/Desktop/Tool-Vision` nhưng tạo **Codex
   worktree sạch từ `origin/main`**. Không dùng working tree đang dirty, không
   base trên `codex/independent-pickup-evidence`, không merge/cherry-pick nhánh
   đó.
2. Tạo branch mới `rewrite/toolvision-v4-greenfield` từ đúng `origin/main`.
3. Đọc đầy đủ `AGENTS.md` và **mọi Markdown first-party đang tracked** (không
   chỉ README hoặc các file được link từ README) để trích xuất invariant, sign
   convention, failure behavior và bằng chứng lịch sử. Dùng
   `git ls-files '*.md'` làm manifest kiểm kê; third-party README/license chỉ
   đọc để hiểu provenance và không được viết lại sai tác giả. Sau bước audit,
   coi code v3 là read-only reference.
4. Tạo backup local theo quy tắc repo, kiểm tra `git status`, remote, revision và
   baseline tests. Không xoá hoặc ghi đè thay đổi chưa biết của người dùng.
5. Trước khi viết production code, tạo:
   - `docs/rewrite/REQUIREMENTS.md`;
   - `docs/rewrite/ARCHITECTURE.md`;
   - `docs/rewrite/FILE_DISPOSITION.md`;
   - `docs/rewrite/TRACEABILITY.md`;
   - một ADR chốt greenfield rewrite và ranh giới v3/v4.
6. `FILE_DISPOSITION.md` phải liệt kê **mọi file tracked hiện tại**, đặc biệt mọi
   `.md`, với một trong các trạng thái: `REWRITE`, `REPLACE`, `ARCHIVE`,
   `REMOVE`, hoặc `THIRD_PARTY_REFERENCE`. Không được để file cũ sống sót mà
   không có quyết định rõ.

## 2. Nguồn sự thật của bản viết lại

Thiết kế v4 phải xuất phát từ bằng chứng HIL kTAMV vừa thực hiện, không xuất
phát từ cách chia lớp hiện tại của ToolVision.

Đọc trực tiếp các file:

- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/experiments/ktamv-xy-independent-cycles-20260831.csv`
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/experiments/ktamv-xy-independent-cycles-20260831.md`
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/toolvision-xy-repeat-average-proposal.en.md`
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/toolvision-xy-repeat-average-proposal.vi.md`
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/ktamv-usage-comparison.en.md`
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/ktamv-usage-comparison.vi.md`

Bằng chứng phải được copy thành fixture có provenance/checksum trong repo mới,
không sửa raw values:

```text
Cycle 1:
T0 ( 0.000,  0.000)
T1 (+0.004, -0.078)
T2 (+0.006, -0.130)
T3 (+0.029, -0.073)
T4 (+0.004, -0.078)

Cycle 2:
T0 (+0.001, -0.026)
T1 (+0.004, -0.078)
T2 (+0.004, -0.078)
T3 (+0.005, -0.104)
T4 (+0.004, -0.078)

Cycle 3:
T0 (+0.001, -0.026)
T1 (+0.004, -0.078)
T2 (+0.005, -0.104)
T3 (+0.004, -0.078)
T4 (+0.003, -0.052)
```

Observed calibration context:

- camera scale `0.0570 mm/pixel`;
- calibration relative standard deviation `6.3%`;
- camera origin quan sát `[168.716, 18.451]` nhưng đây là evidence, **không phải
  constant để đưa vào code/config mặc định**;
- operator cho phép Z an toàn `40 mm` cho phiên thử này, nhưng v4 phải nhận vị
  trí từ lệnh/runtime, không hard-code `40`;
- active tool LED được tắt;
- ánh sáng mặc định do camera cung cấp là đủ;
- ESP32-C3 + WCMCU WS2812B 8 LED là giải pháp tạm độc lập, không thuộc
  ToolVision, không nối Klipper, không được điều khiển/đồng bộ/hiệu chuẩn/giả
  định trong code;
- heater targets bằng 0 trong HIL này;
- không offset nào được ghi trong phiên evidence mới.

Interpretation bắt buộc:

- Ba lần center liên tiếp trong cùng một pickup chỉ đánh giá detector/centering
  repeatability và có thể tạo spread bằng 0 giả.
- Repeatability cần đánh giá bằng ba **chu kỳ pickup độc lập**, mỗi chu kỳ đi
  qua T0→T1→T2→T3→T4. Fixture HIL hiện có chỉ ghi một mẫu T0 đầu mỗi cycle;
  không được mô tả nó như đã có mẫu T0 cuối cycle.
- Bản v4 phải nâng protocol thành T0→T1→T2→T3→T4→T0 để đo
  reference-return drift trong chính mỗi cycle. Đây là **yêu cầu thiết kế mới
  suy ra từ bằng chứng**, chưa phải kết quả HIL đã xác nhận; giữ nhãn
  `Planned/Requires HIL` cho đến khi chạy lại trên máy.
- T3 có outlier X ở cycle 1: mean `+0.012667`, median `+0.005`. Hệ thống phải
  lưu và hiển thị cả raw/mean/median; không âm thầm loại outlier.
- Mean là candidate người dùng yêu cầu để đối chiếu/áp dụng, nhưng apply phải bị
  chặn nếu gate outlier, drift, fingerprint hoặc safety không đạt. Median là
  robust comparison/recommendation, không được che mean.

## 3. Mục tiêu chức năng v4

### 3.1 XY bằng camera

- T0 mặc định là reference nhưng phải hỗ trợ `REFERENCE_TOOL=` và snapshot
  configured offsets; không phụ thuộc reference có configured XY bằng 0.
- Tool list phải lấy từ toolchanger/runtime, không hard-code đúng năm tool.
  HIL/fixture chuẩn vẫn dùng T0–T4.
- Camera source được chọn rõ hoặc discovery qua Moonraker; không đoán camera khi
  có nhiều lựa chọn.
- Giữ native resolution và metadata rotation/flip. Host process sở hữu capture,
  detector và transform; Klippy không import OpenCV/NumPy.
- Calibration phải dùng nhiều chuyển động đã biết, fit transform pixel→machine,
  kiểm tra rank, conditioning, residual, holdout, uncertainty và frozen frame.
- Detector phải xử lý ambiguity, glare, blur, saturation, nhiều vật thể và ảnh
  cache/frozen; không chọn theo list order.
- Sign invariant:

  ```text
  residual_xy(tool, cycle) = raw_center(tool, cycle)
                           - raw_center(reference, cycle)
  candidate_xy(tool) = configured_xy_snapshot(tool)
                     + accepted_estimator(residual_xy)
  ```

- Không trộn G-code position với raw machine position mà không ghi rõ transform
  và configured offsets đang nạp.

### 3.2 Z bằng Cartographer hoặc công tắc

- Có interface `ZProvider` rõ ràng với hai implementation:
  `CartographerProvider` và `PhysicalSwitchProvider`.
- Dùng thuật ngữ/API ổn định `physical-switch`; không nhập nhằng với
  SexBolt/SexBall hay `CALIBRATE_ALL_OFFSETS`.
- Người dùng chọn method tường minh mỗi run; không tự chọn chỉ vì phát hiện phần
  cứng.
- Vị trí station/probe/switch được teach/capture bằng lệnh runtime; không có
  X/Y/Z station cố định trong source hoặc config mẫu.
- Provider trả raw trigger/contact và evidence công khai. Không đọc private
  state/log để bịa raw samples.
- Sign invariant:

  ```text
  residual_z(tool, cycle) = raw_contact_z(tool, cycle)
                          - raw_contact_z(reference, cycle)
  candidate_z(tool) = configured_z_snapshot(tool)
                    + accepted_estimator(residual_z)
  ```

- XY apply không được thay đổi Z; Z apply không được thay đổi XY. Viết test
  byte-for-byte cho invariant này.
- Cartographer và switch có preflight, trigger freshness, travel envelope,
  retract, timeout và cleanup riêng nhưng trả cùng domain contract.

### 3.3 Lệnh teach vị trí động — không hard-code

Thiết kế public command tối thiểu tương đương:

```gcode
TOOL_VISION_TEACH_CAMERA_POSITION [SAFE_Z=<current-or-explicit>]
TOOL_VISION_TEACH_Z_POSITION METHOD=CARTOGRAPHER|SWITCH [SAFE_Z=<...>]
TOOL_VISION_SHOW_POSITIONS
```

Yêu cầu:

- Teach command capture current raw machine XYZ, homed axes, active/detected
  tool, kinematic limits, configured-offset snapshot, timestamp và revision.
- Mỗi station có fingerprint; thay đổi camera identity/resolution/rotation,
  tool layout, axis limits hoặc configured offsets phải làm evidence cũ stale.
- Ngay trước **mọi sample**, Klippy phải gọi provider/lệnh tương đương
  `GET_POSITION`, xác nhận pose hiện tại, nâng Z tại current XY trước khi travel,
  rồi mới đi tới station đã teach.
- Lưu cả pre-sample pose và station revision vào raw evidence.
- Không đưa `X170 Y20 Z40`, camera origin HIL hoặc dock coordinates của máy hiện
  tại thành default production.
- Operator chịu trách nhiệm xác nhận đường thẳng vertical/travel không va chạm;
  software kiểm tra mọi limit có thể biết và fail closed.

### 3.4 Chu kỳ đo độc lập

Public workflow phải hỗ trợ:

```gcode
TOOL_VISION_MEASURE_XY CYCLES=3 ESTIMATOR=MEAN
TOOL_VISION_MEASURE_Z METHOD=CARTOGRAPHER|SWITCH CYCLES=3 ESTIMATOR=MEAN
TOOL_VISION_MEASURE_XYZ METHOD=CARTOGRAPHER|SWITCH CYCLES=3 ESTIMATOR=MEAN
```

Mỗi outer cycle:

1. Xác nhận printer idle, không paused/printing, homed, toolchanger ready.
2. Đảm bảo reference tool được pickup thật; cycle đầu không được gắn nhãn
   independent nếu T0 chưa trải qua pickup.
3. Đo T0 start reference.
4. Lần lượt pickup và đo từng tool discovered/selected đúng một lần.
5. Pickup lại T0 và đo reference-return drift.
6. Cleanup heater/tool/G-code state, persist immutable attempt rồi mới bắt đầu
   cycle kế tiếp.

Không được biến `CYCLES=3` thành ba detector calls tại cùng một pickup. Nếu có
multi-frame detector burst, phải gọi nó là `frame_observations`, không gọi là
pickup samples.

Lưu hai tầng statistic riêng:

- inner detection: frame count, center confidence, frame spread, ambiguity;
- outer pickup: raw residual mỗi cycle, mean, median, min, max, range, sample
  standard deviation, MAD và T0 return drift.

Không tự xoá outlier. Chỉ classify `PASS`, `REVIEW_REQUIRED`, `INVALID` dựa trên
threshold do user config hoặc corpus/HIL cung cấp. Threshold unset phải được
hiển thị là unset, không suy ra universal value từ một máy.

## 4. Apply offset: tách khỏi measurement

Mặc định toàn bộ measurement là `report-only`, `applied=false`.

Có thể implement lệnh riêng:

```gcode
TOOL_VISION_APPLY_LAST AXES=XY|Z|XYZ ESTIMATOR=MEAN|MEDIAN CONFIRM=<token>
```

Lệnh apply phải fail closed nếu bất kỳ điều kiện nào sai:

- session không đủ ba cycle independent;
- result `INVALID` hoặc `REVIEW_REQUIRED` chưa được operator override theo
  contract có audit;
- T0 drift/gate, detector ambiguity, provider gate hoặc cleanup không đạt;
- configured-offset snapshot/fingerprint khác lúc đo;
- station/camera/tool layout đã stale;
- active/detected tool state incoherent;
- result cũ, thiếu raw rows hoặc schema không hợp lệ;
- thiếu backup marker hoặc explicit confirmation token;
- apply có nguy cơ sửa trục ngoài `AXES=`.

Apply chỉ stage candidate thông qua public KTC/Klipper contract đã được test.
Không gọi `SAVE_CONFIG` ngầm. Sau khi stage phải in diff old→candidate và yêu
cầu operator review; persistence là lệnh riêng. Có rollback artifact và
post-apply verification report-only. Không apply T0 reference.

## 5. Kiến trúc mới — không giữ monolith v3

Thiết kế package mới theo domain boundaries; tên cụ thể có thể điều chỉnh trong
ADR nhưng phải có các lớp trách nhiệm sau:

```text
toolvision/
  domain/        # vectors, signs, sessions, cycles, statistics, verdicts
  protocol/      # versioned request/response/evidence schemas
  vision/        # capture, detector, calibration, transform, quality
  persistence/   # atomic state/result/history, migration, quarantine
  service/       # loopback API, jobs, health, bounded I/O
  klipper/       # thin adapters/orchestrator, motion, tools, heaters, cleanup
  z/             # provider interface + cartographer + switch
  cli_or_macros/ # stable public commands and reports
```

Ràng buộc:

- Domain/statistics/schema phải là pure Python, deterministic và testable.
- Host service tuyệt đối không được phát motion G-code.
- Klippy giữ motion/toolchange/homing/probe/heater cleanup; không chạy computer
  vision và không blocking network trong reactor.
- HTTP/API loopback-only, body/frame bounded, timeout/cancel rõ, redaction URL
  credential và không lộ camera URL/IP trong result công khai.
- Dùng async job/session contract; command trả session ID nhanh và status/history
  là completion evidence.
- State/result write atomic: temp file trong cùng filesystem, fsync/replace,
  bounded backup/history, schema migration và quarantine file hỏng.
- Không import production code từ `Axiscope/` hoặc `kTAMV/`. Nếu giữ source
  tham chiếu, chuyển thành `third_party` read-only kèm license/checksum và không
  nằm trên runtime path; ưu tiên bỏ vendored code và chỉ giữ provenance/link.
- Không copy nguyên source upstream khi chưa kiểm tra license.

## 6. Safety và recovery bắt buộc

- Reject printing, paused, shutdown, unhomed, busy job, toolchanger unready hoặc
  active/detected mismatch trước motion/heat.
- Preflight toàn bộ known target và motion envelope trước khi bắt đầu cycle.
- Travel order: raise Z at current XY → travel XY → approach Z.
- Tool/heater ownership rõ; cleanup heater target độc lập với tool recovery.
- Mọi failure giữ cả primary error và cleanup errors; không báo success nếu
  cleanup không an toàn.
- Không blind-select tool khi toolchanger state unknown. Recovery hook phải
  explicit, bounded, verify lại ready/active/detected.
- Detection/camera/network failure giữa correction phải dừng correction, recover
  an toàn và không persist result hoàn chỉnh.
- MCU/reactor/wait failure không được giả thành recoverable state mismatch.
- Không dùng `CALIBRATE_ALL_OFFSETS`; đó là KTC/tools_calibrate SexBolt/SexBall
  workflow riêng. ToolVision v4 có command riêng cho camera XY và provider Z.
- Không cài/deploy lên máy production trong task rewrite này.

## 7. Data model và evidence schema

Schema version mới phải lưu tối thiểu:

- software version, Git commit, schema version;
- session/job ID, attempt/cycle/sample/frame ID;
- mode/axes/provider/reference/tool set/estimator;
- configured XYZ snapshot và fingerprint;
- dynamic pre-sample pose, taught station revision, limits/homing/tool state;
- camera identity/profile/resolution/rotation/flip/exposure/focus khi có;
- `lighting_mode=camera_default`; generic readiness hook result;
- raw detector observations, transform/correction/uncertainty;
- raw XY center và raw Z contact, không chỉ aggregate;
- per-cycle residual, T0 start/return drift;
- mean/median/min/max/range/sample-SD/MAD;
- thresholds đã dùng hoặc `null`;
- verdict/reason codes, primary error, cleanup errors;
- candidate, configured comparison, `applied=false|true`, apply audit record;
- start/end timestamps và final machine-state evidence.

Schema phải có JSON Schema hoặc equivalent contract, round-trip tests, migration
tests và reject unknown/incompatible major version.

## 8. Viết lại toàn bộ Markdown

Không chỉ cập nhật README. Mọi Markdown first-party phải được xử lý theo
`FILE_DISPOSITION.md`.

Tạo bộ tài liệu v4 nhất quán:

- `AGENTS.md` — quy tắc cho agent và source-of-truth map;
- `README.md` và `README.vi.md` — mục tiêu, trạng thái, quick start, cảnh báo;
- `docs/ARCHITECTURE.md` — domain/process/motion/data boundaries;
- `docs/REQUIREMENTS.md` — functional/non-functional requirements;
- `docs/COMMAND_REFERENCE.md` — từng macro, params, motion/heat/apply effect;
- `docs/CONFIG_REFERENCE.md` — options, default, units, source/evidence;
- `docs/XY_CAMERA_WORKFLOW.md`;
- `docs/Z_PROVIDER_WORKFLOW.md`;
- `docs/OPERATOR_GUIDE.vi.md` — hướng dẫn Việt đầy đủ;
- `docs/SAFETY.md`, `RISK_REGISTER.md`;
- `docs/DATA_AND_STORAGE.md`, schema/migration/backup/restore;
- `docs/DETECTION_DESIGN.md`;
- `docs/API.md`;
- `docs/INSTALL.md`, `OPERATIONS.md`, `UNINSTALL.md`, `UPDATE.md`;
- `docs/DEVELOPMENT.md`, `TESTING.md`, `COMPATIBILITY.md`, `RELEASE.md`;
- `docs/HIL_PROTOCOL.md` và evidence template;
- ADR index và ADR mới cho sign, process boundary, dynamic positions,
  independent cycles, Z providers, report/apply separation, persistence.

Đối với ADR/change-plan v3:

- Không sửa lịch sử để giả thành v4.
- Move vào `docs/archive/v3/` hoặc thay bằng manifest archive rõ ràng.
- Mỗi file lịch sử phải có disposition; không để link cũ trở thành hướng dẫn
  active.
- Third-party README/license không được viết lại sai tác giả; remove vendored
  subtree hoặc giữ immutable với provenance.
- Chạy local-link checker; không còn broken link, tên macro/version/schema/service
  mâu thuẫn.
- Mọi claim phải gắn `Implemented`, `Observed`, `Planned` hoặc `Unknown`. Không
  biến fixture offline thành HIL support claim.

## 9. Test strategy bắt buộc

Viết test trước hoặc song song từng vertical slice. Không chỉ port test cũ.

### Unit/domain

- dấu XY/Z với positive/negative fixtures;
- candidate = snapshot + residual;
- ba outer cycle độc lập;
- inner frame observations không bị đếm thành pickup cycle;
- mean/median divergence, T3 outlier, range/SD/MAD;
- T0 start/return drift;
- duplicate/missing cycle/sample/tool;
- arbitrary discovered tool set và reference khác T0;
- schema validate/migrate/quarantine/round-trip;
- XY apply không đổi Z và ngược lại.

### Vision/component

- native resolution, rotation/flip;
- zero/one/multiple camera discovery;
- dark/glare/blur/saturation/ambiguous/distractor/no-nozzle;
- frozen/cached frame sau commanded move;
- transform rank/condition/residual/holdout/uncertainty;
- HTTP timeout, oversized/malformed body/frame, restart/cancel/concurrency.

### Klipper simulator/integration

- load extension bằng config thật;
- homed/unhomed/printing/paused/shutdown/busy;
- dynamic teach position và provider được gọi trước mọi sample;
- assert không production path nào dùng hard-coded camera/probe/switch XYZ;
- toolchanger ready/unknown/mismatch/toolchange fail;
- motion limit, negative axis minimum, safe-Z order;
- heater timeout/cleanup fail;
- camera loss giữa move;
- Cartographer success/window failure/no public raw;
- switch open/stuck/no-trigger/tolerance/retract;
- persistence disk full/permission/restart giữa job;
- original-tool restore và primary+cleanup evidence;
- apply stale fingerprint/confirmation/axis isolation/rollback.

### Installer/security/docs

- fresh install, idempotent update, interrupted install rollback, uninstall
  restore;
- systemd/Moonraker/config include/version/path consistency;
- loopback-only API, URL credential redaction, secrets scan, dependency audit;
- Bash syntax, compileall, Ruff, coverage branch, Markdown links;
- no automatic `SAVE_CONFIG`, no implicit offset mutation, no ESP32/WS2812
  runtime dependency.

Fixture HIL 2026-08-31 phải có deterministic test xác nhận đúng mean/median và
T3 review behavior. Không được thay raw data để làm test pass.

## 10. HIL và release policy

Task rewrite chỉ tạo code + offline/simulator evidence. Không SSH, không deploy,
không move máy.

Sau merge mới lập canary/HIL có người giám sát:

1. backup config/state/result;
2. cold report-only XY bằng camera default light;
3. ba full T0→T4→T0 cycle;
4. Z Cartographer và switch ở controlled comparable conditions;
5. fault injection có checkpoint/STOP;
6. post-run verify tool, heaters, homing, state, history, `applied=false`;
7. chỉ sau evidence review mới thử explicit apply trên canary.

Không tag stable, không merge main, không claim production support chỉ vì unit
tests pass.

## 11. Quy trình triển khai code trong task

Làm theo các checkpoint, mỗi checkpoint có commit tiếng Anh và push branch:

1. `docs: define ToolVision v4 greenfield requirements`
2. `feat: add versioned domain and evidence schemas`
3. `feat: add camera calibration and detection service`
4. `feat: add dynamic station and safe-position contracts`
5. `feat: add independent pickup-cycle orchestrator`
6. `feat: add cartographer and switch z providers`
7. `feat: add guarded offset apply transaction`
8. `feat: add atomic persistence and job api`
9. `feat: replace installer and public macro surface`
10. `test: complete simulator and failure-injection gates`
11. `docs: replace ToolVision documentation for v4`
12. `chore: remove or archive all v3 runtime and stale docs`

Sau mỗi checkpoint:

- chạy focused tests;
- `git diff --check`;
- inspect staged diff;
- update traceability/risk/changelog;
- push branch, không force.

Không dùng một commit khổng lồ. Không để code v3 và v4 cùng active path. Khi v4
đạt parity, remove v3 production modules trong branch rewrite; Git history là
rollback, không cần giữ dead code trong runtime.

## 12. Definition of done

Chỉ báo hoàn tất khi:

- production code là implementation mới, không import/route qua v3 hoặc nhánh
  thử nghiệm;
- mọi tracked file cũ có disposition và không còn stale active docs;
- toàn bộ Markdown first-party đã rewrite/replace/archive có chủ đích;
- XY camera và Z Cartographer/switch chạy qua interface mới;
- camera/Z positions được teach và xác nhận động bằng command, không hard-code;
- ba cycle independent được model/test đúng;
- raw/mean/median/outlier/T0 drift hiển thị đầy đủ;
- report-only default và apply transaction explicit đã được test;
- không dependency/control ESP32-C3/WS2812B;
- full unit/component/integration/fault/security/docs/install gates pass;
- coverage các nhánh safety/recovery không giảm so với baseline và có báo cáo;
- branch `rewrite/toolvision-v4-greenfield` được push;
- tạo PR nhưng không merge;
- worktree sạch;
- final report liệt kê architecture, file rewritten/removed/archived, tests,
  coverage, commit hashes, remote branch, open risks và HIL còn thiếu.

Nếu một phần chưa thể hoàn tất offline, vẫn tiếp tục các phần độc lập; ghi rõ
`BLOCKED` và bằng chứng. Không biến thiếu HIL thành lý do giữ lại kiến trúc vá
cũ. Mục tiêu của task này là một nền tảng ToolVision v4 mới, nhỏ gọn, có thể
kiểm chứng và xuất phát trực tiếp từ bài học đo kTAMV thực tế.

---

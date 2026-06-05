# 2026-06-05 - Tong hop cap nhat he thong

## Muc tieu

Tong hop cac thay doi lon da dua vao cau hinh Voron/StealthChanger sau dot on dinh prime line, print-start va quy trinh cap nhat tu GitHub.

## Cau truc repository

- Sap xep lai repository thanh 2 nhom chinh:
  - `config/`: cau hinh Klipper/Moonraker that su duoc copy ve may Voron.
  - `extras/`: tep tham khao, log, hinh anh, G-code, tai lieu va project phu khong duoc copy vao `~/printer_data/config`.
- Xoa thu muc backup cu `config_full_backup_before_english_comments_...` khoi repository vi cau hinh hien tai da on dinh.
- Di chuyen cac phan khong can chay tren Voron vao `extras/`, giup thu muc `config/` gon va de doc hon.

## Script install/update

- `config/scripts/install.sh` va `config/scripts/update.sh` chi copy noi dung trong `config/` ve `~/printer_data/config`.
- Them co che tao backup tren may Voron truoc khi cap nhat:
  - Backup duoc luu tai `~/printer_data/config_backups/config-YYYYMMDD-HHMMSS`.
  - Mac dinh giu cac backup moi nhat, tranh lam day thu muc home.
- Them `config/scripts/cleanup-voron.sh` de don cac thu muc cu/khong con dung tren may Voron. Script chay dry-run mac dinh, chi xoa khi them `--apply`.

## PRINT_START va QGL

- Dieu chinh `PRINT_START` de tranh toolchange/dock truoc khi full `G28`.
- Bo lan QGL som khi ban con dang nong len. QGL hien chi chay sau khi:
  - `M190` da cho ban dat nhiet.
  - Heat soak neu can da xong.
- Ly do: Cartographer va ban dang drift nhiet co the lam QGL retry tang dan, dan toi loi:
  - `Probed points range is increasing`
  - `Possibly Z motor numbering is wrong`
- Xoa `G28 Z` du sau `QUAD_GANTRY_LEVEL` trong `PRINT_START`, vi wrapper `QUAD_GANTRY_LEVEL` da tu ket thuc bang `G28 Z`.
- Cap nhat cac huong dan calibration cu tu:
  - `G28 -> QUAD_GANTRY_LEVEL -> G28 Z`
  thanh:
  - `G28 -> QUAD_GANTRY_LEVEL`

## Quan ly nhiet tool trong PRINT_START

- Cac tool co dung trong file in duoc giu o standby khoang 150 C trong giai do chuan bi.
- Tool khong dung se tat nhiet.
- T0 bi gioi han o nhiet probe/touch-home cho den khi Cartographer touch home xong.
- Sau touch-home:
  - Tool sap prime dau tien duoc nang len nhiet in trong luc mesh dang chay.
  - Cac tool dung con lai giu standby de giam thoi gian cho nhiet nhung han che nhua chay ra.

## Prime line nhieu tool

- Them/hoan thien `PRIME_LINES` cho he multi-tool.
- Prime cac tool co su dung trong G-code slicer, tool in dau tien duoc prime cuoi cung de sau prime dau in san sang bat dau in.
- Chuyen bo cuc prime line ve phia truoc giua ban, tranh qua gan cac goc.
- Moi tool ve 3 duong song song theo truc X, tong chieu dai khoang 40 mm de co du thoi gian ra nhua.
- Giam nguy co tao soi dai khi dock bang cac thao tac retract/wipe/standby trong logic prime.

## Hieu chinh tool offset

- Cap nhat Z offset theo ket qua test first layer thuc te:
  - T1 bu sai lech khoang +0.07 mm.
  - T3 bu sai lech khoang +0.26 mm.
  - T4 bu sai lech khoang +0.26 mm.
  - T2 tam thoi de rieng vi dang nghi ngo co van de co khi/nhiet dau in.
- Cac gia tri duoc dua vao `printer.cfg`/SAVE_CONFIG de gan voi thuc te in, khong phai loi do prime line.

## Moonraker va Tailscale

- Them dai Tailscale vao `moonraker.conf`:
  - `100.64.0.0/10`
  - `fd7a:115c:a1e0::/48`
- Muc dich: cho phep truy cap Mainsail/Moonraker qua IP Tailscale tu xa ma khong bi chan authorization/CORS.

## Don dep Axiscope

- Axiscope khong con dung trong cau hinh chay chinh.
- Phan lien quan duoc dua ve khu vuc tham khao/backup, khong nam trong payload cap nhat truc tiep vao may Voron.

## Luu y van hanh

- Sau khi cap nhat macro Klipper:

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart klipper
```

- Chi can restart Moonraker khi thay doi `moonraker.conf`.
- Khi cap nhat tu GitHub ve Voron, script se tu tao backup truoc khi copy file moi.

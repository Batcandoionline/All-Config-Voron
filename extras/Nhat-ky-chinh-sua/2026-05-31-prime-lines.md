# 2026-05-31 - Prime line nhiều tool

## Tóm tắt

- Thêm `Printer-Setup/prime-lines.cfg`.
- Include file này từ `printer.cfg`.
- Cập nhật `PRINT_START` để gọi `PRIME_LINES` thay cho `_PRIME_LINE` một tool.

## Cách hoạt động

- Chỉ prime các tool có giá trị `Tn_TEMP` do slicer truyền vào.
- Các tool không phải tool in ban đầu sẽ được prime trước.
- Tool in ban đầu được prime sau cùng và giữ nguyên trên carriage để bắt đầu layer 1.
- Chiều dài đường prime theo trục X được giới hạn theo kích thước bàn hiện tại.
- Khoảng cách theo Y tự co lại nếu số lượng tool cấu hình có nguy cơ vượt chiều sâu bàn.

## Luồng nhiệt

- T0 được giữ ở `PROBE_TEMP` cho đến khi Cartographer touch-home hoàn tất.
- Các tool không phải T0 nhưng có dùng trong file in được làm nóng sớm đến tối đa khoảng 170 độ C trong giai đoạn khởi động.
- `PRIME_LINES` chờ từng tool đạt nhiệt độ first-layer của slicer ngay trước khi purge tool đó.

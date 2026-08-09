# Tổng quan dự án

## Tên dự án

**Voron 2.4 StealthChanger — Kho cấu hình 5-Tool**

## Mục đích

Kho lưu trữ này chứa **toàn bộ cấu hình đang vận hành (production)** cho máy in Voron 2.4 trang bị hệ thống StealthChanger 5-tool chạy firmware Klipper.

## Mục tiêu

Mọi hành động trong kho lưu trữ này phải phục vụ các mục tiêu cốt lõi sau:

1. **Ổn định** — Máy in phải hoạt động bình thường sau mỗi thay đổi. Không bao giờ đưa vào các sửa đổi chưa được kiểm tra hoặc mang tính suy đoán.
2. **Dễ hoàn tác** — Mọi thay đổi phải có khả năng đảo ngược. Sao lưu và kiểm soát phiên bản đảm bảo phục hồi tức thì.
3. **Dễ bảo trì** — Các file cấu hình phải sạch sẽ, có tài liệu đầy đủ và được tổ chức logic.
4. **Dễ hợp tác** — Bất kỳ AI assistant hoặc người nào cũng phải hiểu cấu trúc dự án trong vài phút.

## Thông số phần cứng

| Thành phần | Chi tiết |
|-----------|----------|
| Máy in | Voron 2.4 (350mm) |
| Hệ thống đổi đầu | StealthChanger — 5 tool (T0–T4) |
| Firmware | Klipper (v0.13.x) |
| MCU chính | Octopus Pro (STM32, CAN bridge) |
| MCU đầu in | EBBCan (EBB0–EBB4) — CAN bus |
| Cảm biến probe | Cartographer v3 (CAN bus) |
| Giao diện web | Mainsail |
| Màn hình | KlipperScreen |
| Máy chủ | Raspberry Pi chạy MainsailOS |

## Quy tắc quan trọng nhất

> **Đây là dự án đang vận hành (production).**
>
> Mọi thay đổi phải đảm bảo sự ổn định của máy in.
> Nếu không chắc chắn về bất kỳ sửa đổi nào — **DỪNG LẠI và hỏi người dùng.**

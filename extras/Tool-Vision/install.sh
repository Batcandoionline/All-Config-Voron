#!/bin/bash
echo "======================================================"
echo "    Cài đặt Tool Vision (Z & XY Calibration)          "
echo "======================================================"

# 1. Link Klipper Extension
echo "[1/4] Liên kết mã nguồn Python vào Klipper..."
ln -sf ~/printer_data/config/Voron\ 5\ Tool/extras/Tool-Vision/klippy/extras/tool_vision.py ~/klipper/klippy/extras/tool_vision.py
echo "Đã liên kết (link) module tool_vision.py."

# 2. Setup Python Virtual Environment for Vision Server
echo "[2/4] Thiết lập môi trường Python cho Vision Server..."
cd ~/
if [ ! -d "tool-vision-env" ]; then
    python3 -m venv tool-vision-env
fi
source tool-vision-env/bin/activate
pip install opencv-python-headless numpy requests flask

# 3. Setup Systemd Service
echo "[3/4] Đăng ký Systemd Service cho Vision Server..."
sudo cp ~/printer_data/config/Voron\ 5\ Tool/extras/Tool-Vision/server/tool_vision.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tool_vision.service
sudo systemctl restart tool_vision.service
echo "Dịch vụ tool_vision đã được kích hoạt."

# 4. Restart Klipper
echo "[4/4] Khởi động lại Klipper..."
sudo systemctl restart klipper

echo "======================================================"
echo "    CÀI ĐẶT THÀNH CÔNG!                               "
echo "======================================================"
echo "Vui lòng mở file printer.cfg, thêm dòng sau:"
echo "  [include Voron 5 Tool/extras/Tool-Vision/tool_vision.cfg]"
echo "Bạn có thể chỉnh sửa tọa độ trong file tool_vision.cfg để phù hợp với máy in."

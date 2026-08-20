#!/bin/bash
echo "======================================================"
echo "    Tool Vision - Install Script                       "
echo "    Unified XYZ Tool Alignment for Klipper             "
echo "======================================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KLIPPER_EXTRAS="$HOME/klipper/klippy/extras"
SERVER_DIR="$SCRIPT_DIR/server"

# 1. Link Klipper Extension
echo "[1/4] Linking Klipper extension..."
if [ ! -d "$KLIPPER_EXTRAS" ]; then
    echo "  ERROR: Klipper extras directory not found at $KLIPPER_EXTRAS"
    exit 1
fi
ln -sf "$SCRIPT_DIR/klippy/extras/tool_vision.py" "$KLIPPER_EXTRAS/tool_vision.py"
echo "  -> Linked tool_vision.py"

# 2. Setup Python Virtual Environment for Vision Server
echo "[2/4] Setting up Python venv for Vision Server..."
cd "$HOME"
if [ ! -d "tool-vision-env" ]; then
    python3 -m venv tool-vision-env
    echo "  -> Created virtual environment"
fi
source tool-vision-env/bin/activate
pip install -q opencv-python-headless numpy requests flask Pillow matplotlib waitress
deactivate
echo "  -> Python packages installed."

# 3. Setup Systemd Service
echo "[3/4] Registering systemd service..."
sudo cp "$SERVER_DIR/tool_vision.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tool_vision.service
sudo systemctl restart tool_vision.service
echo "  -> Service tool_vision enabled and started."

# 4. Restart Klipper
echo "[4/4] Restarting Klipper..."
sudo systemctl restart klipper

echo ""
echo "======================================================"
echo "    INSTALLATION COMPLETE!                             "
echo "======================================================"
echo ""
echo "Next steps:"
echo "  1. Add to printer.cfg:"
echo "     [include Voron 5 Tool/extras/Tool-Vision/tool_vision.cfg]"
echo "  2. Edit tool_vision.cfg with your Z switch and camera coordinates."
echo "  3. Remove [axiscope] section if present (Tool Vision replaces it)."
echo "  4. Restart Klipper."
echo ""
echo "Quick start:"
echo "  TV_SEND_SERVER_CFG         Send camera config to server"
echo "  TV_START_PREVIEW           Check camera view"
echo "  TV_CALIBRATE_ALL           Full XYZ calibration for all tools"
echo ""
echo "Individual commands:"
echo "  TV_CALIB_CAMERA            Calibrate camera mm/pixel"
echo "  TV_FIND_NOZZLE_CENTER      Center nozzle in camera view"
echo "  TV_CALIBRATE_ALL_Z         Z-only calibration"
echo "  TV_CALIBRATE_ALL_XY        XY-only calibration"
echo "  TV_MOVE_TO_ZSWITCH         Move above Z switch"
echo "  TV_PROBE_ZSWITCH           Probe Z switch"
echo "======================================================"

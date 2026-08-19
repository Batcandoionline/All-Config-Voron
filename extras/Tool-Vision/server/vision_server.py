# Tool Vision - HTTP Server
# Based on: kTAMV/server/ktamv_server.py
# Flask + Waitress server handling nozzle detection requests and camera preview
#
# API Endpoints (same as kTAMV for backward compatibility):
#   POST /set_server_cfg       - Set camera URL and detection config
#   GET  /getNozzlePosition    - Start async nozzle detection
#   GET  /getRequest           - Poll for detection result
#   POST /calculate_camera_to_space_matrix - Build transform matrix
#   POST /calculate_offset_from_matrix     - Calculate offset from matrix
#   POST /preview              - Start/stop camera preview
#   GET  /image                - Get latest processed frame as JPEG
#   GET  /                     - Server status page

import datetime
import io
import time
import random
import os
import numpy as np
import threading
from dataclasses import dataclass, asdict
from flask import Flask, jsonify, request, send_file
from PIL import Image, ImageDraw, ImageFont
from argparse import ArgumentParser
import matplotlib.font_manager as fm
from waitress import serve
import logging
import json
import traceback
from vision_dm import VisionDetectionManager

# ── Constants ──────────────────────────────────────────────────
_FRAME_WIDTH = 640
_FRAME_HEIGHT = 480
_CV_TIMEOUT = 20          # seconds before nozzle detection times out
_CV_MIN_MATCHES = 3       # consecutive matches required
_PREVIEW_FPS = 2          # max FPS for preview mode

# ── Module State ───────────────────────────────────────────────
_camera_url = None
_transform_matrix = None
_detection_tolerance = 0
_send_frame_to_cloud = False
_cloud_url = ""
_preview_running = False
_update_static_image = True
_error_message = ""
_processed_frame_as_image = None
_processed_frame_as_bytes = None
_logdebug = ""

# Request results storage {request_id: RequestResult}
request_results = dict()

# ── Logging Setup ──────────────────────────────────────────────
if not os.path.exists("./logs"):
    os.makedirs("logs")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    filename="logs/tool_vision_server.log",
    filemode="w",
    encoding="utf-8",
)

# ── Flask App ──────────────────────────────────────────────────
app = Flask(__name__)


@dataclass
class RequestResult:
    """Stores the result of an async nozzle detection request."""
    request_id: int
    data: str            # JSON-encoded position data
    runtime: float = None
    statuscode: int = None
    statusmessage: str = None


# ═══════════════════════════════════════════════════════════════
#  CAMERA-TO-SPACE MATRIX (from kTAMV)
# ═══════════════════════════════════════════════════════════════

@app.route("/calculate_camera_to_space_matrix", methods=["POST"])
def calculate_camera_to_space_matrix():
    """Build transformation matrix from calibration points.

    From kTAMV: uses polynomial least-squares fit with features
    [x², y², xy, x, y, 1] to map pixel coords → real-world coords.

    Input JSON: {"calibration_points": [([real_x, real_y], [pixel_x, pixel_y]), ...]}
    """
    _show_error("")
    try:
        log("*** calculate_camera_to_space_matrix ***")

        data = json.loads(request.data)
        calibration_points = data.get("calibration_points")
        if calibration_points is None:
            return "Calibration points not found in request", 400

        n = len(calibration_points)
        real_coords = np.empty((n, 2))
        pixel_coords = np.empty((n, 2))
        for i, (r, p) in enumerate(calibration_points):
            real_coords[i] = r
            pixel_coords[i] = p

        # Build polynomial feature matrix: [x², y², xy, x, y, 1]
        x = pixel_coords[:, 0]
        y = pixel_coords[:, 1]
        A = np.vstack([x**2, y**2, x * y, x, y, np.ones(n)]).T

        # Solve least-squares: A @ coeffs ≈ real_coords
        transform = np.linalg.lstsq(A, real_coords, rcond=None)

        global _transform_matrix
        _transform_matrix = transform[0].T
        log("Transform matrix computed successfully.")
        return "OK", 200

    except json.JSONDecodeError:
        _show_error("Error: Invalid JSON in request.")
        return "JSON decode error", 400
    except Exception as e:
        _show_error("Error: Could not calculate matrix.")
        log("Error: %s\n%s" % (str(e), traceback.format_exc()))
        return str(e), 500


@app.route("/calculate_offset_from_matrix", methods=["POST"])
def calculate_offset_from_matrix():
    """Calculate XY offset from current nozzle position using transform matrix.

    From kTAMV: applies the precomputed transform matrix with a 0.55
    damping factor to prevent overshooting during iterative centering.

    Input JSON: {"_v": [cx², cy², cx*cy, cx, cy, 0]}
    """
    _show_error("")
    try:
        log("*** calculate_offset_from_matrix ***")

        data = json.loads(request.data)
        _v = data.get("_v")

        # Apply transform with damping factor (0.55 from kTAMV)
        offsets = -1 * (0.55 * _transform_matrix @ _v)
        return jsonify(offsets.tolist())

    except json.JSONDecodeError:
        _show_error("Error: Invalid JSON.")
        return "JSON decode error", 400
    except Exception as e:
        _show_error("Error: Could not calculate offset.")
        log("Error: %s\n%s" % (str(e), traceback.format_exc()))
        return str(e), 500


# ═══════════════════════════════════════════════════════════════
#  SERVER CONFIGURATION
# ═══════════════════════════════════════════════════════════════

@app.route("/set_server_cfg", methods=["POST"])
def set_server_cfg():
    """Set camera URL and detection parameters.

    Input JSON: {
        "camera_url": "http://...",
        "send_frame_to_cloud": false,
        "detection_tolerance": 0
    }
    """
    _show_error("")
    try:
        log("*** set_server_cfg ***")

        # Stop preview if running
        global _preview_running, _detection_tolerance, _send_frame_to_cloud
        _preview_running = False

        data = json.loads(request.data)
        camera_url = data.get("camera_url")
        response = ""

        # Optional: cloud upload setting
        cloud_flag = data.get("send_frame_to_cloud")
        if cloud_flag is not None:
            _send_frame_to_cloud = bool(cloud_flag)
            response += "send_frame_to_cloud=%s\n" % _send_frame_to_cloud

        # Optional: detection tolerance
        tol = data.get("detection_tolerance")
        if tol is not None:
            _detection_tolerance = int(tol)

        if camera_url is None:
            _show_error("Error: Missing camera_url.")
            return "camera_url not found in request", 400

        if camera_url.casefold().startswith(("http://", "https://")):
            global _camera_url
            _camera_url = camera_url
            log("Camera URL set to: %s" % _camera_url)
            _show_error("Camera URL set.")
            return response + "Camera set to " + _camera_url, 200
        else:
            _show_error("Error: Invalid camera URL.")
            return "Camera URL must start with http:// or https://", 400

    except json.JSONDecodeError:
        _show_error("Error: Invalid JSON.")
        return "JSON decode error", 400
    except Exception as e:
        _show_error("Error: Config failed.")
        log("Error: %s\n%s" % (str(e), traceback.format_exc()))
        return str(e), 500


# ═══════════════════════════════════════════════════════════════
#  NOZZLE POSITION DETECTION (Async Request/Result Pattern)
# ═══════════════════════════════════════════════════════════════

@app.route("/getNozzlePosition")
def getNozzlePosition():
    """Start asynchronous nozzle detection.

    From kTAMV: generates a random request_id, starts detection in a
    background thread, returns immediately with status 202 (Accepted).
    Client polls /getRequest?request_id=... for result.

    Returns JSON: {"request_id": N, "statuscode": 202, ...}
    """
    _show_error("")
    global _preview_running
    _preview_running = False

    try:
        log("*** getNozzlePosition ***")
        start_time = time.time()
        request_id = random.randint(0, 1000000)

        if _camera_url is None:
            request_results[request_id] = RequestResult(
                request_id, None,
                time.time() - start_time, 502, "Camera URL not set"
            )
            log("Camera URL not set, returning 502.")
            return jsonify(asdict(request_results[request_id]))

        # Mark as accepted
        request_results[request_id] = RequestResult(
            request_id, None, None, 202, "Accepted"
        )

        def do_work():
            """Background thread: run detection and store result."""
            log("Detection thread started (id=%d)" % request_id)
            dm = VisionDetectionManager(
                log, _camera_url, _cloud_url, _send_frame_to_cloud
            )

            position = dm.recursively_find_nozzle_position(
                _put_frame, _CV_MIN_MATCHES, _CV_TIMEOUT, _detection_tolerance
            )
            log("Detection result: %s" % str(position))

            if position is None:
                result = RequestResult(
                    request_id, None,
                    time.time() - start_time, 404, "No nozzle found"
                )
                _show_error("Error: No nozzle found.")
            else:
                result = RequestResult(
                    request_id, json.dumps(position),
                    time.time() - start_time, 200, "OK"
                )

            request_results[request_id] = result
            log("Detection thread finished (id=%d)" % request_id)

        thread = threading.Thread(target=do_work)
        thread.start()

        return jsonify(asdict(request_results[request_id]))

    except Exception as e:
        _show_error("Error: Detection failed.")
        log("Error: %s\n%s" % (str(e), traceback.format_exc()))
        return str(e), 500


@app.route("/getRequest", methods=["GET", "POST"])
def getRequest():
    """Poll for an async detection result.

    Query param: request_id (int)
    Returns the RequestResult for that id, or 404 if not found.
    """
    try:
        request_id = request.args.get("request_id", type=int, default=None)
        if request_id in request_results:
            return jsonify(asdict(request_results[request_id]))
        else:
            return jsonify(asdict(
                RequestResult(request_id, None, None, 404, "Request not found")
            ))
    except Exception as e:
        log("Error in getRequest: %s" % str(e))
        return str(e), 500


@app.route("/getAllRequests")
def getAllRequests():
    """Return all stored request results (debugging)."""
    try:
        serialized = {k: asdict(v) for k, v in request_results.items()}
        return jsonify(serialized)
    except Exception as e:
        log("Error: %s" % str(e))
        return str(e), 500


# ═══════════════════════════════════════════════════════════════
#  PREVIEW
# ═══════════════════════════════════════════════════════════════

@app.route("/preview", methods=["POST"])
def preview():
    """Start or stop camera preview.

    Input JSON: {"action": "start"} or {"action": "stop"}
    """
    _show_error("")
    try:
        global _preview_running
        data = json.loads(request.data)
        action = data.get("action")

        def do_preview():
            """Background thread: continuous frame capture + detection."""
            dm = VisionDetectionManager(
                log, _camera_url, cloud_url="", send_to_cloud=False
            )
            while _preview_running:
                dm.get_preview_frame(_put_frame)
                # Rate limit to prevent overload
                time.sleep(1.0 / _PREVIEW_FPS)

        if action == "stop":
            _preview_running = False
            return "Preview stopped.", 200
        elif action == "start":
            if _camera_url is None:
                return "Camera URL not set", 502
            _preview_running = True
            threading.Thread(target=do_preview).start()
            return "Preview started.", 200
        else:
            return "Invalid action. Use 'start' or 'stop'.", 400

    except json.JSONDecodeError:
        _show_error("Error: Invalid JSON.")
        return "JSON decode error", 400
    except Exception as e:
        _show_error("Error: Preview failed.")
        log("Error: %s\n%s" % (str(e), traceback.format_exc()))
        return str(e), 500


# ═══════════════════════════════════════════════════════════════
#  IMAGE ENDPOINT
# ═══════════════════════════════════════════════════════════════

@app.route("/image")
def image():
    """Return the latest processed frame as JPEG.

    If no frame has been captured yet, shows a blank standby image.
    Text overlays show: timestamp, config status, error messages.
    """
    try:
        global _processed_frame_as_bytes, _update_static_image
        global _processed_frame_as_image

        # Load standby image if no frame yet
        if _processed_frame_as_image is None:
            standby_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "standby.jpg"
            )
            if os.path.exists(standby_path):
                _processed_frame_as_image = Image.open(standby_path)
                _processed_frame_as_image.load()
            else:
                _processed_frame_as_image = Image.new(
                    "RGB", (640, 480), (40, 40, 40)
                )
            _update_static_image = True

        if _update_static_image:
            _update_static_image = False

            # Draw status overlays
            _processed_frame_as_image = _draw_on_frame(
                _processed_frame_as_image
            )

            # Convert to JPEG bytes
            img_io = io.BytesIO()
            _processed_frame_as_image.save(img_io, "JPEG")
            img_io.seek(0)
            _processed_frame_as_bytes = img_io.read()

        frame_file = io.BytesIO(_processed_frame_as_bytes)
        frame_file.seek(0)
        return send_file(frame_file, mimetype="image/jpeg")

    except Exception as e:
        log("Error in /image: %s\n%s" % (str(e), traceback.format_exc()))
        return str(e), 500


# ═══════════════════════════════════════════════════════════════
#  STATUS PAGE
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Server status page showing config and recent log."""
    content = "<H1>Tool Vision Server is running</H1><br>"
    content += "Frame: %dx%d<br>" % (_FRAME_WIDTH, _FRAME_HEIGHT)
    content += "Debug:<br>%s<br>" % _logdebug
    try:
        with open("logs/tool_vision_server.log", "r", encoding="utf-8") as f:
            content += f.read().replace("\n", "<br>")
        return (
            '<html><head><meta charset="utf-8"></head>'
            "<body>%s</body></html>" % content
        )
    except FileNotFoundError:
        return content + "Log file not found"


# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _put_frame(frame):
    """Called by DetectionManager to store the latest processed frame."""
    try:
        global _processed_frame_as_image, _update_static_image
        _processed_frame_as_image = Image.fromarray(frame)
        _update_static_image = True
    except Exception as e:
        log("Error in _put_frame: %s" % str(e))


def _draw_on_frame(frame):
    """Draw text overlays on the frame image."""
    current_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    frame = _draw_text(frame, "Updated: " + current_dt, row=1)

    if _camera_url is None:
        frame = _draw_text(
            frame, "Tool Vision: Config not received.", row=2
        )
    elif _processed_frame_as_image is None:
        frame = _draw_text(
            frame, "No image received since start.", row=2
        )
    elif _transform_matrix is None:
        frame = _draw_text(frame, "Camera not calibrated.", row=2)

    if _error_message:
        frame = _draw_text(frame, _error_message, row=3)

    if _preview_running:
        frame = _draw_text(
            frame, "Preview running.", row=-1, row_width=270
        )

    return frame


def _draw_text(frame, text, row=1, row_width=640):
    """Draw text with black background on frame.

    Args:
        frame: PIL Image
        text: string to draw
        row: positive = from top, negative = from bottom
        row_width: width of the text background bar
    """
    try:
        FONT_SIZE = 28
        FONT_COLOR = (255, 255, 255)
        ORIGIN = (10, 10)

        draw = ImageDraw.Draw(frame)
        font_path = fm.findfont(fm.FontProperties(family="arial"))
        font = ImageFont.truetype(font_path, FONT_SIZE)

        if row > 0:
            start = (ORIGIN[0], ORIGIN[1] + (row - 1) * (FONT_SIZE + 10))
        else:
            start = (
                ORIGIN[0],
                frame.height - (abs(row) * (FONT_SIZE + 10) + ORIGIN[1]),
            )

        # Black background bar
        draw.rectangle(
            (
                start[0] - 5, start[1] - 5,
                row_width - start[0], start[1] + FONT_SIZE + 10,
            ),
            fill=(0, 0, 0),
        )
        draw.text(start, text, font=font, fill=FONT_COLOR)
        return frame
    except Exception as e:
        log("Error in _draw_text: %s" % str(e))
        return frame


def _show_error(message):
    """Set error message to display on next frame."""
    global _error_message, _update_static_image
    _error_message = message
    _update_static_image = True


def log(message):
    """Append to in-memory debug log."""
    global _logdebug
    _logdebug += message + "<br>"


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--port", type=int, default=8085, help="Port number")
    args = parser.parse_args()

    serve(app, host="0.0.0.0", port=args.port)

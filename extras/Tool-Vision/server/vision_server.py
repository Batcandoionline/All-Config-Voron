# Tool Vision - HTTP Server
# Handles nozzle detection requests and camera preview
# Rebuilt from ktamv_server.py with identical API endpoints

import datetime
import io
import time
import random
import os
import numpy as np
import threading
from flask import Flask, jsonify, request, send_file
from PIL import Image, ImageDraw, ImageFont
from argparse import ArgumentParser
import matplotlib.font_manager as fm
from waitress import serve
import logging
import json
import traceback
from dataclasses import dataclass
from vision_dm import VisionDetectionManager as DM

__logdebug = ""
__CLOUD_URL = ""
__CV_TIMEOUT = 20
__CV_MIN_MATCHES = 3
_FRAME_WIDTH = 640
_FRAME_HEIGHT = 480
__PREVIEW_FPS = 2

__detection_tolerance = 0
__update_static_image = True
__error_message_to_image = ""
__preview_running = False

# Logging
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

app = Flask(__name__)

__processed_frame_as_image = None
__processed_frame_as_bytes = None
__standby_image = None
_camera_url = None
__send_frame_to_cloud = False
request_results = dict()
_transformMatrix = None


@dataclass
class RequestResult:
    request_id: int
    data: str
    runtime: float = None
    statuscode: int = None
    statusmessage: str = None


# ── Camera-to-Space Matrix ─────────────────────────────────────
@app.route("/calculate_camera_to_space_matrix", methods=["POST"])
def calculate_camera_to_space_matrix():
    show_error_message_to_image("")
    try:
        log("*** calculate_camera_to_space_matrix ***")
        data = json.loads(request.data)
        calibration_points = data.get("calibration_points")

        if calibration_points is None:
            return "Calibration Points not found", 400

        n = len(calibration_points)
        real_coords = np.empty((n, 2))
        pixel_coords = np.empty((n, 2))
        for i, (r, p) in enumerate(calibration_points):
            real_coords[i] = r
            pixel_coords[i] = p

        x, y = pixel_coords[:, 0], pixel_coords[:, 1]
        A = np.vstack([x**2, y**2, x * y, x, y, np.ones(n)]).T
        transform = np.linalg.lstsq(A, real_coords, rcond=None)

        global _transformMatrix
        _transformMatrix = transform[0].T
        return "OK", 200
    except Exception as e:
        show_error_message_to_image("Error: Could not calculate matrix.")
        log("Error: " + str(e) + "\n" + traceback.format_exc())
        return str(e), 500


@app.route("/calculate_offset_from_matrix", methods=["POST"])
def calculate_offset_from_matrix():
    show_error_message_to_image("")
    try:
        log("*** calculate_offset ***")
        data = json.loads(request.data)
        _v = data.get("_v")
        offsets = -1 * (0.55 * _transformMatrix @ _v)
        return jsonify(offsets.tolist())
    except Exception as e:
        show_error_message_to_image("Error: Could not calculate offset.")
        log("Error: " + str(e) + "\n" + traceback.format_exc())
        return str(e), 500


# ── Server Config ──────────────────────────────────────────────
@app.route("/set_server_cfg", methods=["POST"])
def set_server_cfg():
    show_error_message_to_image("")
    try:
        log("*** set_server_cfg ***")
        global __preview_running, __detection_tolerance, __send_frame_to_cloud
        __preview_running = False
        response = ""

        data = json.loads(request.data)
        camera_url = data.get("camera_url")

        try:
            __send_frame_to_cloud = data.get("send_frame_to_cloud", False)
        except:
            pass

        try:
            __detection_tolerance = data.get("detection_tolerance", 0)
        except:
            pass

        if camera_url is None:
            show_error_message_to_image("Error: Missing camera_url.")
            return "camera_url not found", 400

        if camera_url.casefold().startswith(("http://", "https://")):
            global _camera_url
            _camera_url = camera_url
            log("Camera URL set to %s" % _camera_url)
            show_error_message_to_image("Camera URL set.")
            return response + "Camera set to " + _camera_url, 200
        else:
            show_error_message_to_image("Error: Invalid camera URL.")
            return "Camera URL must start with http:// or https://", 400
    except Exception as e:
        show_error_message_to_image("Error: Config failed.")
        log("Error: " + str(e) + "\n" + traceback.format_exc())
        return str(e), 500


# ── Frame Display ──────────────────────────────────────────────
def put_frame(frame):
    try:
        global __processed_frame_as_image, __update_static_image
        __processed_frame_as_image = Image.fromarray(frame)
        __update_static_image = True
    except Exception as e:
        log("Error: " + str(e) + "\n" + traceback.format_exc())


# ── Request Management ────────────────────────────────────────
@app.route("/getAllRequests")
def getAllRequests():
    try:
        return jsonify(request_results)
    except Exception as e:
        log("Error: " + str(e))


@app.route("/")
def index():
    content = "<H1>Tool Vision Server is running</H1><br>"
    content += "Frame: %dx%d<br>" % (_FRAME_WIDTH, _FRAME_HEIGHT)
    content += "Debug:<br>" + __logdebug + "<br>"
    try:
        with open("logs/tool_vision_server.log", "r", encoding="utf-8") as f:
            content += f.read().replace("\n", "<br>")
        return '<html><head><meta charset="utf-8"></head><body>%s</body></html>' % content
    except FileNotFoundError:
        return content + "Log file not found"


@app.route("/getRequest", methods=["GET", "POST"])
def getRequest():
    try:
        request_id = request.args.get("request_id", type=int, default=None)
        try:
            return jsonify(request_results[request_id])
        except KeyError:
            return jsonify(
                RequestResult(request_id, None, None, 404, "Request not found")
            )
    except Exception as e:
        log("Error: " + str(e))


# ── Nozzle Position Detection ─────────────────────────────────
@app.route("/getNozzlePosition")
def getNozzlePosition():
    show_error_message_to_image("")
    global __preview_running
    __preview_running = False

    try:
        log("*** getNozzlePosition ***")
        start_time = time.time()
        request_id = random.randint(0, 1000000)

        if _camera_url is None:
            request_results[request_id] = RequestResult(
                request_id, None, time.time() - start_time, 502, "Camera URL not set"
            )
            return jsonify(request_results[request_id])

        request_results[request_id] = RequestResult(
            request_id, None, None, 202, "Accepted"
        )

        def do_work():
            log("*** detection thread started ***")
            detection_manager = DM(
                log, _camera_url, __CLOUD_URL, __send_frame_to_cloud
            )
            position = detection_manager.recursively_find_nozzle_position(
                put_frame, __CV_MIN_MATCHES, __CV_TIMEOUT, __detection_tolerance
            )

            if position is None:
                result = RequestResult(
                    request_id, None, time.time() - start_time, 404, "No nozzle found"
                )
                show_error_message_to_image("Error: No nozzle found.")
            else:
                result = RequestResult(
                    request_id,
                    json.dumps(position),
                    time.time() - start_time,
                    200,
                    "OK",
                )

            request_results[request_id] = result
            log("*** detection thread finished ***")

        thread = threading.Thread(target=do_work)
        thread.start()

        return jsonify(request_results[request_id])
    except Exception as e:
        show_error_message_to_image("Error: Detection failed.")
        log("Error: " + str(e) + "\n" + traceback.format_exc())


# ── Preview ────────────────────────────────────────────────────
@app.route("/preview", methods=["POST"])
def preview():
    show_error_message_to_image("")
    try:
        global __preview_running
        data = json.loads(request.data)
        action = data.get("action")

        def do_preview():
            dm = DM(log, _camera_url, cloud_url="", send_to_cloud=False)
            while __preview_running:
                dm.get_preview_frame(put_frame)
                time.sleep(1 / __PREVIEW_FPS)

        if action == "stop":
            __preview_running = False
            return "Preview stopped.", 200
        elif action == "start":
            if _camera_url is None:
                return "Camera URL not set", 502
            __preview_running = True
            threading.Thread(target=do_preview).start()
            return "Preview started.", 200
        else:
            return "Invalid action.", 400
    except Exception as e:
        show_error_message_to_image("Error: Preview failed.")
        log("Error: " + str(e) + "\n" + traceback.format_exc())


# ── Image Endpoint ────────────────────────────────────────────
@app.route("/image")
def image():
    try:
        global __processed_frame_as_bytes, __update_static_image
        global __processed_frame_as_image

        if __processed_frame_as_image is None:
            standby_path = os.path.join(os.path.dirname(__file__), "standby.jpg")
            if os.path.exists(standby_path):
                __processed_frame_as_image = Image.open(standby_path, mode="r")
                __processed_frame_as_image.load()
            else:
                __processed_frame_as_image = Image.new("RGB", (640, 480), (40, 40, 40))
            __update_static_image = True

        if __update_static_image:
            __update_static_image = False
            __processed_frame_as_image = drawOnFrame(__processed_frame_as_image)
            img_io = io.BytesIO()
            __processed_frame_as_image.save(img_io, "JPEG")
            img_io.seek(0)
            __processed_frame_as_bytes = img_io.read()

        processed_frame_file = io.BytesIO(__processed_frame_as_bytes)
        processed_frame_file.seek(0)
        return send_file(processed_frame_file, mimetype="image/jpeg")
    except Exception as e:
        log("Error: " + str(e) + "\n" + traceback.format_exc())


# ── Drawing Helpers ────────────────────────────────────────────
def drawOnFrame(usedFrame):
    current_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    usedFrame = drawTextOnFrame(usedFrame, "Updated: " + current_dt, row=1)

    if _camera_url is None:
        usedFrame = drawTextOnFrame(
            usedFrame, "Tool Vision: Config not received.", row=2
        )
    elif __processed_frame_as_image is None:
        usedFrame = drawTextOnFrame(
            usedFrame, "No image received since start.", row=2
        )
    elif _transformMatrix is None:
        usedFrame = drawTextOnFrame(
            usedFrame, "Camera not calibrated.", row=2
        )

    if __error_message_to_image:
        usedFrame = drawTextOnFrame(usedFrame, __error_message_to_image, row=3)

    if __preview_running:
        usedFrame = drawTextOnFrame(
            usedFrame, "Preview running.", row=-1, row_width=270
        )

    return usedFrame


def drawTextOnFrame(usedFrame, text, row=1, row_width=640):
    try:
        FONT_SIZE = 28
        FONT_COLOR = (255, 255, 255)
        FIRST_ROW_START = (10, 10)

        draw = ImageDraw.Draw(usedFrame)
        font_path = fm.findfont(fm.FontProperties(family="arial"))
        font = ImageFont.truetype(font_path, FONT_SIZE)

        if row > 0:
            start_point = (
                FIRST_ROW_START[0],
                FIRST_ROW_START[1] + (row - 1) * (FONT_SIZE + 10),
            )
        else:
            start_point = (
                FIRST_ROW_START[0],
                usedFrame.height
                - (abs(row) * (FONT_SIZE + 10) + FIRST_ROW_START[1]),
            )

        draw.rectangle(
            (
                start_point[0] - 5,
                start_point[1] - 5,
                row_width - start_point[0],
                start_point[1] + FONT_SIZE + 10,
            ),
            fill=(0, 0, 0),
        )
        draw.text(start_point, text, font=font, fill=FONT_COLOR)
        return usedFrame
    except Exception as e:
        log("Error: " + str(e) + "\n" + traceback.format_exc())


# ── Logging ────────────────────────────────────────────────────
def log_clear():
    global __logdebug
    __logdebug = ""


def log(message):
    global __logdebug
    __logdebug += message + "<br>"


def log_get():
    return __logdebug


def show_error_message_to_image(message):
    global __error_message_to_image, __update_static_image
    __error_message_to_image = message
    __update_static_image = True


# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--port", type=int, default=8085, help="Port number")
    args = parser.parse_args()

    serve(app, host="0.0.0.0", port=args.port)

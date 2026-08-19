# Tool Vision - Klipper Extension for XYZ Tool Alignment
# Rebuilt from kTAMV (XY vision) + Axiscope (Z probe) logic
# Unified into a single autonomous module

import os
import ast
import json
import time
import logging
from math import sqrt
from statistics import mean, stdev

import typing
import urllib.error
import urllib.parse
import urllib.request
from email.message import Message


# ─── Exceptions ────────────────────────────────────────────────
class NozzleNotFoundException(Exception):
    pass


# ─── HTTP Client ───────────────────────────────────────────────
class ServerResponse(typing.NamedTuple):
    body: str
    headers: Message
    status: int

    def json(self) -> typing.Any:
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            return ""


def server_request(url, data=None, params=None, headers=None,
                   method="GET", timeout=2):
    if not url.casefold().startswith("http"):
        raise urllib.error.URLError("Incorrect protocol in url")
    method = method.upper()
    request_data = None
    headers = headers or {}
    data = data or {}
    params = params or {}
    headers = {"Accept": "application/json", **headers}

    if method == "GET":
        params = {**params, **data}
        data = None

    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True, safe="/")

    if data:
        request_data = json.dumps(data).encode()
        headers["Content-Type"] = "application/json; charset=UTF-8"

    httprequest = urllib.request.Request(
        url, data=request_data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(httprequest, timeout=timeout) as resp:
            return ServerResponse(
                headers=resp.headers,
                status=resp.status,
                body=resp.read().decode(
                    resp.headers.get_content_charset("utf-8")
                ),
            )
    except Exception as e:
        raise e.with_traceback(e.__traceback__)


def send_server_command(server_url, command, **data):
    rr = server_request(server_url + command, data=data, method="POST")
    if rr.status != 200:
        raise Exception("Server responded %s: %s" % (rr.status, rr.body))
    return rr.body


# ─── Nozzle Position Fetcher (Async Request/Result pattern) ───
def get_nozzle_position(server_url, reactor):
    logging.debug("tool_vision: get_nozzle_position called")

    response = server_request(
        server_url + "/getNozzlePosition", timeout=2
    )
    if response.status != 200:
        raise Exception(
            "Server error %s: %s" % (response.status, response.body)
        )
    result = json.loads(response.body)
    if not (result["statuscode"] == 202 or result["statuscode"] == 200):
        raise Exception(
            "Server error %s: %s"
            % (result["statuscode"], result["statusmessage"])
        )

    request_id = result["request_id"]
    start_time = time.time()

    while True:
        response = server_request(
            "%s/getRequest?request_id=%s" % (server_url, request_id),
            timeout=2,
        )
        if response.status != 200:
            raise Exception(
                "Server error %s: %s" % (response.status, response.body)
            )
        result = json.loads(response.body)

        if result["statuscode"] == 202:
            if time.time() - start_time >= 60:
                raise NozzleNotFoundException(
                    "Nozzle detection timed out after 60 seconds."
                )
            _ = reactor.pause(reactor.monotonic() + 0.200)
            continue

        elif result["statuscode"] == 200:
            return result

        elif result["statuscode"] == 404:
            raise NozzleNotFoundException(
                "Server did not find nozzle (%s: %s). "
                "Try cleaning the nozzle or adjust Z height."
                % (result["statuscode"], result["statusmessage"])
            )
        else:
            raise Exception(
                "Nozzle detection failed (%s: %s)"
                % (result["statuscode"], result["statusmessage"])
            )


# ─── Camera-to-Space Matrix ───────────────────────────────────
def calculate_camera_to_space_matrix(server_url, calibration_points):
    rr = server_request(
        server_url + "/calculate_camera_to_space_matrix",
        {"calibration_points": calibration_points},
        method="POST",
    )
    return rr.status == 200


def calculate_offset_from_matrix(server_url, _v):
    rr = server_request(
        server_url + "/calculate_offset_from_matrix",
        {"_v": _v},
        method="POST",
    )
    return rr.body


# ─── Math Utilities ───────────────────────────────────────────
def normalize_coords(coords, frame_width=640, frame_height=480):
    return (coords[0] / frame_width - 0.5,
            coords[1] / frame_height - 0.5)


def get_distance(x1, y1, x0, y0):
    return round(sqrt((float(x1) - float(x0))**2
                      + (float(y1) - float(y0))**2), 3)


def get_average_mpp(mpps, space_coordinates, camera_coordinates, gcmd):
    initial_mpps = mpps.copy()

    def _stats(vals):
        return stdev(vals), round(mean(vals), 3)

    mpps_std_dev, mpp = _stats(mpps)

    # Remove highest if >20% above mean
    if max(mpps) > mpp + (mpp * 0.20):
        idx = mpps.index(max(mpps))
        mpps.pop(idx)
        space_coordinates.pop(idx)
        camera_coordinates.pop(idx)
    mpps_std_dev, mpp = _stats(mpps)

    # Remove lowest if >20% below mean
    if min(mpps) < mpp - (mpp * 0.20):
        idx = mpps.index(min(mpps))
        mpps.pop(idx)
        space_coordinates.pop(idx)
        camera_coordinates.pop(idx)
    mpps_std_dev, mpp = _stats(mpps)

    # Remove >2 std deviations
    for i in reversed(range(len(mpps))):
        if mpps[i] > mpp + mpps_std_dev * 2 or mpps[i] < mpp - mpps_std_dev * 2:
            mpps.pop(i)
            space_coordinates.pop(i)
            camera_coordinates.pop(i)
    mpps_std_dev, mpp = _stats(mpps)

    # Remove >25% deviation
    for i in reversed(range(len(mpps))):
        if mpps[i] > mpp + mpp * 0.25 or mpps[i] < mpp - mpp * 0.25:
            mpps.pop(i)
    mpps_std_dev, mpp = _stats(mpps)

    gcmd.respond_info(
        "Final mm/pixel: %.4f, std dev: %.1f%%, using %d of %d values"
        % (mpp, (mpps_std_dev / mpp) * 100, len(mpps), len(initial_mpps))
    )

    if mpps_std_dev / mpp > 0.2:
        gcmd.respond_info("Standard deviation too high. Calibration failed.")
        return None

    return mpp, mpps, space_coordinates, camera_coordinates


# ─── Printer Movement Manager ─────────────────────────────────
class PrinterManager:
    DEFAULT_SPEED = 3000

    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object("gcode")
        self.toolhead = self.printer.lookup_object("toolhead")

    def ensure_homed(self):
        curtime = self.printer.get_reactor().monotonic()
        kin_status = self.toolhead.get_kinematics().get_status(curtime)
        if ("x" not in kin_status["homed_axes"]
                or "y" not in kin_status["homed_axes"]
                or "z" not in kin_status["homed_axes"]):
            raise Exception("Must home X, Y, and Z axes first.")

    def move_relative(self, X=0, Y=0, Z=0, speed=None):
        if speed is None:
            speed = self.DEFAULT_SPEED
        self.ensure_homed()
        pos = self.get_gcode_position()
        new_pos = [pos[0] + X, pos[1] + Y]
        self._move_absolute_array(new_pos, speed)
        self.toolhead.wait_moves()

    def move_absolute(self, X=None, Y=None, Z=None, speed=None):
        if speed is None:
            speed = self.DEFAULT_SPEED
        self._move_absolute_array([X, Y, Z], speed)

    def _move_absolute_array(self, pos_array, speed):
        gcode = "G90\nG1 "
        for i, val in enumerate(pos_array):
            if val is not None:
                axis = ["X", "Y", "Z"][i]
                gcode += "%s%s " % (axis, val)
        gcode += "F%s " % speed
        self.gcode.run_script_from_command(gcode)
        self.toolhead.wait_moves()

    def get_gcode_position(self):
        gcode_move = self.printer.lookup_object("gcode_move")
        pos = gcode_move.get_status()["gcode_position"]
        return [pos.x, pos.y, pos.z]

    def get_raw_position(self):
        gcode_move = self.printer.lookup_object("gcode_move")
        pos = gcode_move.get_status()["position"]
        return [pos.x, pos.y, pos.z]


# ═══════════════════════════════════════════════════════════════
#  MAIN CLASS: ToolVision
# ═══════════════════════════════════════════════════════════════

class ToolVision:
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480

    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object("gcode")
        self.gcode_move = self.printer.load_object(config, "gcode_move")
        self.config = config

        # ── Vision Server config (from kTAMV) ──
        self.camera_url = config.get("nozzle_cam_url")
        self.server_url = config.get("server_url")
        self.move_speed = config.getfloat("move_speed", 1800.0, above=10.0)
        self.calib_iterations = config.getint(
            "calib_iterations", 1, minval=1, maxval=25
        )
        self.calib_value = config.getfloat("calib_value", 1.0, above=0.25)
        self.send_frame_to_cloud = config.getboolean(
            "send_frame_to_cloud", False
        )
        self.detection_tolerance = config.getint(
            "detection_tolerance", 0, minval=0, maxval=5
        )

        # ── Z Switch config (from Axiscope) ──
        self.z_x_pos = config.getfloat("zswitch_x_pos", None)
        self.z_y_pos = config.getfloat("zswitch_y_pos", None)
        self.z_z_pos = config.getfloat("zswitch_z_pos", None)
        self.lift_z = config.getfloat("lift_z", 1)
        self.z_move_speed = config.getint("z_move_speed", 10)
        self.z_samples = config.getint("samples", 10)

        # ── Config File for Saving Offsets (from Axiscope) ──
        self.config_file_path = config.get("config_file_path", None)
        self.has_cfg_data = False

        # ── Z Probe Setup (from Axiscope) ──
        self.pin = config.get("pin", None)
        if self.pin is not None:
            from . import tools_calibrate
            self.probe_multi_axis = tools_calibrate.PrinterProbeMultiAxis(
                config,
                tools_calibrate.ProbeEndstopWrapper(config, "x"),
                tools_calibrate.ProbeEndstopWrapper(config, "y"),
                tools_calibrate.ProbeEndstopWrapper(config, "z"),
            )
            query_endstops = self.printer.load_object(
                config, "query_endstops"
            )
            query_endstops.register_endstop(
                self.probe_multi_axis.mcu_probe[-1].mcu_endstop,
                "ToolVision",
            )
        else:
            self.probe_multi_axis = None

        # ── Custom GCode Templates (from Axiscope) ──
        self.gcode_macro = self.printer.load_object(config, "gcode_macro")
        self.start_gcode = self.gcode_macro.load_template(
            config, "start_gcode", ""
        )
        self.before_pickup_gcode = self.gcode_macro.load_template(
            config, "before_pickup_gcode", ""
        )
        self.after_pickup_gcode = self.gcode_macro.load_template(
            config, "after_pickup_gcode", ""
        )
        self.finish_gcode = self.gcode_macro.load_template(
            config, "finish_gcode", ""
        )

        # ── Internal State (from kTAMV) ──
        self.mpp = None
        self.is_calibrated = False
        self.last_nozzle_center_successful = False
        self.space_coordinates = []
        self.camera_coordinates = []
        self.mm_per_pixels = []
        self.cp = None
        self.last_calculated_offset = [0, 0]

        # ── Internal State (from Axiscope) ──
        self.probe_results = {}

        # ── Toolchanger ──
        self.toolchanger = self.printer.load_object(config, "toolchanger")

        self.printer.register_event_handler(
            "klippy:connect", self._handle_connect
        )
        self.printer.register_event_handler(
            "klippy:ready", self._handle_ready
        )

    # ── Startup ────────────────────────────────────────────────
    def _handle_connect(self):
        if self.config_file_path is not None:
            expanded = os.path.expanduser(self.config_file_path)
            self.config_file_path = expanded
            if os.path.exists(expanded):
                self.has_cfg_data = True
                self.gcode.respond_info(
                    "Tool Vision: config file found (%s)." % expanded
                )
            else:
                self.gcode.respond_info(
                    "Tool Vision: config file not found (%s)." % expanded
                )
        self.gcode.respond_info("--Tool Vision Loaded--")

    def _handle_ready(self):
        self.reactor = self.printer.get_reactor()
        self.pm = PrinterManager(self.config)

        # ── XY Vision Commands (from kTAMV) ──
        self.gcode.register_command(
            "TV_CALIB_CAMERA",
            self.cmd_CALIB_CAMERA,
            desc="Calibrate camera mm/pixel ratio",
        )
        self.gcode.register_command(
            "TV_FIND_NOZZLE_CENTER",
            self.cmd_FIND_NOZZLE_CENTER,
            desc="Find nozzle center and move to it",
        )
        self.gcode.register_command(
            "TV_SET_ORIGIN",
            self.cmd_SET_ORIGIN,
            desc="Save current position as reference origin",
        )
        self.gcode.register_command(
            "TV_GET_OFFSET",
            self.cmd_GET_OFFSET,
            desc="Get XY offset from saved origin",
        )
        self.gcode.register_command(
            "TV_SIMPLE_NOZZLE_POSITION",
            self.cmd_SIMPLE_NOZZLE_POSITION,
            desc="Check if a nozzle is visible in camera",
        )
        self.gcode.register_command(
            "TV_SEND_SERVER_CFG",
            self.cmd_SEND_SERVER_CFG,
            desc="Send camera URL config to vision server",
        )
        self.gcode.register_command(
            "TV_START_PREVIEW",
            self.cmd_START_PREVIEW,
            desc="Start camera preview stream",
        )
        self.gcode.register_command(
            "TV_STOP_PREVIEW",
            self.cmd_STOP_PREVIEW,
            desc="Stop camera preview stream",
        )

        # ── Z Probe Commands (from Axiscope) ──
        self.gcode.register_command(
            "TV_MOVE_TO_ZSWITCH",
            self.cmd_MOVE_TO_ZSWITCH,
            desc="Move toolhead above Z switch",
        )
        self.gcode.register_command(
            "TV_PROBE_ZSWITCH",
            self.cmd_PROBE_ZSWITCH,
            desc="Probe Z switch to determine offset",
        )
        self.gcode.register_command(
            "TV_SET_ENDSTOP_POSITION",
            self.cmd_SET_ENDSTOP_POSITION,
            desc="Set Z switch endstop position",
        )

        # ── Combined Commands ──
        self.gcode.register_command(
            "TV_CALIBRATE_ALL_Z",
            self.cmd_CALIBRATE_ALL_Z,
            desc="Probe Z offset for all tools",
        )
        self.gcode.register_command(
            "TV_CALIBRATE_ALL_XY",
            self.cmd_CALIBRATE_ALL_XY,
            desc="Calibrate XY offset for all tools using camera",
        )
        self.gcode.register_command(
            "TV_CALIBRATE_ALL",
            self.cmd_CALIBRATE_ALL,
            desc="Calibrate XYZ offset for all tools (Z + XY combined)",
        )

        # ── Save/Load Commands (from Axiscope) ──
        self.gcode.register_command(
            "TV_SAVE_TOOL_OFFSET",
            self.cmd_SAVE_TOOL_OFFSET,
            desc="Save tool offsets to config file",
        )
        self.gcode.register_command(
            "TV_SAVE_MULTIPLE_TOOL_OFFSETS",
            self.cmd_SAVE_MULTIPLE_TOOL_OFFSETS,
            desc="Save multiple tool offsets to config file",
        )

        # ── GCode Template Commands ──
        self.gcode.register_command(
            "TV_START_GCODE",
            self.cmd_TV_START_GCODE,
            desc="Execute start_gcode template",
        )
        self.gcode.register_command(
            "TV_BEFORE_PICKUP_GCODE",
            self.cmd_TV_BEFORE_PICKUP_GCODE,
            desc="Execute before_pickup_gcode template",
        )
        self.gcode.register_command(
            "TV_AFTER_PICKUP_GCODE",
            self.cmd_TV_AFTER_PICKUP_GCODE,
            desc="Execute after_pickup_gcode template",
        )
        self.gcode.register_command(
            "TV_FINISH_GCODE",
            self.cmd_TV_FINISH_GCODE,
            desc="Execute finish_gcode template",
        )

    # ═══════════════════════════════════════════════════════════
    #  XY VISION COMMANDS (from kTAMV logic)
    # ═══════════════════════════════════════════════════════════

    def cmd_SEND_SERVER_CFG(self, gcmd):
        """Send camera configuration to the vision server."""
        try:
            cam = gcmd.get("CAMERA_URL", self.camera_url)
            rr = send_server_command(
                self.server_url,
                "/set_server_cfg",
                camera_url=cam,
                send_frame_to_cloud=self.send_frame_to_cloud,
                detection_tolerance=self.detection_tolerance,
            )
            gcmd.respond_info("Tool Vision Server: %s" % str(rr))
        except Exception as e:
            raise self.gcode.error(
                "Failed to send config to server: %s" % str(e)
            )

    def cmd_START_PREVIEW(self, gcmd):
        self._preview(gcmd, "start")

    def cmd_STOP_PREVIEW(self, gcmd):
        self._preview(gcmd, "stop")

    def _preview(self, gcmd, action="start"):
        try:
            rr = send_server_command(
                self.server_url, "/preview", action=action
            )
            gcmd.respond_info("Tool Vision Server: %s" % str(rr))
        except Exception as e:
            raise self.gcode.error(
                "Preview command failed: %s" % str(e)
            )

    def cmd_SET_ORIGIN(self, gcmd):
        """Save raw position as reference point for offset calculations."""
        self.cp = self.pm.get_raw_position()
        self.cp = (round(float(self.cp[0]), 3), round(float(self.cp[1]), 3))
        self.gcode.respond_info(
            "Origin set to X:%.3f Y:%.3f" % (self.cp[0], self.cp[1])
        )

    def cmd_GET_OFFSET(self, gcmd):
        """Calculate XY offset from current position to saved origin."""
        if self.cp is None:
            raise self.gcode.error(
                "No origin set. Use TV_SET_ORIGIN first."
            )
        pos = self.pm.get_raw_position()
        self.last_calculated_offset = (
            round(float(pos[0]) - self.cp[0], 3),
            round(float(pos[1]) - self.cp[1], 3),
        )
        self.gcode.respond_info(
            "Offset from origin: X:%.3f Y:%.3f"
            % (self.last_calculated_offset[0], self.last_calculated_offset[1])
        )

    def cmd_SIMPLE_NOZZLE_POSITION(self, gcmd):
        """Detect if a nozzle is visible in the current camera frame."""
        try:
            result = get_nozzle_position(self.server_url, self.reactor)
            if result is None:
                raise self.gcode.error("Nozzle not found.")
            gcmd.respond_info(
                "Nozzle found at: %s (%.2fs)"
                % (str(result["data"]), float(result["runtime"]))
            )
        except Exception as e:
            raise self.gcode.error(
                "Nozzle position check failed: %s" % str(e)
            )

    def cmd_CALIB_CAMERA(self, gcmd):
        """Calibrate camera mm/pixel ratio using 10-point radial pattern."""
        gcmd.respond_info("Starting mm/pixel calibration...")
        self._calibrate_px_mm(gcmd)

    def cmd_FIND_NOZZLE_CENTER(self, gcmd):
        """Find nozzle center and iteratively move toolhead to camera center."""
        self.last_nozzle_center_successful = False
        self._calibrate_nozzle(gcmd)

    # ── Core XY Calibration Logic (from kTAMV) ────────────────

    def _calibrate_px_mm(self, gcmd):
        """10-point radial calibration for mm/pixel and transformation matrix."""
        self.space_coordinates = []
        self.camera_coordinates = []
        self.mm_per_pixels = []

        calibration_coordinates = [
            [0, -0.5],
            [0.294, -0.405],
            [0.476, -0.155],
            [0.476, 0.155],
            [0.294, 0.405],
            [0, 0.5],
            [-0.294, 0.405],
            [-0.476, 0.155],
            [-0.476, -0.155],
            [-0.294, -0.405],
        ]

        guess_position = [1, 1]

        try:
            self.pm.ensure_homed()
            _rr = get_nozzle_position(self.server_url, self.reactor)

            if _rr is None:
                gcmd.respond_info("Nozzle not found, aborting.")
                return

            _uv = json.loads(_rr["data"])
            _olduv = _uv
            _xy = self.pm.get_gcode_position()

            for i in range(len(calibration_coordinates)):
                _rr = _xy = None
                try:
                    _rr, _xy = self._move_relative_and_get_nozzle_position(
                        calibration_coordinates[i][0],
                        calibration_coordinates[i][1],
                        gcmd,
                    )
                except NozzleNotFoundException:
                    _rr = None

                if _rr is None:
                    self.pm.move_relative(
                        X=-calibration_coordinates[i][0],
                        Y=-calibration_coordinates[i][1],
                    )
                    gcmd.respond_info(
                        "Step %d/%d failed."
                        % (i + 1, len(calibration_coordinates))
                    )
                    continue

                _uv = json.loads(_rr["data"])
                mpp = self._get_mm_per_pixel(
                    calibration_coordinates[i], _olduv, _uv
                )
                self._save_coordinates_for_matrix(_xy, _uv, mpp)
                gcmd.respond_info(
                    "Step %d/%d: mm/px = %s"
                    % (i + 1, len(calibration_coordinates), str(mpp))
                )

                if i < len(calibration_coordinates) - 1:
                    self.pm.move_relative(
                        X=-calibration_coordinates[i][0],
                        Y=-calibration_coordinates[i][1],
                    )

            # Move back to center
            gcmd.respond_info("Moving back to starting position...")
            if _rr is not None:
                try:
                    _rr, _xy = self._move_relative_and_get_nozzle_position(
                        -calibration_coordinates[i][0],
                        -calibration_coordinates[i][1],
                        gcmd,
                    )
                except NozzleNotFoundException:
                    _rr = None

                if _rr is None:
                    _uv = _olduv = None
                else:
                    _olduv = _uv
                    _uv = json.loads(_rr["data"])
                    mpp = self._get_mm_per_pixel(
                        calibration_coordinates[i], _olduv, _uv
                    )
                    self._save_coordinates_for_matrix(_xy, _uv, mpp)
                    gcmd.respond_info(
                        "Center calibrated: mm/px = %.4f" % mpp
                    )

            # Validate
            if len(self.mm_per_pixels) < len(calibration_coordinates) * 0.75:
                raise self.gcode.error(
                    "More than 25%% of calibration points failed, aborting."
                )

            # Calculate average mpp
            gcmd.respond_info("Calculating average mm/pixel...")
            self.mpp = self._get_average_mpp_from_lists(gcmd)

            # Build transformation matrix
            transform_input = [
                (
                    self.space_coordinates[i],
                    normalize_coords(camera),
                )
                for i, camera in enumerate(self.camera_coordinates)
            ]

            if not calculate_camera_to_space_matrix(
                self.server_url, transform_input
            ):
                raise self.gcode.error(
                    "Failed to calculate camera-to-space matrix."
                )

            # Guess center position
            _current_position = self.pm.get_gcode_position()
            _cx, _cy = normalize_coords(_uv)
            _v = [_cx**2, _cy**2, _cx * _cy, _cx, _cy, 0]

            _offsets = json.loads(
                calculate_offset_from_matrix(self.server_url, _v)
            )

            guess_position[0] = (
                round(_offsets[0], 3) + round(_current_position[0], 3)
            )
            guess_position[1] = (
                round(_offsets[1], 3) + round(_current_position[1], 3)
            )

            self.pm.move_absolute(
                X=guess_position[0], Y=guess_position[1]
            )
            try:
                get_nozzle_position(self.server_url, self.reactor)
            except NozzleNotFoundException:
                pass

            self.is_calibrated = True
            gcmd.respond_info("Camera calibration complete!")

        except Exception as e:
            raise self.gcode.error(
                "Camera calibration failed: %s" % str(e)
            ).with_traceback(e.__traceback__)

    def _calibrate_nozzle(self, gcmd, retries=30):
        """Iteratively move nozzle to camera center using transformation matrix."""
        _retries = 0
        _not_found_retries = 0
        _uv = [None, None]
        _xy = [None, None]
        _olduv = None
        _pixel_offsets = [None, None]
        _offsets = [None, None]
        _rr = None

        try:
            self.pm.ensure_homed()

            if not self.is_calibrated:
                raise self.gcode.error(
                    "Camera not calibrated. Run TV_CALIB_CAMERA first."
                )

            for _retries in range(retries):
                _rr = get_nozzle_position(self.server_url, self.reactor)

                if _rr is None:
                    if _not_found_retries > 3:
                        raise self.gcode.error(
                            "Nozzle not found after 4 wiggle attempts."
                        )
                    gcmd.respond_info(
                        "Nozzle not found, wiggling toolhead..."
                    )
                    if _not_found_retries == 0:
                        self.pm.move_relative(X=0.1)
                    elif _not_found_retries == 1:
                        self.pm.move_relative(X=-0.2)
                    elif _not_found_retries == 2:
                        self.pm.move_relative(X=0.1, Y=0.1)
                    elif _not_found_retries == 3:
                        self.pm.move_relative(Y=-0.2)
                    _not_found_retries += 1
                    continue
                else:
                    _not_found_retries = 0

                _uv = json.loads(_rr["data"])
                if _olduv is None:
                    _olduv = _uv
                _xy = self.pm.get_gcode_position()

                _cx, _cy = normalize_coords(_uv)
                _v = [_cx**2, _cy**2, _cx * _cy, _cx, _cy, 0]
                _offsets = json.loads(
                    calculate_offset_from_matrix(self.server_url, _v)
                )
                _offsets[0] = round(_offsets[0], 3)
                _offsets[1] = round(_offsets[1], 3)

                gcmd.respond_info(
                    "Take %d: X%.2f Y%.2f UV:%s Offset X:%.2f Y:%.2f"
                    % (
                        _retries,
                        round(_xy[0], 2),
                        round(_xy[1], 2),
                        str(_uv),
                        _offsets[0],
                        _offsets[1],
                    )
                )

                if _offsets[0] != 0.0 or _offsets[1] != 0.0:
                    _pixel_offsets[0] = _offsets[0] / self.mpp
                    _pixel_offsets[1] = _offsets[1] / self.mpp

                    if (
                        _pixel_offsets[0] + _uv[0] > self.FRAME_WIDTH
                        or _pixel_offsets[1] + _uv[1] > self.FRAME_HEIGHT
                        or _pixel_offsets[0] + _uv[0] < 0
                        or _pixel_offsets[1] + _uv[1] < 0
                    ):
                        raise self.gcode.error(
                            "Offset would move nozzle outside frame. "
                            "Check mm/px calibration."
                        )

                    _olduv = _uv
                    self.pm.move_relative(
                        X=_offsets[0], Y=_offsets[1], speed=1000
                    )
                    continue

                elif _offsets[0] == 0.0 and _offsets[1] == 0.0:
                    gcmd.respond_info("Nozzle aligned to camera center!")
                    self.last_nozzle_center_successful = True
                    return

        except Exception as e:
            logging.exception(
                "tool_vision _calibrate_nozzle: mpp=%s pixel_offsets=%s "
                "uv=%s offsets=%s olduv=%s xy=%s retries=%s "
                "not_found_retries=%s rr=%s"
                % (
                    self.mpp,
                    _pixel_offsets,
                    _uv,
                    _offsets,
                    _olduv,
                    _xy,
                    _retries,
                    _not_found_retries,
                    _rr,
                )
            )
            raise self.gcode.error(e).with_traceback(e.__traceback__)

    def _get_mm_per_pixel(self, distance_traveled, from_pt, to_pt):
        total_dist = abs(distance_traveled[0]) + abs(distance_traveled[1])
        pixel_dist = get_distance(
            from_pt[0], from_pt[1], to_pt[0], to_pt[1]
        )
        return round(total_dist / pixel_dist, 3)

    def _move_relative_and_get_nozzle_position(self, X, Y, gcmd):
        self.pm.move_relative(X=X, Y=Y)
        result = get_nozzle_position(self.server_url, self.reactor)
        if result is None:
            return None, None
        pos = self.pm.get_gcode_position()
        return result, [pos[0], pos[1]]

    def _save_coordinates_for_matrix(self, space, camera, mpp):
        self.space_coordinates.append(space)
        self.camera_coordinates.append(camera)
        self.mm_per_pixels.append(mpp)

    def _get_average_mpp_from_lists(self, gcmd):
        try:
            result = get_average_mpp(
                self.mm_per_pixels,
                self.space_coordinates,
                self.camera_coordinates,
                gcmd,
            )
            if result is None:
                raise self.gcode.error(
                    "Failed to calculate average mm/pixel."
                )
            mpp, new_mpps, new_space, new_camera = result

            if len(new_mpps) < len(self.mm_per_pixels) * 0.75:
                raise self.gcode.error(
                    "More than 25%% of calibration points failed."
                )

            self.mm_per_pixels = new_mpps
            self.space_coordinates = new_space
            self.camera_coordinates = new_camera
            return mpp
        except Exception as e:
            raise self.gcode.error(
                "Average mm/pixel calculation failed: %s" % str(e)
            ).with_traceback(e.__traceback__)

    # ═══════════════════════════════════════════════════════════
    #  Z PROBE COMMANDS (from Axiscope logic)
    # ═══════════════════════════════════════════════════════════

    def _is_homed(self):
        toolhead = self.printer.lookup_object("toolhead")
        ctime = self.printer.get_reactor().monotonic()
        homed = toolhead.get_kinematics().get_status(ctime)["homed_axes"]
        return all(x in homed for x in "xyz")

    def _has_switch_pos(self):
        return all(
            x is not None for x in [self.z_x_pos, self.z_y_pos, self.z_z_pos]
        )

    def cmd_MOVE_TO_ZSWITCH(self, gcmd):
        """Move toolhead above the Z switch position."""
        if not self._is_homed():
            gcmd.respond_info("Must home first.")
            return
        if not self._has_switch_pos():
            gcmd.respond_error("Z switch positions not configured.")
            return

        gcmd.respond_info("Moving to Z Switch...")
        toolhead = self.printer.lookup_object("toolhead")
        toolhead.wait_moves()
        current_pos = toolhead.get_position()

        self.gcode_move.cmd_G1(
            self.gcode.create_gcode_command(
                "G0",
                "G0",
                {
                    "X": self.z_x_pos,
                    "Y": self.z_y_pos,
                    "Z": current_pos[2],
                    "F": self.z_move_speed * 60,
                },
            )
        )
        toolhead.manual_move(
            [None, None, self.z_z_pos + self.lift_z], self.z_move_speed
        )

    def cmd_PROBE_ZSWITCH(self, gcmd):
        """Probe the Z switch and record the result."""
        toolhead = self.printer.lookup_object("toolhead")
        tool_no = str(self.toolchanger.active_tool.tool_number)
        start_pos = toolhead.get_position()

        z_result = self.probe_multi_axis.run_probe(
            "z-", gcmd, speed_ratio=0.5, max_distance=10.0,
            samples=self.z_samples,
        )[2]

        measured_time = self.printer.get_reactor().monotonic()

        if tool_no == "0":
            self.probe_results[tool_no] = {
                "z_trigger": z_result,
                "z_offset": 0,
                "last_run": measured_time,
            }
        elif "0" in self.probe_results:
            z_offset = z_result - self.probe_results["0"]["z_trigger"]
            self.probe_results[tool_no] = {
                "z_trigger": z_result,
                "z_offset": z_offset,
                "last_run": measured_time,
            }
        else:
            self.probe_results[tool_no] = {
                "z_trigger": z_result,
                "z_offset": None,
                "last_run": measured_time,
            }

        toolhead.move(start_pos, self.z_move_speed)
        toolhead.set_position(start_pos)
        toolhead.wait_moves()

    def cmd_SET_ENDSTOP_POSITION(self, gcmd):
        """Set Z switch endstop position dynamically."""
        toolhead = self.printer.lookup_object("toolhead")
        current_pos = toolhead.get_position()
        use_current = gcmd.get_int("CURRENT", 0)

        x_pos = gcmd.get_float("X", None)
        y_pos = gcmd.get_float("Y", None)
        z_pos = gcmd.get_float("Z", None)

        if use_current:
            if x_pos is None:
                x_pos = current_pos[0]
            if y_pos is None:
                y_pos = current_pos[1]
            if z_pos is None:
                z_pos = current_pos[2]

        set_axes = []
        if x_pos is not None:
            self.z_x_pos = x_pos
            set_axes.append("X=%.3f" % x_pos)
        if y_pos is not None:
            self.z_y_pos = y_pos
            set_axes.append("Y=%.3f" % y_pos)
        if z_pos is not None:
            self.z_z_pos = z_pos
            set_axes.append("Z=%.3f" % z_pos)

        if set_axes:
            gcmd.respond_info(
                "Tool Vision endstop: %s" % " ".join(set_axes)
            )
        else:
            gcmd.respond_info(
                "No axes specified. Use X=, Y=, Z=, or CURRENT=1."
            )

    # ═══════════════════════════════════════════════════════════
    #  COMBINED CALIBRATION COMMANDS
    # ═══════════════════════════════════════════════════════════

    def cmd_CALIBRATE_ALL_Z(self, gcmd):
        """Probe Z offset for all tools (Axiscope CALIBRATE_ALL_Z_OFFSETS)."""
        if not self._is_homed():
            gcmd.respond_info("Must home first.")
            return

        self.cmd_TV_START_GCODE(gcmd)

        for tool_no in self.toolchanger.tool_numbers:
            self.cmd_TV_BEFORE_PICKUP_GCODE(gcmd)
            self.gcode.run_script_from_command("T%i" % tool_no)
            self.cmd_TV_AFTER_PICKUP_GCODE(gcmd)

            self.gcode.run_script_from_command("TV_MOVE_TO_ZSWITCH")
            self.gcode.run_script_from_command(
                "TV_PROBE_ZSWITCH SAMPLES=%i" % self.z_samples
            )

        self.gcode.run_script_from_command("T0")
        toolhead = self.printer.lookup_object("toolhead")
        toolhead.wait_moves()

        for tn in self.probe_results:
            if tn != "0":
                gcmd.respond_info(
                    "T%s gcode_z_offset: %.3f"
                    % (tn, self.probe_results[tn]["z_offset"])
                )

        self.cmd_TV_FINISH_GCODE(gcmd)

    def cmd_CALIBRATE_ALL_XY(self, gcmd):
        """Calibrate XY offset for all tools using camera vision."""
        if not self._is_homed():
            gcmd.respond_info("Must home first.")
            return

        # Send config and calibrate camera on T0
        self.gcode.run_script_from_command("T0")
        self.cmd_SEND_SERVER_CFG(gcmd)
        self._calibrate_px_mm(gcmd)

        if not self.is_calibrated:
            raise self.gcode.error(
                "Camera calibration failed. Cannot proceed."
            )

        # Set T0 as origin
        self._calibrate_nozzle(gcmd)
        self.cmd_SET_ORIGIN(gcmd)

        # Calibrate each tool
        for tool_no in self.toolchanger.tool_numbers:
            if tool_no == 0:
                continue

            gcmd.respond_info("Calibrating T%d XY offset..." % tool_no)
            self.gcode.run_script_from_command("T%i" % tool_no)
            self._calibrate_nozzle(gcmd)
            self.cmd_GET_OFFSET(gcmd)

            gcmd.respond_info(
                "T%d XY offset: X:%.3f Y:%.3f"
                % (
                    tool_no,
                    self.last_calculated_offset[0],
                    self.last_calculated_offset[1],
                )
            )

        self.gcode.run_script_from_command("T0")

    def cmd_CALIBRATE_ALL(self, gcmd):
        """Combined XYZ calibration: Z probe + XY vision for all tools."""
        if not self._is_homed():
            gcmd.respond_info("Must home first.")
            return

        gcmd.respond_info("=== Tool Vision: Starting full XYZ calibration ===")
        self.cmd_TV_START_GCODE(gcmd)

        # ── Phase 1: Camera Calibration on T0 ──
        gcmd.respond_info("Phase 1: Camera calibration on T0...")
        self.gcode.run_script_from_command("T0")
        self.cmd_SEND_SERVER_CFG(gcmd)
        self._calibrate_px_mm(gcmd)

        if not self.is_calibrated:
            raise self.gcode.error("Camera calibration failed.")

        # ── Phase 2: Z + XY for each tool ──
        for tool_no in self.toolchanger.tool_numbers:
            gcmd.respond_info(
                "=== Calibrating T%d ===" % tool_no
            )

            self.cmd_TV_BEFORE_PICKUP_GCODE(gcmd)
            self.gcode.run_script_from_command("T%i" % tool_no)
            self.cmd_TV_AFTER_PICKUP_GCODE(gcmd)

            # Z probe
            if self._has_switch_pos() and self.probe_multi_axis is not None:
                self.gcode.run_script_from_command("TV_MOVE_TO_ZSWITCH")
                self.gcode.run_script_from_command(
                    "TV_PROBE_ZSWITCH SAMPLES=%i" % self.z_samples
                )

            # XY vision
            self._calibrate_nozzle(gcmd)

            if tool_no == 0:
                self.cmd_SET_ORIGIN(gcmd)
                gcmd.respond_info("T0: Set as reference origin.")
            else:
                self.cmd_GET_OFFSET(gcmd)
                z_offset_str = "N/A"
                if str(tool_no) in self.probe_results:
                    z_off = self.probe_results[str(tool_no)].get("z_offset")
                    if z_off is not None:
                        z_offset_str = "%.3f" % z_off

                gcmd.respond_info(
                    "T%d: X:%.3f Y:%.3f Z:%s"
                    % (
                        tool_no,
                        self.last_calculated_offset[0],
                        self.last_calculated_offset[1],
                        z_offset_str,
                    )
                )

        self.gcode.run_script_from_command("T0")
        toolhead = self.printer.lookup_object("toolhead")
        toolhead.wait_moves()

        # ── Summary ──
        gcmd.respond_info("=== Tool Vision: Calibration Summary ===")
        for tn in self.probe_results:
            r = self.probe_results[tn]
            gcmd.respond_info(
                "T%s: Z_trigger=%.3f Z_offset=%s"
                % (
                    tn,
                    r["z_trigger"],
                    "%.3f" % r["z_offset"] if r["z_offset"] is not None else "N/A",
                )
            )

        self.cmd_TV_FINISH_GCODE(gcmd)
        gcmd.respond_info("=== Tool Vision: Calibration Complete! ===")

    # ═══════════════════════════════════════════════════════════
    #  GCODE TEMPLATE COMMANDS (from Axiscope)
    # ═══════════════════════════════════════════════════════════

    def _run_gcode_template(self, name, template, extra_context=None):
        if extra_context is None:
            extra_context = {}
        curtime = self.printer.get_reactor().monotonic()
        context = {
            **template.create_template_context(),
            "tool": (
                self.toolchanger.active_tool.get_status(curtime)
                if self.toolchanger.active_tool
                else {}
            ),
            "toolchanger": self.toolchanger.get_status(curtime),
            "tool_vision": self.get_status(curtime),
            **extra_context,
        }
        template.run_gcode_from_command(context)

    def cmd_TV_START_GCODE(self, gcmd):
        if self.start_gcode:
            self._run_gcode_template("start_gcode", self.start_gcode)

    def cmd_TV_BEFORE_PICKUP_GCODE(self, gcmd):
        if self.before_pickup_gcode:
            self._run_gcode_template(
                "before_pickup_gcode", self.before_pickup_gcode
            )

    def cmd_TV_AFTER_PICKUP_GCODE(self, gcmd):
        if self.after_pickup_gcode:
            self._run_gcode_template(
                "after_pickup_gcode", self.after_pickup_gcode
            )

    def cmd_TV_FINISH_GCODE(self, gcmd):
        if self.finish_gcode:
            self._run_gcode_template("finish_gcode", self.finish_gcode)

    # ═══════════════════════════════════════════════════════════
    #  SAVE/LOAD CONFIG (from Axiscope)
    # ═══════════════════════════════════════════════════════════

    def _update_tool_offsets(self, cfg_data, tool_name, offsets):
        axis = "xyz" if len(offsets) == 3 else "xy"
        section_name = "[%s]" % tool_name
        section_start = None
        section_end = None
        new_section = None

        for i, line in enumerate(cfg_data):
            stripped = line.lstrip()
            if stripped.startswith(section_name):
                section_start = i + 1
            elif section_start is not None:
                if stripped.startswith("["):
                    section_end = i - 1
                    break

        for i, a in enumerate(axis):
            offset_name = "gcode_%s_offset" % a
            offset_value = offsets[i]
            offset_string = "%s: %.3f\n" % (offset_name, offset_value)

            if section_start is not None:
                section_lines = (
                    cfg_data[section_start : section_end + 1]
                    if section_end is not None
                    else cfg_data[section_start:]
                )
                for line in section_lines:
                    if line.lstrip().startswith(offset_name):
                        cfg_data[cfg_data.index(line)] = offset_string
            else:
                if new_section is not None:
                    new_section.append(offset_string)
                else:
                    new_section = ["\n", section_name + "\n", offset_string]

        if new_section is not None:
            new_section.append("\n")
            no_touch_index = None
            if self.config_file_path.endswith("printer.cfg"):
                for line in cfg_data:
                    if line.lstrip().startswith("#*#"):
                        no_touch_index = cfg_data.index(line)
                        break
            if no_touch_index is not None:
                cfg_data = (
                    cfg_data[:no_touch_index]
                    + ["\n"]
                    + new_section
                    + cfg_data[no_touch_index:]
                )
            else:
                cfg_data = cfg_data + ["\n"] + new_section

        return cfg_data

    def cmd_SAVE_TOOL_OFFSET(self, gcmd):
        """Save tool offsets to config file."""
        if not self.has_cfg_data:
            gcmd.respond_info(
                "Tool Vision needs config_file_path to save offsets."
            )
            return
        with open(self.config_file_path, "r") as f:
            cfg_data = f.readlines()

        tool_name = gcmd.get("TOOL_NAME")
        offsets = ast.literal_eval(gcmd.get("OFFSETS"))
        out_data = self._update_tool_offsets(cfg_data, tool_name, offsets)

        gcmd.respond_info("Writing %s offsets..." % tool_name)
        with open(self.config_file_path, "w") as f:
            for line in out_data:
                f.write(line)
        gcmd.respond_info("Offsets written successfully.")

    def cmd_SAVE_MULTIPLE_TOOL_OFFSETS(self, gcmd):
        """Save multiple tool offsets at once."""
        if not self.has_cfg_data:
            gcmd.respond_info(
                "Tool Vision needs config_file_path to save offsets."
            )
            return
        with open(self.config_file_path, "r") as f:
            cfg_data = f.readlines()

        tool_names = gcmd.get("TOOLS")
        offsets = ast.literal_eval(gcmd.get("OFFSETS"))
        out_data = cfg_data

        for i, tool_name in enumerate(tool_names):
            out_data = self._update_tool_offsets(
                out_data, tool_name, offsets[i]
            )

        gcmd.respond_info("Writing offsets for %d tools..." % len(tool_names))
        with open(self.config_file_path, "w") as f:
            for line in out_data:
                f.write(line)
        gcmd.respond_info("Offsets written successfully.")

    # ═══════════════════════════════════════════════════════════
    #  STATUS
    # ═══════════════════════════════════════════════════════════

    def get_status(self, eventtime=None):
        return {
            "last_calculated_offset": self.last_calculated_offset,
            "mm_per_pixel": self.mpp,
            "is_calibrated": self.is_calibrated,
            "send_frame_to_cloud": self.send_frame_to_cloud,
            "camera_center_coordinates": self.cp,
            "travel_speed": self.move_speed,
            "last_nozzle_center_successful": self.last_nozzle_center_successful,
            "probe_results": self.probe_results,
            "can_save_config": self.has_cfg_data is not False,
            "endstop_x": self.z_x_pos,
            "endstop_y": self.z_y_pos,
            "endstop_z": self.z_z_pos,
        }


def load_config(config):
    return ToolVision(config)

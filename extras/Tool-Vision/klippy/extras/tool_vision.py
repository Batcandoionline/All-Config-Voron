import os, json, time
import urllib.request
import urllib.parse
from . import tools_calibrate

class ToolVision:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode_move = self.printer.load_object(config, 'gcode_move')
        
        # Load Z Switch config
        self.z_x = config.getfloat('z_switch_x')
        self.z_y = config.getfloat('z_switch_y')
        self.z_z = config.getfloat('z_switch_z')
        self.z_clearance = config.getfloat('z_clearance', 2.0)
        self.samples = config.getint('z_samples', 3)
        
        # Load Camera config
        self.cam_x = config.getfloat('camera_x')
        self.cam_y = config.getfloat('camera_y')
        self.server_url = config.get('vision_server_url')
        self.camera_stream = config.get('camera_stream_url')
        self.move_speed = config.getfloat('move_speed', 100.0)
        self.z_speed = config.getfloat('z_speed', 15.0)
        
        # Internal states
        self.mpp_x = None  # mm per pixel X
        self.mpp_y = None  # mm per pixel Y
        self.t0_z = None
        self.t0_x = None
        self.t0_y = None
        
        # Setup Probe Multi Axis for Z
        self.probe_multi_axis = tools_calibrate.PrinterProbeMultiAxis(
            config,
            tools_calibrate.ProbeEndstopWrapper(config, 'x'),
            tools_calibrate.ProbeEndstopWrapper(config, 'y'),
            tools_calibrate.ProbeEndstopWrapper(config, 'z')
        )
        query_endstops = self.printer.load_object(config, 'query_endstops')
        query_endstops.register_endstop(self.probe_multi_axis.mcu_probe[-1].mcu_endstop, "ToolVision")
        
        # Ensure toolchanger is loaded later
        self.printer.register_event_handler("klippy:ready", self.handle_ready)
        
        self.gcode.register_command('TOOL_VISION_CALIBRATE_ALL', self.cmd_TOOL_VISION_CALIBRATE_ALL, desc="Đo đồng thời XYZ cho tất cả các Tool")
        
    def handle_ready(self):
        self.toolchanger = self.printer.lookup_object('toolchanger')

    def _fetch_nozzle_pos(self, wiggle=False):
        url = f"{self.server_url}/detect?camera_url={urllib.parse.quote(self.camera_stream, safe='')}"
        
        for attempt in range(5):
            try:
                req = urllib.request.urlopen(url, timeout=5)
                res = json.loads(req.read())
                if res.get('status') == 'ok':
                    return res['x'], res['y']
            except Exception as e:
                pass
                
            if wiggle:
                self.gcode.respond_info(f"Không thấy kim phun, tiến hành lắc (wiggle) lần {attempt + 1}/5...")
                pos = self.toolhead.get_position()
                # Di chuyển nhích qua nhích lại 0.5mm
                wiggle_offset = 0.5 if attempt % 2 == 0 else -0.5
                self._move_absolute(pos[0] + wiggle_offset, pos[1] + wiggle_offset, pos[2], self.move_speed)
                time.sleep(0.5)
                self._move_absolute(pos[0], pos[1], pos[2], self.move_speed)
                time.sleep(0.5)
            else:
                break
                
        return None, None

    def _move_absolute(self, x, y, z, speed):
        self.toolhead.manual_move([x, y, z], speed)
        self.toolhead.wait_moves()

    def _probe_z(self, gcmd):
        pos = self.toolhead.get_position()
        # Move above switch
        self._move_absolute(self.z_x, self.z_y, pos[2], self.move_speed)
        self._move_absolute(self.z_x, self.z_y, self.z_z + self.z_clearance, self.z_speed)
        
        # Probe
        z_result = self.probe_multi_axis.run_probe("z-", gcmd, speed_ratio=0.5, max_distance=10.0, samples=self.samples)[2]
        
        # Lift up
        self._move_absolute(self.z_x, self.z_y, self.z_z + self.z_clearance, self.z_speed)
        return z_result

    def _calibrate_camera_mpp(self, gcmd):
        """ Tính toán tỷ lệ mm/pixel bằng cách di chuyển đầu in 1mm """
        gcmd.respond_info("Đang tính toán tỷ lệ mm/pixel của Camera...")
        self._move_absolute(self.cam_x, self.cam_y, self.toolhead.get_position()[2], self.move_speed)
        
        px1, py1 = self._fetch_nozzle_pos(wiggle=True)
        if px1 is None:
            raise self.gcode.error("Không tìm thấy kim phun ở tâm Camera.")
            
        # Di chuyển X thêm 1mm
        self._move_absolute(self.cam_x + 1.0, self.cam_y, self.toolhead.get_position()[2], self.move_speed)
        px2, py2 = self._fetch_nozzle_pos(wiggle=True)
        if px2 is None:
            raise self.gcode.error("Mất dấu kim phun khi di chuyển X.")
            
        self.mpp_x = abs(1.0 / (px2 - px1)) if px2 != px1 else 0.01
        
        # Di chuyển Y thêm 1mm
        self._move_absolute(self.cam_x, self.cam_y + 1.0, self.toolhead.get_position()[2], self.move_speed)
        px3, py3 = self._fetch_nozzle_pos(wiggle=True)
        if px3 is None:
            raise self.gcode.error("Mất dấu kim phun khi di chuyển Y.")
            
        self.mpp_y = abs(1.0 / (py3 - py2)) if py3 != py2 else 0.01
        
        gcmd.respond_info(f"Đã tính mm/px thành công! X: {self.mpp_x:.5f}, Y: {self.mpp_y:.5f}")
        
        # Quay về tâm
        self._move_absolute(self.cam_x, self.cam_y, self.toolhead.get_position()[2], self.move_speed)

    def _align_to_center(self, gcmd):
        """ Di chuyển kim phun vào chính giữa camera (320, 240) """
        target_px_x, target_px_y = 320, 240
        for _ in range(5):
            px, py = self._fetch_nozzle_pos(wiggle=True)
            if px is None:
                raise self.gcode.error("Không tìm thấy kim phun khi căn chỉnh tâm.")
                
            dx_px = target_px_x - px
            dy_px = target_px_y - py
            
            # Klipper Y axis often inverted relative to camera Y axis.
            # We assume standard orientation but might need tweak.
            # Assuming camera +X = machine +X, camera +Y = machine -Y
            dx_mm = dx_px * self.mpp_x
            dy_mm = dy_px * self.mpp_y * -1.0 
            
            if abs(dx_mm) < 0.02 and abs(dy_mm) < 0.02:
                break
                
            pos = self.toolhead.get_position()
            self._move_absolute(pos[0] + dx_mm, pos[1] + dy_mm, pos[2], self.move_speed)
            time.sleep(0.5)

    def _save_tool_offset(self, tool_id, axis, value):
        self.gcode.run_script_from_command(f"SET_TOOL_PARAMETER T={tool_id} PARAMETER=gcode_{axis}_offset VALUE={value}")
        self.gcode.run_script_from_command(f"SAVE_TOOL_PARAMETER T={tool_id} PARAMETER=gcode_{axis}_offset")

    def cmd_TOOL_VISION_CALIBRATE_ALL(self, gcmd):
        self.toolhead = self.printer.lookup_object('toolhead')
        kin_status = self.toolhead.get_kinematics().get_status(self.printer.get_reactor().monotonic())
        if "x" not in kin_status["homed_axes"] or "z" not in kin_status["homed_axes"]:
            gcmd.respond_error("Máy chưa được home toàn bộ.")
            return

        # 1. Lấy T0 làm mốc chuẩn
        gcmd.respond_info("Đang lấy mốc T0...")
        self.gcode.run_script_from_command("T0")
        
        self.t0_z = self._probe_z(gcmd)
        
        self._calibrate_camera_mpp(gcmd)
        self._align_to_center(gcmd)
        
        t0_pos = self.toolhead.get_position()
        self.t0_x = t0_pos[0]
        self.t0_y = t0_pos[1]
        
        gcmd.respond_info(f"Mốc T0 hoàn tất: Z={self.t0_z:.3f}, Camera XY=({self.t0_x:.3f}, {self.t0_y:.3f})")

        # 2. Lặp qua các Tool còn lại
        for tool_no in self.toolchanger.tool_numbers:
            if str(tool_no) == "0":
                continue
                
            gcmd.respond_info(f"Đang đo Tool T{tool_no}...")
            self.gcode.run_script_from_command(f"T{tool_no}")
            
            # Z
            tz = self._probe_z(gcmd)
            z_offset = tz - self.t0_z
            self._save_tool_offset(tool_no, 'z', z_offset)
            
            # XY
            self._move_absolute(self.cam_x, self.cam_y, self.toolhead.get_position()[2], self.move_speed)
            self._align_to_center(gcmd)
            t_pos = self.toolhead.get_position()
            
            x_offset = self.t0_x - t_pos[0]
            y_offset = self.t0_y - t_pos[1]
            
            self._save_tool_offset(tool_no, 'x', x_offset)
            self._save_tool_offset(tool_no, 'y', y_offset)
            
            gcmd.respond_info(f"T{tool_no} hoàn tất! Lưu Offset: X={x_offset:.3f}, Y={y_offset:.3f}, Z={z_offset:.3f}")

        # Quay lại T0
        self.gcode.run_script_from_command("T0")
        gcmd.respond_info("Quá trình Tool Vision hoàn tất!")

def load_config(config):
    return ToolVision(config)

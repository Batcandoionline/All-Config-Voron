"""Offline reproductions against TKC b6c3328; no printer/network operations.

Usage: python reproduce_remaining.py /path/to/Tool-Klipper-Calibration
Fixtures are upstream dummy printer objects. Findings are observations, not fixes.
"""
import json
import pathlib
import sys
import tempfile
from unittest.mock import MagicMock

source = pathlib.Path(sys.argv[1]).resolve()
sys.path[:0] = [str(source), str(source / 'tests')]
from test_calibration_cycle import DummyConfig, DummyGCode, DummyGCodeCommand, DummyPrinter, DummyToolhead
from klippy.extras.tool_calibrator import ToolCalibrator
from klippy.extras.safe_navigator import SafeNavigatorException

findings = {}
with tempfile.TemporaryDirectory(prefix='tkc-offline-') as tmp:
    def make():
        th = DummyToolhead()
        p = DummyPrinter(th, DummyGCode())
        cfg = DummyConfig(p, {'safe_z':40.0, 'camera_x':150.0, 'camera_y':10.0,
                              'offset_config_path':str(pathlib.Path(tmp)/'station.cfg')})
        c = ToolCalibrator(cfg)
        c._ensure_vision_sync = lambda: None
        c._set_inspection_lighting = lambda *a: None
        return c, th, p

    # Calibration offset is raw target carriage minus reference carriage.
    # A +0.865 X result therefore requires reference station X + 0.865.
    c, th, p = make()
    c.navigator.switch_target_x = 68.0
    c.navigator.switch_target_y = 10.0
    c.navigator.switch_target_z = 7.0
    c.navigator.approach_switch(th, p.gcode_move, offset_xy=(0.865,0.285))
    findings['z_xy_sign'] = {'actual_carriage_xy':th.pos[:2],
                             'required_from_measured_carriage_delta':[68.865,10.285]}
    assert th.pos[0] == 67.135

    # Health failure after acquiring a session lies outside the cleanup finally.
    c, th, p = make()
    calls = []
    def fail_health(endpoint, payload=None, timeout=2.0):
        calls.append(endpoint)
        if endpoint == 'acquire_lock': return {'session_token':'owned'}
        if endpoint == 'health': raise SafeNavigatorException('injected health failure')
        return {}
    c._query_vision = fail_health
    try: c.cmd_CALIBRATE_TOOL_OFFSETS(DummyGCodeCommand({'CALIBRATE_Z':0,'SAVE_CONFIG':0}))
    except Exception: pass
    findings['preflight_cleanup'] = {'calls':calls,'session_token':c.session_token,'record':c.run_record}
    assert 'release_lock' not in calls and c.session_token == 'owned'

    # Camera scale ignores failed lock acquisition and enters the station anyway.
    c, th, p = make()
    c._query_vision = MagicMock(side_effect=SafeNavigatorException('injected lock conflict'))
    c.navigator.approach_camera = MagicMock(side_effect=SafeNavigatorException('stop before dummy motion'))
    try: c.cmd_CALIBRATE_CAMERA_SCALE(DummyGCodeCommand({'DISTANCE':0.5}))
    except Exception: pass
    findings['scale_lock_failure'] = {'approach_called_after_lock_error':c.navigator.approach_camera.called}
    assert c.navigator.approach_camera.called

    # Scale persists and prints SUCCESS even when post-fit centering fails.
    c, th, p = make()
    c._sample_burst = MagicMock(side_effect=[{'found':True,'center_uv':uv} for uv in
        [[320,240],[298,240],[342,240],[320,218],[320,262]]])
    def scale_query(endpoint, payload=None, timeout=2.0):
        if endpoint == 'acquire_lock': return {'session_token':'owned'}
        if endpoint == 'calibrate_mpp': return {'mpp':0.023}
        if endpoint == 'solve_matrix': return {'success':True,'matrix':[[-7.36,0,0],[0,-5.52,0]]}
        return {}
    c._query_vision = scale_query
    c._center_nozzle = MagicMock(side_effect=SafeNavigatorException('injected ERR_CV_202'))
    cmd = DummyGCodeCommand({'DISTANCE':0.5})
    c.cmd_CALIBRATE_CAMERA_SCALE(cmd)
    findings['scale_success_after_center_failure'] = cmd.info_messages[-2:]
    assert any('CAMERA CALIBRATION SUCCESS' in m for m in cmd.info_messages)

    # At this camera scale, a 5px spread is 0.115mm, still accepted by the 6px floor.
    c, th, p = make()
    c.calibrated_mpp = 0.023
    c._query_vision = MagicMock(side_effect=[{'found':True,'center_uv':uv} for uv in
                                            [[320,240],[320,245],[320,240]]])
    burst = c._sample_burst(th,samples=3)
    findings['burst_physical_spread'] = {'burst':burst,'spread_mm':burst['spread_px']*c.calibrated_mpp}
    assert burst['found'] and burst['spread_px'] == 5

print(json.dumps(findings,indent=2))

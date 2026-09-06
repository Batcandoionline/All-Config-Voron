"""Read-only installation audit. Run with the printer's tkc-env Python.

No movement, service restart, config edit, dependency installation or offset apply.
The include-path check invokes only Klipper's config file reader.
"""
import ast
import importlib.metadata as metadata
import json
import pathlib
import subprocess
import sys
import time
import urllib.request

p = pathlib.Path.home()
repo = p / 'Tool-Klipper-Calibration'
def sh(args):
    r = subprocess.run(args, capture_output=True, text=True)
    return {'exit': r.returncode, 'stdout': r.stdout.strip(), 'stderr': r.stderr.strip()}
def api(path):
    with urllib.request.urlopen('http://127.0.0.1:7125' + path, timeout=15) as response:
        return json.load(response)

status = api('/printer/objects/query?tool_calibrator&toolchanger&toolhead&webhooks&configfile')['result']['status']
settings = status.pop('configfile')['settings']
commands = api('/printer/gcode/help')['result']
names = ['CALIBRATE_TOOL_OFFSETS', 'CALIBRATE_CAMERA_SCALE', 'CALIBRATION_ABORT',
         'TKC_TEST_XY', 'TKC_STATUS', 'CALIBRATE_ALL_TOOLS', 'CALIBRATE_TOOLS_XY',
         'CALIBRATE_TOOL_XY', 'CALIBRATE_CAMERA', 'GOTO_CAMERA_TARGET']
def section(name):
    return next((v for k, v in settings.items() if k.lower() == name.lower()), None)

links = {}
for name in ['tool_calibrator.py', 'tool_calibrator_station.py', 'tool_offsets.py',
             'safe_navigator.py', 'config_manager.py', 'z_backends']:
    f = p / 'klipper/klippy/extras' / name
    links[name] = {'symlink': f.is_symlink(), 'resolved': str(f.resolve()), 'exists': f.exists()}

import cv2
import numpy
packages = {}
for name in ['flask', 'waitress', 'numpy', 'requests', 'urllib3', 'opencv-python-headless', 'opencv-python']:
    try:
        packages[name] = metadata.version(name)
    except metadata.PackageNotFoundError:
        packages[name] = None

pid = sh(['systemctl', '--user', 'show', 'tool-calibrator-experiment', '--property=MainPID', '--value'])['stdout']
klipper_pid = sh(['systemctl', 'show', 'klipper', '--property=MainPID', '--value'])['stdout']
conf = (p / 'printer_data/config/printer.cfg').read_text()
moon = (p / 'printer_data/config/moonraker.conf').read_text()
asvc = p / 'printer_data/moonraker.asvc'

# Reproduce the guide's tilde include handling with the installed parser only.
sys.path.insert(0, str(p / 'klipper/klippy'))
import configfile
reader = configfile.ConfigFileReader()
include_spec = '~/Tool-Klipper-Calibration/macros/tool_calibrator_macros.cfg'
try:
    include_result = reader._resolve_include(str(p / 'printer_data/config/printer.cfg'),
                                            include_spec, reader._create_fileconfig(), set())
except Exception as exc:
    include_result = str(exc)

# Static option reads: the guide's names are not recognized by these modules.
option_reads = {}
for name in ['tool_calibrator.py', 'safe_navigator.py', 'tool_calibrator_station.py']:
    tree = ast.parse((repo / 'klippy/extras' / name).read_text())
    option_reads[name] = sorted({n.args[0].value for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name) and n.func.value.id == 'config'
        and n.func.attr.startswith('get') and n.args
        and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)})

result = {
    'audit_time': time.time(), 'host': sh(['hostname'])['stdout'],
    'source_head': sh(['git', '-C', str(repo), 'rev-parse', 'HEAD'])['stdout'],
    'source_diff': sh(['git', '-C', str(repo), 'diff'])['stdout'],
    'user_services': sh(['systemctl', '--user', 'show', 'tool-calibrator-experiment.service',
        'ktamv-server.service', '--property=Id,ActiveState,SubState,UnitFileState,MainPID,ExecStart,FragmentPath']),
    'standard_system_service': sh(['systemctl', 'show', 'tool_calibrator.service', '--property=LoadState,ActiveState,FragmentPath']),
    'linger': sh(['loginctl', 'show-user', 'voron', '--property=Linger']),
    'daemon_process_cmdline': pathlib.Path('/proc/' + pid + '/cmdline').read_bytes().replace(b'\0', b' ').decode(),
    'klipper_process_cmdline': pathlib.Path('/proc/' + klipper_pid + '/cmdline').read_bytes().replace(b'\0', b' ').decode(),
    'symlinks': links,
    'health': json.load(urllib.request.urlopen('http://127.0.0.1:8090/health', timeout=15)),
    'printer_status': status, 'commands': {n: commands.get(n) for n in names},
    'runtime_tkc_config': section('tool_calibrator'),
    'runtime_tkc_wrapper': section('gcode_macro TKC_TEST_XY'),
    'runtime_optional_macros': {n: section('gcode_macro ' + n) for n in names[5:]},
    'printer_includes': [l for l in conf.splitlines() if l.startswith('[include')
                         and any(n in l.lower() for n in ['tkc', 'calibrat', 'ktamv'])],
    'updater_present': '[update_manager tool_calibrator]' in moon,
    'asvc_tkc_entries': [l for l in asvc.read_text().splitlines() if 'calibrat' in l.lower()] if asvc.exists() else [],
    'python_runtime': {'python': sys.version, 'executable': sys.executable,
        'prefix': sys.prefix, 'base_prefix': sys.base_prefix, 'cv2_version': cv2.__version__,
        'cv2_file': cv2.__file__, 'numpy_file': numpy.__file__, 'packages': packages},
    'venv_cfg': (p / 'tkc-env/pyvenv.cfg').read_text(),
    'dpkg_opencv': sh(['dpkg-query', '-W', 'python3-opencv']),
    'guide_tilde_include_result': include_result,
    'module_option_reads': option_reads,
    'declared_requirements': (repo / 'server/requirements.txt').read_text(),
}
print(json.dumps(result, indent=2))

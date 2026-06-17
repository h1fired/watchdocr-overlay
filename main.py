from frontend.core import GuiCoreApplication
from frontend.utils import ghotkey
from src.core import WatchdOcrCore
from qt.utils import invokeFunc
from config import config
import importlib
import subprocess
import sys

try:
    from frontend import qresources as _res
except ImportError as e:
    raise ImportError(
        'Resources modules not found. Maybe '
        'you forgot to compile the resource files?'
    ) from e


if __name__ == '__main__':
    if config.DEBUG:
        cmd = ' '.join((
            sys.executable,
            '-B ./tools/resources.py',
            '--generate',
            '--compile',
            '--noautoinit'
        ))
        subprocess.run(cmd, check=True)
        importlib.reload(_res)
        _res.qInitResources()

    core = WatchdOcrCore()
    core.initialize()

    gui = GuiCoreApplication()
    gui.load(core.api_collection(), core.event_system())

    # Install global keyboard events hook
    ghotkey.install_keyboard_hook_proc()

    @invokeFunc
    def toggle_window_visibility():
        system_obj = gui.system_obj()
        system_obj.requestVisibilitySwap()

    ghotkey.bind(config.WINDOW_TOGGLE_HOTKEY, toggle_window_visibility)

    sys.exit(gui.exec())

from frontend.core import GuiCoreApplication
from frontend.utils import ghotkey
from src.core import WatchdOcrCore
from src.utils.sysbehavior import SingleInstance
from config import config
import subprocess
import sys
import ctypes


ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('company.app.1')


def show_overlay():
    gui = GuiCoreApplication()
    gui.system_obj().setVisible(True)


if __name__ == '__main__':
    if config.DEBUG:
        cmd = ' '.join((
            sys.executable,
            '-B ./tools/resources.py',
            '--generate',
            '--compile'
        ))
        subprocess.run(cmd, check=True)

        from frontend import qresources as _res
        _res.qInitResources()
    else:
        try:
            from frontend import qresources as _res
            _res.qInitResources()
        except ImportError as e:
            raise ImportError(
                'Resources modules not found. Maybe '
                'you forgot to compile the resource files?'
            ) from e

    core = WatchdOcrCore()
    core.initialize()

    gui = GuiCoreApplication()

    # Check for single application instance
    guard = SingleInstance(config.APP_ID)
    if not guard.try_run():
        sys.exit(0)

    guard.activate_requested.connect(show_overlay)

    # Load GUI core
    gui.load(core.api_collection(), core.event_system())

    # Install global keyboard events hook
    ghotkey.install_keyboard_hook_proc()

    sys.exit(gui.exec())

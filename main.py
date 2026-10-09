from frontend.core import GuiCoreApplication
from frontend.utils import ghotkey
from frontend.utils.sysbehavior import SingleInstance
from config import config
import subprocess
import sys
import ctypes
import argparse


ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('company.app.1')


def precompile_resources():
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


def show_overlay():
    gui = GuiCoreApplication()
    gui.system_obj().setVisible(True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=config.APP_NAME)
    parser.add_argument('--hide-on-exec', action='store_true')
    args = parser.parse_args()

    if config.BACKEND_IS_LOCAL:
        from src.backend.runner import run_server
        run_server(config.BACKEND_HOST, config.BACKEND_PORT)

    precompile_resources()

    gui = GuiCoreApplication()
    gui.pre_init()

    # Check for single application instance
    guard = SingleInstance(config.APP_ID)
    if not guard.try_run():
        sys.exit(0)

    guard.activate_requested.connect(show_overlay)

    gui.tray().setShowActiveVisible(True)
    gui.load()  # Load GUI core

    # Install global keyboard events hook
    ghotkey.install_keyboard_hook_proc()

    sys_obj = gui.system_obj()
    if not args.hide_on_exec:
        sys_obj.setVisible(True)
    else:
        sys_obj.setWindowTransparentForInput(True)

    sys.exit(gui.exec())

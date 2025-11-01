from qt.utils import invokeFunc
from frontend.core import GuiCoreApplication
from frontend.utils import ghotkey
from src.app import CoreApplication
from config import config
import sys
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='MD Control')
    parser.add_argument('--notray', action='store_true', help='disable tray')
    args = parser.parse_args()

    core = CoreApplication()
    core.init()

    gui_core = GuiCoreApplication()
    gui_core.init(core.accessor(), core.event_system(), args.notray)

    # Install global keyboard events hook
    ghotkey.install_keyboard_hook_proc()

    @invokeFunc
    def toggle_window_visibility():
        system_obj = gui_core.system_object()
        system_obj.requestVisibilityChange()

    ghotkey.bind(config.WINDOW_TOGGLE_HOTKEY, toggle_window_visibility)

    # Run application
    sys.exit(gui_core.exec())

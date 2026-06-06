from frontend.core import GuiCoreApplication
from frontend.utils import ghotkey
from src.core import WatchdOcrCore
from qt.utils import invokeFunc
from config import config
import sys


if __name__ == '__main__':
    core = WatchdOcrCore()
    core.initialize()

    gui = GuiCoreApplication()
    gui.load(core.context())

    # Install global keyboard events hook
    ghotkey.install_keyboard_hook_proc()

    @invokeFunc
    def toggle_window_visibility():
        system_obj = gui.system_obj()
        system_obj.requestVisibilityChange()

    ghotkey.bind(config.WINDOW_TOGGLE_HOTKEY, toggle_window_visibility)

    sys.exit(gui.exec())

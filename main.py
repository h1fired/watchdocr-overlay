from frontend.core import GuiCoreApplication
from src.core import WatchdOcrCore
import sys


if __name__ == '__main__':
    core = WatchdOcrCore()
    core.initialize()

    gui = GuiCoreApplication()
    gui.load(core.eventsys())
    sys.exit(gui.exec())

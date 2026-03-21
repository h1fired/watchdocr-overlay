from frontend.core import GuiCoreApplication
import sys


if __name__ == '__main__':
    gui = GuiCoreApplication()
    gui.load()
    sys.exit(gui.exec())

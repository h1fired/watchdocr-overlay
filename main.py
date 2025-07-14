from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject
from src.app import CoreApplication
from frontend.viewmodels.ocroverlay import OCROverlayViewModel
from config import config
import sys


class SystemTray(QObject):
    def __init__(self, window, app):
        super().__init__(window)

        self.tray = QSystemTrayIcon(QIcon("resources/icons/tray.svg"), app)
        self.tray.show()

        self.menu = QMenu()
        self.show_action = QAction("Show")
        self.quit_action = QAction("Quit")

        self.show_action.triggered.connect(window.show)
        self.quit_action.triggered.connect(app.quit)

        self.menu.addAction(self.show_action)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)


if __name__ == '__main__':
    core = CoreApplication()
    core.init()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    engine = QQmlApplicationEngine()

    # Load viewmodels
    viewmodels = (OCROverlayViewModel,)
    viewmodels_objs = []
    for vm in viewmodels:
        obj = vm(engine, core.accessor(), core.event_system())
        obj.load()
        viewmodels_objs.append(obj)

    # Load QML window
    engine.load(config.QML_WINDOW_FILE)
    if not engine.rootObjects():
        sys.exit(-1)

    # Create tray
    tray = SystemTray(engine.rootObjects()[0], app)

    # Run GUI
    sys.exit(app.exec())

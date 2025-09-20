from qt.qml import QQmlApplicationEngine
from qt.core import QObject, QIcon, QAction, QApplication, QSystemTrayIcon, QMenu, Signal
from qt.utils import invokeFunc
from src.app import CoreApplication
from frontend.viewmodels.ocroverlay import OCROverlayViewModel
from frontend.utils import ghotkey
from config import config
import sys
import argparse


class SystemTray(QObject):
    def __init__(self, window, app):
        super().__init__(window)

        self.tray = QSystemTrayIcon(QIcon("resources/icons/tray.svg"), app)

        self.menu = QMenu()
        self.show_action = QAction("Show")
        self.quit_action = QAction("Quit")

        self.show_action.triggered.connect(window.show)
        self.quit_action.triggered.connect(app.quit)

        self.menu.addAction(self.show_action)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)

    def show(self):
        self.tray.show()


class SystemObject(QObject):
    visibilityChanged = Signal()

    def requestVisibilityChange(self):
        self.visibilityChanged.emit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='MD Control')
    parser.add_argument('--notray', action='store_true', help='disable tray')
    args = parser.parse_args()

    core = CoreApplication()
    core.init()

    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Load viewmodels
    viewmodels = (OCROverlayViewModel,)
    viewmodels_objs = []
    for vm in viewmodels:
        obj = vm(engine, core.accessor(), core.event_system())
        obj.load()
        viewmodels_objs.append(obj)

    # Pass system object to QML
    system_obj = SystemObject(app)
    engine.rootContext().setContextProperty('system', system_obj)

    # Load QML window
    engine.load(config.QML_WINDOW_FILE)
    if not engine.rootObjects():
        sys.exit(-1)

    # Create tray
    if not args.notray:
        app.setQuitOnLastWindowClosed(False)
        tray = SystemTray(engine.rootObjects()[0], app)
        tray.show()

    # Register open/close hotkey
    window = engine.rootObjects()[0]

    # Install global keyboard events hook
    ghotkey.install_keyboard_hook_proc()

    @invokeFunc
    def toggle_window_visibility():
        system_obj.requestVisibilityChange()
    ghotkey.bind(config.WINDOW_TOGGLE_HOTKEY, toggle_window_visibility)

    # Run GUI
    sys.exit(app.exec())

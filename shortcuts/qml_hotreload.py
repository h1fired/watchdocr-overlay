from qt.qml import QQmlApplicationEngine
from qt.core import QApplication, QObject
from qt.utils import invokeFunc
from frontend.utils import ghotkey
from config import config
import sys
import time


RELOAD_HOTKEY = 'Alt+B'


if __name__ == '__main__':
    ghotkey.install_keyboard_hook_proc()

    app = QApplication([])
    engine = QQmlApplicationEngine()
    engine.load(config.QML_WINDOW_FILE)
    if not engine.rootObjects():
        raise RuntimeError('Failed to load QML window')

    window = engine.rootObjects()[0]
    loader = window.findChild(QObject, "windowContentLoader")

    @invokeFunc
    def reload():
        engine.clearComponentCache()

        loader.setProperty("source", "")
        loader.setProperty("source", f"Component.qml?t={time.time()}")

    reload()

    ghotkey.bind(RELOAD_HOTKEY, reload)

    sys.exit(app.exec())

from qt.core import QApplication, QUrl, QTimer
from qt.qml import QQmlApplicationEngine
from qt.utils import invokeFunc
from frontend.utils import ghotkey
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, parent_dir)

from frontend import core


QML_FILE = 'frontend/ui/WindowHotReload.qml'
RELOAD_HOTKEY = 'Alt+B'

engine = None


def load():
    global engine

    engine = QQmlApplicationEngine()
    engine.clearComponentCache()
    engine.load(QUrl.fromLocalFile(QML_FILE))


@invokeFunc
def reload():
    global engine

    if engine:
        for obj in engine.rootObjects():
            obj.deleteLater()
        engine.deleteLater()
        engine = None

    QTimer.singleShot(1, load)


def main():
    global engine

    app = QApplication(sys.argv)

    load()

    ghotkey.install_keyboard_hook_proc()
    ghotkey.bind(RELOAD_HOTKEY, reload)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

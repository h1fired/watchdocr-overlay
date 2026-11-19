from qt.core import QApplication, QUrl, QTimer
from qt.qml import QQmlApplicationEngine
from qt.utils import invokeFunc
from frontend.utils import ghotkey
import qasync
import asyncio
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


async def setup():
    load()

    await ghotkey.install_keyboard_hook_proc()
    ghotkey.bind(RELOAD_HOTKEY, reload)


def main():
    app = QApplication(sys.argv)

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        loop.run_until_complete(setup())
        sys.exit(loop.run_forever())


if __name__ == '__main__':
    main()

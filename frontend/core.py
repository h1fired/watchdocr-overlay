from common.utils.meta import Singleton
from qt.qml import QQmlApplicationEngine
from qt.core import QApplication, QObject, Signal
from config import config


class GuiCoreApplication(metaclass=Singleton):
    def __init__(self):
        pass

    def load(self):
        app = QApplication([])

        engine = QQmlApplicationEngine()
        engine.load(config.QML_WINDOW_FILE)
        if not engine.rootObjects():
            raise RuntimeError('Failed to load QML window')

        self._app = app
        self._engine = engine

    def exec(self):
        return self._app.exec()

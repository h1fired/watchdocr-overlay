from common.utils.meta import Singleton
from qt.qml import QQmlApplicationEngine, qmlRegisterSingletonType
from qt.core import QApplication, QUrl
from config import config


qmlRegisterSingletonType(QUrl.fromLocalFile('frontend/ui/Gui.qml'), 'App.Gui', 1, 0, 'Gui')


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

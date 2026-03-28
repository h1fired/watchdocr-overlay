from common.utils.meta import Singleton
from qt.qml import (
    QQmlApplicationEngine,
    qmlRegisterSingletonType,
    qmlRegisterSingletonInstance
)
from qt.core import QApplication, QUrl
from config import config
from frontend.viewmodels import WatchdOcrLinkerCore
from src.common.event import EventSystem


_qmlLinkerCore = WatchdOcrLinkerCore()
qmlRegisterSingletonInstance(WatchdOcrLinkerCore, 'App.Backend', 1, 0, 'Backend', _qmlLinkerCore)
qmlRegisterSingletonType(QUrl.fromLocalFile('frontend/ui/Gui.qml'), 'App.Gui', 1, 0, 'Gui')


class GuiCoreApplication(metaclass=Singleton):
    def load(
        self,
        eventsys: EventSystem,
        load_viewmodels=True
    ):
        app = QApplication([])

        engine = QQmlApplicationEngine()
        engine.load(config.QML_WINDOW_FILE)
        if not engine.rootObjects():
            raise RuntimeError('Failed to load QML window')

        self._app = app
        self._engine = engine
        self._window = engine.rootObjects()[0]

        self._eventsys = eventsys

        if load_viewmodels:
            _qmlLinkerCore.initialize(self._window, eventsys)
            _qmlLinkerCore.loadContent()
            _qmlLinkerCore.loadFullyContent()

    def destroy(self):
        _qmlLinkerCore.destroyContent()

        if not self._engine:
            raise RuntimeError('GUI already destroyed')
        del self._engine
        self._engine = None

    def exec(self):
        return self._app.exec()

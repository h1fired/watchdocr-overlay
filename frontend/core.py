from common.utils.meta import Singleton
from qt.qml import (
    QQmlApplicationEngine,
    qmlRegisterSingletonType,
    qmlRegisterSingletonInstance
)
from qt.core import QApplication, QUrl, QObject, Signal
from src.common.api import KernelAPICollection
from src.common.event import EventSystem
from frontend.ui.tray import SystemTray
from frontend.viewmodels import WatchdOcrLinkerCore
from frontend.viewmodels.types import registerUtilsQmlTypes
from config import config


_qmlLinkerCore = WatchdOcrLinkerCore()
qmlRegisterSingletonInstance(WatchdOcrLinkerCore, 'App.Backend', 1, 0, 'Backend', _qmlLinkerCore)
qmlRegisterSingletonType(QUrl.fromLocalFile('frontend/ui/Gui.qml'), 'App.Gui', 1, 0, 'Gui')
registerUtilsQmlTypes()


class SystemObject(QObject):
    visibilityChanged = Signal()

    def requestVisibilityChange(self):
        self.visibilityChanged.emit()


_qmlSystemObj = SystemObject()
qmlRegisterSingletonInstance(WatchdOcrLinkerCore, 'App.System', 1, 0, 'System', _qmlSystemObj)


class GuiCoreApplication(metaclass=Singleton):
    def __init__(self):
        self._tray = None

    def load(
        self,
        api_collection: KernelAPICollection,
        eventsys: EventSystem,
        load_viewmodels=True,
        notray=False
    ):
        app = QApplication([])

        engine = QQmlApplicationEngine()
        engine.load(config.QML_WINDOW_FILE)
        if not engine.rootObjects():
            raise RuntimeError('Failed to load QML window')

        self._app = app
        self._engine = engine
        self._window = engine.rootObjects()[0]

        if not notray:
            app.setQuitOnLastWindowClosed(False)
            self._tray = SystemTray(self._window, app)

        if load_viewmodels:
            _qmlLinkerCore.initialize(self._window, api_collection, eventsys)
            _qmlLinkerCore.loadContent()
            _qmlLinkerCore.loadFullyContent()

    def destroy(self):
        _qmlLinkerCore.destroyContent()

        if not self._engine:
            raise RuntimeError('GUI already destroyed')
        del self._engine
        self._engine = None

    def exec(self):
        if self._tray:
            self._tray.show()
        return self._app.exec()

    def window(self):
        return self._window

    def system_obj(self):
        return _qmlSystemObj

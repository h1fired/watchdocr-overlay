from common.utils.meta import Singleton
from qt.qml import (
    QQmlApplicationEngine,
    qmlRegisterSingletonType,
    qmlRegisterSingletonInstance
)
from qt.core import QApplication, QUrl, QObject, Signal, Property
from src.common.api import KernelAPICollection
from src.common.event import EventSystem
from frontend.ui.tray import SystemTray
from frontend.viewmodels import WatchdOcrLinkerCore
from frontend.viewmodels.types.focus import FocusHelper
from frontend.viewmodels.types import (
    registerUtilsQmlTypes,
    registerQmlImageProviders
)
from config import config


_qmlLinkerCore = WatchdOcrLinkerCore()
qmlRegisterSingletonInstance(WatchdOcrLinkerCore, 'App.Backend', 1, 0, 'Backend', _qmlLinkerCore)
qmlRegisterSingletonType(QUrl('qrc:/qml/ui/Gui.qml'), 'App.Gui', 1, 0, 'Gui')
registerUtilsQmlTypes()


class SystemObject(QObject):
    visibleChanged = Signal()
    visibilitySwapRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._visible = True
        self._focus_helper = FocusHelper(self)

    def requestVisibilitySwap(self):
        self.visibilitySwapRequested.emit()

    def getVisible(self):
        return self._visible

    def setVisible(self, value: bool):
        self._visible = value
        self.visibleChanged.emit()

    visible = Property(bool, getVisible, setVisible, notify=visibleChanged)

    def getFocusHelper(self):
        return self._focus_helper

    focusHelper = Property(QObject, getFocusHelper, constant=True)


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

            def onTrayShowTriggered():
                if not _qmlSystemObj.getVisible():
                    _qmlSystemObj.setVisible(True)
            self._tray.showTriggered.connect(onTrayShowTriggered)

        if load_viewmodels:
            _qmlLinkerCore.initialize(self._window, api_collection, eventsys)
            _qmlLinkerCore.loadContent()
            _qmlLinkerCore.loadFullyContent()

        self._image_providers = registerQmlImageProviders(engine)

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

    def image_providers(self):
        return self._image_providers

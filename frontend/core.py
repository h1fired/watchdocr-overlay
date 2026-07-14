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
import ctypes
import os


os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'  # Bad fix, should be replaced


_qmlLinkerCore = WatchdOcrLinkerCore()
qmlRegisterSingletonInstance(WatchdOcrLinkerCore, 'App.Backend', 1, 0, 'Backend', _qmlLinkerCore)
qmlRegisterSingletonType(QUrl('qrc:/qml/ui/Gui.qml'), 'App.Gui', 1, 0, 'Gui')
registerUtilsQmlTypes()


class SystemObject(QObject):
    visibleChanged = Signal()
    visibilitySwapRequested = Signal()
    windowTransparentForCaptureChanged = Signal()
    windowTransparentForInputChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._visible = True
        self._focus_helper = FocusHelper(self)
        self._window = None
        self._window_transparent_for_capture = False
        self._window_transparent_for_input = False

    def requestVisibilitySwap(self):
        self.visibilitySwapRequested.emit()

    def setWindow(self, window):
        self._window = window

    def getVisible(self):
        return self._visible

    def setVisible(self, value: bool):
        self._visible = value
        self.visibleChanged.emit()

    visible = Property(bool, getVisible, setVisible, notify=visibleChanged)

    def getFocusHelper(self):
        return self._focus_helper

    focusHelper = Property(QObject, getFocusHelper, constant=True)

    def getWindowTransparentForCapture(self):
        return self._window_transparent_for_capture

    def setWindowTransparentForCapture(self, value: bool):
        user32 = ctypes.windll.user32
        hwnd = self._window.winId()
        WDA_NONE = 0x00000000
        WDA_EXCLUDEFROMCAPTURE = 0x00000011
        user32.SetWindowDisplayAffinity(
            hwnd,
            WDA_EXCLUDEFROMCAPTURE if value else WDA_NONE
        )
        self._window_transparent_for_capture = value
        self.windowTransparentForCaptureChanged.emit()

    windowTransparentForCapture = Property(
        bool,
        getWindowTransparentForCapture,
        setWindowTransparentForCapture,
        notify=windowTransparentForCaptureChanged
    )

    def getWindowTransparentForInput(self):
        return self._window_transparent_for_input

    def setWindowTransparentForInput(self, value: bool):
        WS_EX_TRANSPARENT = 0x00000020
        GWL_EXSTYLE = -20
        hwnd = self._window.winId()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if value:
            style |= WS_EX_TRANSPARENT
        else:
            style &= ~WS_EX_TRANSPARENT
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

        self._window_transparent_for_input = value
        self.windowTransparentForInputChanged.emit()

    windowTransparentForInput = Property(
        bool,
        getWindowTransparentForInput,
        setWindowTransparentForInput,
        notify=windowTransparentForInputChanged
    )


_qmlSystemObj = SystemObject()
qmlRegisterSingletonInstance(WatchdOcrLinkerCore, 'App.System', 1, 0, 'System', _qmlSystemObj)


class GuiCoreApplication(metaclass=Singleton):
    def __init__(self):
        self._tray = None

    def pre_init(self):
        self._app = QApplication([])

        # Init tray
        self._app.setQuitOnLastWindowClosed(False)
        self._tray = SystemTray(self._app)

        def onTrayShowTriggered():
            if not _qmlSystemObj.getVisible():
                _qmlSystemObj.setVisible(True)
        self._tray.showTriggered.connect(onTrayShowTriggered)

    def load(
        self,
        api_collection: KernelAPICollection,
        eventsys: EventSystem,
        load_viewmodels=True
    ):
        engine = QQmlApplicationEngine()
        engine.load(config.QML_WINDOW_FILE)
        if not engine.rootObjects():
            raise RuntimeError('Failed to load QML window')

        self._engine = engine
        self._window = engine.rootObjects()[0]

        _qmlSystemObj.setWindow(self._window)

        self._image_providers = registerQmlImageProviders(engine)

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

    def image_providers(self):
        return self._image_providers

    def tray(self):
        return self._tray

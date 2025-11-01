from qt.qml import QQmlApplicationEngine
from qt.core import QApplication, QObject, Signal
from frontend.tray import SystemTray
from frontend.viewmodels.core import qmlLinkerCore
from config import config
import sys


class SystemObject(QObject):
    visibilityChanged = Signal()

    def requestVisibilityChange(self):
        self.visibilityChanged.emit()


class GuiCoreApplication:
    def __init__(self):
        self._tray = None

    def init(self, accessor, eventsys, notray=True):
        app = QApplication(sys.argv)
        engine = QQmlApplicationEngine()

        sysobj = self._init_system_object(app, engine)
        window = self._init_window(engine)
        if not notray:
            self._tray = self._init_tray(app, window)
        self._init_viewmodels(window, accessor, eventsys)

        self._app = app
        self._engine = engine
        self._window = window
        self._sysobj = sysobj

    def exec(self):
        if self._tray:
            self._tray.show()
        return self._app.exec()

    def window(self):
        return self._engine.rootObjects()[0]

    def engine(self):
        return self._engine

    def system_object(self):
        return self._sysobj

    def _init_system_object(self, app, engine):
        system_obj = SystemObject(app)
        engine.rootContext().setContextProperty('system', system_obj)
        return system_obj

    def _init_window(self, engine):
        engine.load(config.QML_WINDOW_FILE)
        if not engine.rootObjects():
            raise RuntimeError('Failed to load QML window')
        return engine.rootObjects()[0]

    def _init_tray(self, app, window):
        app.setQuitOnLastWindowClosed(False)
        return SystemTray(window, app)

    def _init_viewmodels(self, window, accessor, eventsys):
        qmlLinkerCore.initialize(
            window=window,
            accessor=accessor,
            eventsys=eventsys
        )
        qmlLinkerCore.loadContent()
        qmlLinkerCore.loadFullyContent()

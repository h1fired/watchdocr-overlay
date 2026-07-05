from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtQml import QQmlApplicationEngine
from config import config


class PluginDownloader(QObject):
    loadingChanged = Signal()
    labelChanged = Signal()
    progressChanged = Signal()

    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._loading = False
        self._label = ''
        self._progress = 0.

    def getLoading(self):
        return self._loading

    loading = Property(bool, getLoading, notify=loadingChanged)

    def getLabel(self):
        return self._label

    label = Property(str, getLabel, notify=labelChanged)

    def getProgress(self):
        return self._progress

    progress = Property(float, getProgress, notify=progressChanged)


class PreloaderCore:
    def exec(self):
        engine = QQmlApplicationEngine()
        engine.load(config.PRELOADER_WINDOW_FILE)

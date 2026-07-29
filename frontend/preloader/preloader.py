from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtQml import QQmlApplicationEngine
from src.common.plugin import PluginManager, PluginResourceDownloader
from config import config
from threading import Thread
import time


class PreloaderWorker(QObject):
    loadingChanged = Signal()
    labelChanged = Signal()
    progressChanged = Signal()
    finished = Signal()
    error = Signal()

    def __init__(self, manager: PluginManager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._loading = False
        self._label = ''
        self._progress = 0.

        self._thread = None

    def getLoading(self):
        return self._loading

    loading = Property(bool, getLoading, notify=loadingChanged)

    def getLabel(self):
        return self._label

    def setLabel(self, text: str):
        self._label = text
        self.labelChanged.emit()

    label = Property(str, getLabel, notify=labelChanged)

    def getProgress(self):
        return self._progress

    def setProgress(self, value: float):
        self._progress = value
        self.progressChanged.emit()

    progress = Property(float, getProgress, notify=progressChanged)

    def startDownloading(self):
        self._thread = Thread(target=self._runner, daemon=True)
        self._thread.start()

    def _runner(self):
        # Plugin downloader
        downloader = PluginResourceDownloader(self._manager)
        self.setLabel('Downloading resources...')
        downloader.observe('progress', self.setProgress)

        if not downloader.start_download():
            self.setLabel('An error occured! Exit...')
            time.sleep(1)
            self.error.emit()
            return

        # Starting app
        self.setLabel('Starting WatchdOcr...')
        time.sleep(0.5)

        self.finished.emit()


class PreloaderCore(QObject):
    finished = Signal()
    error = Signal()

    def __init__(self, manager: PluginManager, parent=None):
        super().__init__(parent)
        self._engine = QQmlApplicationEngine()
        self._worker = PreloaderWorker(manager)

    def exec(self):
        context = self._engine.rootContext()
        context.setContextProperty('preloaderWorker', self._worker)
        self._engine.load(config.PRELOADER_WINDOW_FILE)

        def on_downloading_finish():
            component = self._engine.rootObjects()[0]
            component.close()
            component.deleteLater()
            self.finished.emit()

        self._worker.finished.connect(on_downloading_finish)
        self._worker.error.connect(self.error)
        self._worker.startDownloading()

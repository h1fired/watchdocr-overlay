import asyncio
from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtQml import QQmlApplicationEngine
from src.common.plugin import PluginManager, PluginResourceDownloader
from config import config


class PreloaderWorker(QObject):
    loadingChanged = Signal()
    labelChanged = Signal()
    progressChanged = Signal()

    def __init__(self, manager: PluginManager, parent=None):
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

    async def download(self) -> bool:
        self.setLabel('Downloading resources')

        downloader = PluginResourceDownloader(self._manager)
        downloader.observe('progress', self.setProgress)

        if not await downloader.start_download():
            self.setLabel('An error occured! Exit...')
            await asyncio.sleep(1)
            return False

        # Starting app
        self.setLabel('Starting WatchdOcr...')
        await asyncio.sleep(0.5)

        return True


class PreloaderCore(QObject):
    def __init__(self, manager: PluginManager, parent=None):
        super().__init__(parent)
        self._engine = QQmlApplicationEngine()
        self._worker = PreloaderWorker(manager)

    async def exec(self) -> bool:
        context = self._engine.rootContext()
        context.setContextProperty('preloaderWorker', self._worker)
        self._engine.load(config.PRELOADER_WINDOW_FILE)

        success = await self._worker.download()

        component = self._engine.rootObjects()[0]
        component.close()
        component.deleteLater()

        return success

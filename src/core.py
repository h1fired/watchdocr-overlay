from src.common.event import EventSystem
from src.common.plugin import PluginManager

from src.watchdocr.plugins.ocr.tesseract.main import TesseractOcrPlugin
from src.watchdocr.processor import WatchdOcrProcessor


class _P:
    def __init__(self):
        self.p = None


PROCESSOR = _P()


class WatchdOcrCore:
    def initialize(self):
        self._eventsys = EventSystem()
        self._plugin_manager = PluginManager(self._eventsys)

        # TEMP: Register plugins
        self._plugin_manager.add_plugin(TesseractOcrPlugin)

        self._plugin_manager.init()

        self._processor = WatchdOcrProcessor(self._eventsys, self._plugin_manager)
        self._processor.start_loop()
        PROCESSOR.p = self._processor

    def destroy(self):
        self._processor.stop_loop()

    def eventsys(self):
        return self._eventsys

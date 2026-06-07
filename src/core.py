from src.common.event import EventSystem
from src.common.plugin import PluginManager
from src.watchdocr.processor import WatchdOcrProcessor
from src.common.api import KernelAPICollection


class WatchdOcrCore:
    def initialize(self):
        self._eventsys = EventSystem()
        self._kernel_apis = KernelAPICollection()
        self._plugin_manager = PluginManager(self._eventsys)

        self._plugin_manager.add_entry_point('src.watchdocr.plugins')
        self._plugin_manager.init()

        self._processor = WatchdOcrProcessor(self._eventsys, self._plugin_manager)
        self._processor.start_loop()

    def destroy(self):
        self._processor.stop_loop()

    def api_collection(self):
        return self._kernel_apis

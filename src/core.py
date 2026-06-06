from src.common.event import EventSystem
from src.common.plugin import PluginManager
from src.context import AppContext
from src.watchdocr.processor import WatchdOcrProcessor


class WatchdOcrCore:
    def initialize(self):
        self._eventsys = EventSystem()
        self._plugin_manager = PluginManager(self._eventsys)
        self._plugin_manager.add_entry_point('src.watchdocr.plugins')

        self._plugin_manager.init()

        self._processor = WatchdOcrProcessor(self._eventsys, self._plugin_manager)
        self._processor.start_loop()

        self._context = AppContext(
            eventsys=self._eventsys,
            processor=self._processor,
        )

    def destroy(self):
        self._processor.stop_loop()

    def context(self) -> AppContext:
        return self._context

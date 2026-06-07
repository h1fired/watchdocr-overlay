from src.common.event import EventSystem
from src.common.plugin import PluginManager
from src.watchdocr.processor import WatchdOcrProcessor
from src.common.api import KernelAPICollection


class WatchdOcrKernel:
    def __init__(self):
        self._eventsys = EventSystem()
        self._plugin_manager = PluginManager(self._eventsys)

    @property
    def plugins(self):
        return self._plugin_manager

    @property
    def event_system(self):
        return self._eventsys


class WatchdOcrCore:
    def initialize(self):
        self._kernel = WatchdOcrKernel()
        self._kernel_apis = KernelAPICollection()

        self._kernel.plugins.add_entry_point('src.watchdocr.plugins')
        self._kernel.plugins.init()

        self._processor = WatchdOcrProcessor(
            eventsys=self._kernel.event_system,
            plugins_manager=self._kernel.plugins
        )
        self._processor.start_loop()

    def destroy(self):
        self._processor.stop_loop()

    def api_collection(self):
        return self._kernel_apis

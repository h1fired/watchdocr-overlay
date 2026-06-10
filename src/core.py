from src.common.event import EventSystem
from src.common.plugin import PluginManager
from src.watchdocr.processor import WatchdOcrProcessor
from src.common.api import KernelAPICollection
from typing import Any

from src.watchdocr.api.processor import ProcessorAPI
from src.watchdocr.api.translation import TranslationAPI
from src.watchdocr.api.ocr import OcrAPI


class WatchdOcrKernelObjectsRegistry:
    def __init__(self):
        self._objects: dict[str, Any] = {}

    def set(self, id: str, obj: Any):
        if id in self._objects.keys():
            raise KeyError('Object already exists')
        self._objects[id] = obj

    def pull(self, id: str):
        return self._objects[id]


class WatchdOcrKernel:
    def __init__(self):
        self._eventsys = EventSystem()
        self._plugin_manager = PluginManager(self._eventsys)
        self._objects = WatchdOcrKernelObjectsRegistry()

    @property
    def plugins(self):
        return self._plugin_manager

    @property
    def event_system(self):
        return self._eventsys

    @property
    def objects(self):
        return self._objects


class WatchdOcrCore:
    def initialize(self):
        self._kernel = WatchdOcrKernel()
        self._kernel_apis = KernelAPICollection()

        self._kernel.plugins.add_entry_point('src.watchdocr.plugins')
        self._kernel.plugins.init()

        processor = WatchdOcrProcessor(
            eventsys=self._kernel.event_system,
            plugins_manager=self._kernel.plugins
        )
        processor.start_loop()
        self._kernel.objects.set('watchdocr-processor', processor)

        # API
        processor_api = ProcessorAPI(self._kernel)
        self._kernel_apis.add(processor_api)

        ocr_api = OcrAPI(self._kernel)
        self._kernel_apis.add(ocr_api)

        translation_api = TranslationAPI(self._kernel)
        self._kernel_apis.add(translation_api)

    def destroy(self):
        processor = self._kernel.objects.pull('watchdocr-processor')
        processor.stop_loop()

    def api_collection(self):
        return self._kernel_apis

    def event_system(self):
        return self._kernel.event_system

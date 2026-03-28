from src.common.event import EventSystem
from src.watchdocr.processor import WatchdOcrProcessor


class WatchdOcrCore:
    def initialize(self):
        self._eventsys = EventSystem()
        self._processor = WatchdOcrProcessor(self._eventsys)
        self._processor.start_loop()

    def eventsys(self):
        return self._eventsys

from src.common.event import EventSystem
from src.watchdocr.processor import WatchdOcrProcessor


class _P:
    def __init__(self):
        self.p = None

PROCESSOR = _P()


class WatchdOcrCore:
    def initialize(self):
        self._eventsys = EventSystem()
        self._processor = WatchdOcrProcessor(self._eventsys)
        self._processor.start_loop()

        PROCESSOR.p = self._processor

    def destroy(self):
        self._processor.stop_loop()

    def eventsys(self):
        return self._eventsys

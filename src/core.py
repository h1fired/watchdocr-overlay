from src.common.event import EventSystem


class WatchdOcrCore:
    def initialize(self):
        self._eventsys = EventSystem()

    def eventsys(self):
        return self._eventsys

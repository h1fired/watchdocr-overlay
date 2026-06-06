from dataclasses import dataclass
from src.common.event import EventSystem
from src.watchdocr.processor import WatchdOcrProcessor


@dataclass(frozen=True)
class AppContext:
    eventsys: EventSystem
    processor: WatchdOcrProcessor

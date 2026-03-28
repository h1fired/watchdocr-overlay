from queue import Queue
from threading import Thread
from src.common.event import EventSystem, IEvent
import time


class ProcessorStartedEvent(IEvent):
    pass


class ProcessorStoppedEvent(IEvent):
    pass


class TextResultReceivedEvent(IEvent):
    text: str


class Events:
    PROCESSOR_STARTED = ProcessorStartedEvent
    PROCESSOR_STOPPED = ProcessorStoppedEvent
    TEXT_RESULT_RECEIVED = TextResultReceivedEvent


class WatchdOcrProcessor:
    def __init__(self, eventsys: EventSystem):
        self._eventsys = eventsys

        self._command_q = Queue()
        self._loop_active = False
        self._loop_thread = None

    def start_loop(self):
        if self._loop_active:
            return

        self._loop_active = True
        self._loop_thread = Thread(target=self._loop_infinite, daemon=True)
        self._loop_thread.start()

        self._eventsys.dispatch(Events.PROCESSOR_STARTED, {})

    def stop_loop(self):
        if not self._loop_active:
            return

        self._loop_active = False
        if self._loop_thread.is_alive():
            self._loop_thread.join()
        self._loop_thread = None

        self._eventsys.dispatch(Events.PROCESSOR_STOPPED, {})

    def _loop_infinite(self):
        while self._loop_active:
            self._eventsys.dispatch(
                Events.TEXT_RESULT_RECEIVED,
                {'text': 'result text'}
            )
            time.sleep(1)

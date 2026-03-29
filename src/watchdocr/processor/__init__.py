from src.common.event import EventSystem, IEvent
from threading import Thread
from enum import IntEnum, auto
import queue


class ProcessorStartedEvent(IEvent):
    pass


class ProcessorStoppedEvent(IEvent):
    pass


class ProcessorResultReceivedEvent(IEvent):
    text: str


class Events:
    PROCESSOR_STARTED = ProcessorStartedEvent
    PROCESSOR_STOPPED = ProcessorStoppedEvent
    PROCESSOR_RESULT_RECEIVED = ProcessorResultReceivedEvent


class ProcessorCommandType(IntEnum):
    START = auto()
    STOP = auto()
    ONETIME_MODE_ENABLE = auto()
    LIVE_MODE_ENABLE = auto()


class ProcessorCommand:
    def __init__(self, type: ProcessorCommandType, *args):
        self._type = type
        self._args = args

    def type(self):
        return self._type

    def args(self):
        return self._args


class ProcessorMode(IntEnum):
    ONETIME = 0
    LIVE = 1


class WatchdOcrProcessor:
    def __init__(self, eventsys: EventSystem):
        self._eventsys = eventsys

        self._command_q = queue.Queue()
        self._loop_active = False
        self._loop_thread = None

        self._active = False
        self._mode = ProcessorMode.ONETIME

    def start_loop(self):
        if self._loop_active:
            return

        self._loop_active = True
        self._loop_thread = Thread(target=self._loop_infinite, daemon=True)
        self._loop_thread.start()

    def stop_loop(self):
        if not self._loop_active:
            return

        self._command_q.put(False)
        self._loop_active = False
        if self._loop_thread.is_alive():
            self._loop_thread.join()
        self._loop_thread = None
        self._command_q.queue.clear()

    def queue_command(self, command: ProcessorCommand):
        self._command_q.put(command)

    def _loop_infinite(self):
        counter = 0

        while self._loop_active:
            if self._mode == ProcessorMode.ONETIME:
                cmd: ProcessorCommand = self._command_q.get()
            else:
                try:
                    cmd: ProcessorCommand = self._command_q.get(timeout=1.0)
                except queue.Empty:
                    cmd = None

            if cmd is False:
                break

            if cmd:
                match cmd.type():
                    case ProcessorCommandType.START:
                        self._active = True
                        self._eventsys.dispatch(Events.PROCESSOR_STARTED, {})
                    case ProcessorCommandType.STOP:
                        self._active = False
                        self._eventsys.dispatch(Events.PROCESSOR_STOPPED, {})
                    case ProcessorCommandType.ONETIME_MODE_ENABLE:
                        self._mode = ProcessorMode.ONETIME
                    case ProcessorCommandType.LIVE_MODE_ENABLE:
                        self._mode = ProcessorMode.LIVE

            if not self._active:
                continue

            # Send test result data to event system
            self._eventsys.dispatch(
                event=Events.PROCESSOR_RESULT_RECEIVED,
                data={'text': f'some result {counter}'}
            )
            counter += 1

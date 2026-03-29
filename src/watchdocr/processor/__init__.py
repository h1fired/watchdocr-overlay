from src.common.event import EventSystem, IEvent
from src.watchdocr.processor.recognizer import Recognizer, RecognizerResult
from threading import Thread
from enum import Enum, IntEnum
import queue


class ProcessorStartedEvent(IEvent):
    pass


class ProcessorStoppedEvent(IEvent):
    pass


class ProcessorResultReceivedEvent(IEvent):
    data: dict


class Events:
    PROCESSOR_STARTED = ProcessorStartedEvent
    PROCESSOR_STOPPED = ProcessorStoppedEvent
    PROCESSOR_RESULT_RECEIVED = ProcessorResultReceivedEvent


class ProcessorCommand:
    def __init__(
        self,
        id: str,
        priority=0,
        need_restart=False,
        interruptive=False,
        args=tuple()
    ):
        self._id = id
        self._args = args
        self._priority = priority
        self._need_restart = need_restart
        self._interruptive = interruptive

    def id(self):
        return self._id

    def args(self):
        return self._args

    def get_priority(self):
        return self._priority

    def need_restart(self):
        return self._need_restart

    def interruptive(self):
        return self._interruptive


class ProcessorCommandType(str, Enum):
    START = 'start'
    STOP = 'stop'
    ONETIME_MODE_ENABLE = 'onetime_mode_enable'
    LIVE_MODE_ENABLE = 'live_mode_enable'
    DETECTING_BOX_CHANGED = 'detecting_box_changed'


PROCESSOR_COMMAND_PARAMETERS = {
    ProcessorCommandType.START:                 (5, True),
    ProcessorCommandType.STOP:                  (5, False, True),
    ProcessorCommandType.ONETIME_MODE_ENABLE:   (0, True, True),
    ProcessorCommandType.LIVE_MODE_ENABLE:      (0, True, True),
    ProcessorCommandType.DETECTING_BOX_CHANGED: (0, True, True),
}


class ProcessorMode(IntEnum):
    ONETIME = 0
    LIVE = 1


class ProcessorQueueEmpty(Exception):
    pass


class ProcessorQueue:
    def __init__(self):
        self._q = queue.PriorityQueue()

    def put(self, cmd: ProcessorCommand, priority: int = 0):
        self._q.put((priority, cmd))

    def get(self, timeout: float | None = None):
        try:
            _, cmd = self._q.get(timeout=timeout)
            return cmd
        except queue.Empty:
            raise ProcessorQueueEmpty

    def size(self):
        return self._q.qsize()

    def clear(self):
        self._q.queue.clear()


class WatchdOcrProcessor:
    def __init__(self, eventsys: EventSystem):
        self._eventsys = eventsys

        self._command_q = ProcessorQueue()
        self._loop_active = False
        self._loop_thread = None

        self._recognizer = Recognizer()
        self._recognizer.register_callback(self._on_recognizer_result)

    def start_loop(self):
        if self._loop_active:
            return

        self._recognizer.run()

        self._loop_active = True
        self._loop_thread = Thread(target=self._loop_infinite, daemon=True)
        self._loop_thread.start()

    def stop_loop(self):
        if not self._loop_active:
            return

        self._command_q.put((0, False))
        self._loop_active = False
        if self._loop_thread.is_alive():
            self._loop_thread.join()
        self._loop_thread = None
        self._command_q.clear()

    def queue_command(self, type: ProcessorCommandType, *args):
        params = PROCESSOR_COMMAND_PARAMETERS[type]
        cmd = ProcessorCommand(type, *params, args=args)
        self._command_q.put(cmd)

    def _loop_infinite(self):
        while self._loop_active:
            cmd: ProcessorCommand = self._command_q.get()
            if cmd is False:
                break

            match cmd.id():
                case ProcessorCommandType.START:
                    self._recognizer.set_active(True)
                    self._eventsys.dispatch(Events.PROCESSOR_STARTED, {})
                case ProcessorCommandType.STOP:
                    self._recognizer.set_active(False)
                    self._eventsys.dispatch(Events.PROCESSOR_STOPPED, {})
                case ProcessorCommandType.ONETIME_MODE_ENABLE:
                    self._recognizer.set_mode(ProcessorMode.ONETIME)
                case ProcessorCommandType.LIVE_MODE_ENABLE:
                    self._recognizer.set_mode(ProcessorMode.LIVE)
                case ProcessorCommandType.DETECTING_BOX_CHANGED:
                    self._recognizer.set_area(cmd.args()[0])

            if cmd.interruptive():
                self._recognizer.interrupt()

            if cmd.need_restart():
                self._recognizer.refresh()

    def _on_recognizer_result(self, result: RecognizerResult):
        self._eventsys.dispatch(
            event=Events.PROCESSOR_RESULT_RECEIVED,
            data={'data': result.to_dict()}
        )

from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Signal, Slot
from src.watchdocr.processor import Events
from src.common.event import Event
from src.core import PROCESSOR
from src.watchdocr.processor import ProcessorCommand, ProcessorCommandType


class ProcessorViewModel(QmlViewModel):
    _name = 'Processor'

    started = Signal()
    stopped = Signal()
    resultReceived = Signal(str)

    def onInit(self):
        self._p = PROCESSOR

    def onLoaded(self):
        Event.subscribe(
            system=self.eventsys(),
            event=Events.PROCESSOR_RESULT_RECEIVED,
            handler=self.onResultReceived
        )
        Event.subscribe(
            system=self.eventsys(),
            event=Events.PROCESSOR_STARTED,
            handler=self.onStarted
        )
        Event.subscribe(
            system=self.eventsys(),
            event=Events.PROCESSOR_STOPPED,
            handler=self.onStopped
        )

    def onResultReceived(self, e):
        self.resultReceived.emit(e.text)

    def onStarted(self, _):
        self.started.emit()

    def onStopped(self, _):
        self.stopped.emit()

    @Slot(str)
    def onPlayPauseButtonClick(self, state: str):
        if state == 'run':
            self._p.p.queue_command(ProcessorCommandType.START)
        elif state == 'pause':
            self._p.p.queue_command(ProcessorCommandType.STOP)

    @Slot(str)
    def onModeChanged(self, mode: str):
        if mode == 'onetime':
            self._p.p.queue_command(ProcessorCommandType.ONETIME_MODE_ENABLE)
        elif mode == 'live':
            self._p.p.queue_command(ProcessorCommandType.LIVE_MODE_ENABLE)

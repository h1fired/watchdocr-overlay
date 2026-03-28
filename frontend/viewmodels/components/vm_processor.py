from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Signal, Slot
from src.watchdocr.processor import Events
from src.common.event import Event
from src.core import PROCESSOR
from src.watchdocr.processor import ProcessorCommand, ProcessorCommandType


class ProcessorViewModel(QmlViewModel):
    _name = 'Processor'

    resultReceived = Signal(str)
    started = Signal()
    stopped = Signal()

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
            self._p.p.start_loop()
        elif state == 'pause':
            self._p.p.stop_loop()

    @Slot(str)
    def onModeChanged(self, mode: str):
        if mode == 'onetime':
            cmd = ProcessorCommand(ProcessorCommandType.ONETIME_MODE_ENABLE)
            self._p.p.queue_command(cmd)
        elif mode == 'live':
            cmd = ProcessorCommand(ProcessorCommandType.LIVE_MODE_ENABLE)
            self._p.p.queue_command(cmd)

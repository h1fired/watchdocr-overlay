from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Signal, Slot, QRect, Property
from src.watchdocr.processor import Events
from src.watchdocr.processor import ProcessorCommandType
from src.common.event import IEvent, EventData
from src.core import PROCESSOR


class ProcessorViewModel(QmlViewModel):
    _name = 'Processor'

    resultReceived = Signal(dict)
    activeChanged = Signal()

    def onInit(self):
        self._p = PROCESSOR

    def onLoaded(self):
        self._eventsys.listen(self.onEvent)

    def onEvent(self, event: IEvent, data: EventData):
        match event:
            case Events.PROCESSOR_RESULT_RECEIVED:
                self.resultReceived.emit(data.data)
            case Events.PROCESSOR_ACTIVE_CHANGED:
                self.activeChanged.emit()

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

    @Slot(QRect)
    def onSelectionAreaBoxReleased(self, box: QRect):
        self._p.p.queue_command(
            ProcessorCommandType.DETECTING_BOX_CHANGED,
            (box.x(), box.y(), box.width(), box.height())
        )

    def getActive(self):
        return self._p.p.recognizer().is_active()

    active = Property(bool, getActive, notify=activeChanged)

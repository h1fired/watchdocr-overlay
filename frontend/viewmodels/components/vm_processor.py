from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Signal, Slot, QRect, Property
from src.common.event import IEvent, EventData
from src.watchdocr.api.processor import ProcessorAPI
from src.watchdocr.processor.processor import PipelineStrategy, Events
import json


class ProcessorViewModel(QmlViewModel):
    _name = 'Processor'
    _needed_api = (ProcessorAPI,)

    resultReceived = Signal(str)
    activeChanged = Signal()
    recognizerStatusChanged = Signal(int)

    def onLoaded(self):
        self._api = self.getApi(ProcessorAPI)
        self.getEventSystem().listen(self.onEvent)

    def onEvent(self, event: IEvent, data: EventData):
        match event:
            case Events.PROCESSOR_RESULT_RECEIVED:
                self.resultReceived.emit(json.dumps(data.data))
            case Events.PROCESSOR_ACTIVE_CHANGED:
                self.activeChanged.emit()
            case Events.PROCESSOR_STATUS_CHANGED:
                self.recognizerStatusChanged.emit(data.status)

    @Slot(str)
    def onPlayPauseButtonClick(self, state: str):
        # if state == 'run':
        #     self._api.queue_command(ProcessorCommandType.START)
        # elif state == 'pause':
        #     self._api.queue_command(ProcessorCommandType.STOP)
        pass

    @Slot(str)
    def onModeChanged(self, mode: str):
        # if mode == 'onetime':
        #     self._api.queue_command(ProcessorCommandType.ONETIME_MODE_ENABLE)
        # elif mode == 'live':
        #     self._api.queue_command(ProcessorCommandType.LIVE_MODE_ENABLE)
        pass

    @Slot(QRect)
    def onSelectionAreaBoxReleased(self, box: QRect):
        self._api.queue_pipeline(
            strategy=PipelineStrategy.OCR_TRANSLATION,
            context_data={
                'boundings': (box.x(), box.y(), box.width(), box.height())
            }
        )

    def getActive(self):
        return self._api.get_active()

    active = Property(bool, getActive, notify=activeChanged)

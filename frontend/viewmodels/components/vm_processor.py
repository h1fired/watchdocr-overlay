from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Signal, Slot, QRect, Property
from src.common.event import IEvent, EventData
from src.watchdocr.api.processor import ProcessorAPI
from src.watchdocr.api.workflow import WorkflowAPI
from src.watchdocr.workflow.workflows import OnetimeWorkflow, LiveWorkflow
from src.watchdocr.processor.processor import Events
import json


class ProcessorViewModel(QmlViewModel):
    _name = 'Processor'
    _needed_api = (ProcessorAPI, WorkflowAPI)

    resultReceived = Signal(str)
    activeChanged = Signal()
    recognizerStatusChanged = Signal()

    def onLoaded(self):
        self._api = self.getApi(ProcessorAPI)
        self._workflow_api = self.getApi(WorkflowAPI)
        self.getEventSystem().listen(self.onEvent)

        self._recognizer_status = 0
        self._current_mode = ''

    def onEvent(self, event: IEvent, data: EventData):
        match event:
            case Events.PROCESSOR_RESULT_RECEIVED:
                self.resultReceived.emit(json.dumps(data.data))
            case Events.PROCESSOR_ACTIVE_CHANGED:
                self.activeChanged.emit()
            case Events.PROCESSOR_STATUS_CHANGED:
                self._recognizer_status = data.status
                self.recognizerStatusChanged.emit()

    @Slot(str)
    def onModeChanged(self, mode: str):
        workflow = None
        if mode == 'onetime':
            workflow = OnetimeWorkflow
        elif mode == 'live':
            workflow = LiveWorkflow

        if workflow:
            self._workflow_api.switch_to(workflow)
            self._current_mode = mode

    @Slot(QRect)
    def onSelectionAreaBoxReleased(self, box: QRect):
        if box.isEmpty():
            self._workflow_api.switch_to(None)
        else:
            workflow = self.convertModeStrToType(self._current_mode)
            self._workflow_api.switch_to(workflow)

            self._workflow_api.provide_context_data({
                'boundings': (box.x(), box.y(), box.width(), box.height())
            })
            self._workflow_api.execute()

    def getActive(self):
        return self._api.get_active()

    active = Property(bool, getActive, notify=activeChanged)

    def getRecognizerStatus(self):
        return self._recognizer_status

    recognizerStatus = Property(int, getRecognizerStatus, notify=recognizerStatusChanged)

    def convertModeStrToType(self, mode: str):
        workflow = None
        if mode == 'onetime':
            workflow = OnetimeWorkflow
        elif mode == 'live':
            workflow = LiveWorkflow
        return workflow

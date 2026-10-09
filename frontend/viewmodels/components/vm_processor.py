from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Signal, Slot, QRect, Property
from src.watchdocr.workflow.workflows import OnetimeWorkflow, LiveWorkflow


class ProcessorViewModel(QmlViewModel):
    _name = 'Processor'

    resultReceived = Signal(str)
    activeChanged = Signal()
    recognizerStatusChanged = Signal()

    def onLoaded(self):
        self._recognizer_status = 0
        self._current_mode = ''

    @Slot(str)
    def onModeChanged(self, mode: str):
        # TODO: Implement
        pass

    @Slot(QRect)
    def onSelectionAreaBoxReleased(self, box: QRect):
        # TODO: Implement
        pass

    def getActive(self):
        # TODO: Implement
        return True

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

    @Slot(bool)
    def enableWorkflowManager(self, value: bool):
        # TODO: Implement
        pass

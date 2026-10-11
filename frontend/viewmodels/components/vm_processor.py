from frontend.viewmodels.common.mvvm import QmlViewModel
from frontend.qt.core import Signal, Slot, QRect, Property
from frontend.api.grpc.ocrtranslate.stub import OcrTranslateStub
from qasync import asyncSlot


class ProcessorViewModel(QmlViewModel):
    _name = 'Processor'

    resultReceived = Signal(str)
    activeChanged = Signal()
    recognizerStatusChanged = Signal()

    def onLoaded(self):
        self._recognizer_status = 0
        self._current_mode = ''

        from frontend.core import GuiCoreApplication
        self._grpc = GuiCoreApplication()._grpc_client

        self.receiveResultStream()

    @Slot(str)
    def onModeChanged(self, mode: str):
        # TODO: Implement
        pass

    @asyncSlot(QRect)
    async def onSelectionAreaBoxReleased(self, box: QRect):
        stub = self._grpc.get_stub(OcrTranslateStub)
        bounding = (
            box.x(),
            box.y(),
            box.width(),
            box.height()
        )
        await stub.request_recognize(bounding)

    def getActive(self):
        # TODO: Implement
        return True

    active = Property(bool, getActive, notify=activeChanged)

    def getRecognizerStatus(self):
        return self._recognizer_status

    recognizerStatus = Property(int, getRecognizerStatus, notify=recognizerStatusChanged)

    def convertModeStrToType(self, mode: str):
        # workflow = None
        # if mode == 'onetime':
        #     workflow = OnetimeWorkflow
        # elif mode == 'live':
        #     workflow = LiveWorkflow
        # return workflow
        # TODO: Implement
        pass

    @Slot(bool)
    def enableWorkflowManager(self, value: bool):
        # TODO: Implement
        pass

    @asyncSlot()
    async def receiveResultStream(self):
        stub = self._grpc.get_stub(OcrTranslateStub)
        async for output in stub.stream_results():
            print(output)

from PySide6.QtCore import Slot, Signal, QRect
from PySide6.QtQml import qmlRegisterSingletonType
from common.event import Event
from frontend.utils.screen import ScreenManager
from frontend.common.mvvm_qml import QmlViewModel
from src.tocr.service import OCRTranslateService


qmlRegisterSingletonType(ScreenManager, 'App.Utils', 1, 0, 'ExtScreen')


class OcrTranslateViewModel(QmlViewModel):
    _name = 'OcrTranslate'

    responseReceived = Signal(dict)

    def onLoaded(self):
        Event.subscribe(
            system=self.events,
            event=OCRTranslateService.Events.RESPONSE_RECEIVED,
            handler=self.onOcrTranslateResponseReceive
        )

    def onOcrTranslateResponseReceive(self, e):
        data = {
            'state': int(e.data.state.value),
            'text': e.data.text
        }
        self.responseReceived.emit(data)

    @Slot(QRect)
    def recognizeArea(self, rect: QRect):
        box = (
            rect.x(), rect.y(),
            rect.x() + rect.width(), rect.y() + rect.height()
        )
        s = self.accessor.get(OCRTranslateService)
        s.recognize(box)

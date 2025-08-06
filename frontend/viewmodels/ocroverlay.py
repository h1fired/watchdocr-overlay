from common.event import Event
from frontend.common.mvvm import ViewModel
from src.ocr.service import OCRTranslateService
from PySide6.QtCore import Slot, Signal, QRect, QObject
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import qmlRegisterSingletonType
from config import config
from frontend.utils.screen import ScreenManager


qmlRegisterSingletonType(ScreenManager, 'App.Utils', 1, 0, 'ExtScreen')


class OCROverlayViewModel(ViewModel):
    context_id = 'ocroverlaymodel'
    responseReceived = Signal()
    textCopied = Signal()

    def __init__(self, engine, accessor, event_system):
        super().__init__(engine, accessor, event_system)

    def on_load(self):
        self._response = {}

        Event.subscribe(
            system=self.event(),
            event=OCRTranslateService.Events.RESPONSE_RECEIVED,
            handler=self.on_ocr_translate_response_receive
        )

    def on_ocr_translate_response_receive(self, e):
        self._response = {
            'state': int(e.data.state.value),
            'text': e.data.text
        }
        self.responseReceived.emit()

    # Props
    @Slot(result='QVariant')
    def QMLgetResponse(self):
        return self._response

    @Slot(QRect)
    def QMLareaSelected(self, rect: QRect):
        box = (
            rect.x(), rect.y(),
            rect.x() + rect.width(), rect.y() + rect.height()
        )
        s = self.get_service(OCRTranslateService)
        s.recognize(box, config.TRANSLATION_TARGET_LANG)

    @Slot(str)
    def QMLtextCopied(self, text: str):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.textCopied.emit()

from common.event import Event
from frontend.common.mvvm import ViewModel
from src.ocr.service import OCRTranslateService, OCRState
from PySide6.QtCore import Property, Slot, Signal, QRect
from PySide6.QtWidgets import QApplication
from config import config


class OCROverlayViewModel(ViewModel):
    context_id = 'ocroverlaymodel'
    responseReceived = Signal()
    modeChanged = Signal(int)
    textCopied = Signal()

    def on_load(self):
        self._response = {}
        self._mode = ''

        Event.subscribe(
            system=self.event(),
            event=OCRTranslateService.Events.DATA_RECEIVE,
            handler=self.on_ocr_translate_data_receive
        )
        Event.subscribe(
            system=self.event(),
            event=OCRTranslateService.Events.STATE_CHANGE,
            handler=self.on_ocr_translate_state_change
        )

    def on_ocr_translate_data_receive(self, e):
        self._response = {
            'state': int(e.data.state.value),
            'text': e.data.text
        }
        self.responseReceived.emit()

    def on_ocr_translate_state_change(self, e):
        match e.state:
            case OCRState.RECOGNIZING:
                self.QMLsetMode(1)
            case OCRState.FINISHED:
                self.QMLsetMode(2)

    # Props
    @Slot(result='QVariant')
    def QMLgetResponse(self):
        return self._response

    def QMLgetMode(self):
        return self._mode

    def QMLsetMode(self, mode: int):
        self._mode = mode
        self.modeChanged.emit(mode)

    mode = Property(int, QMLgetMode, QMLsetMode, notify=modeChanged)

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

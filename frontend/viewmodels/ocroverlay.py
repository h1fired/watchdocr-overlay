from common.event import Event
from frontend.common.mvvm import ViewModel
from src.ocr.service import OCRTranslateService
from PySide6.QtCore import Property, Signal


class OCROverlayViewModel(ViewModel):
    context_id = 'ocroverlaymodel'
    textChanged = Signal(str)

    def on_load(self):
        self._text = ''

        Event.subscribe(
            system=self.event(),
            event=OCRTranslateService.Events.DATA_RECEIVE,
            handler=self.on_ocr_translate_data_receive
        )

    def on_ocr_translate_data_receive(self, e):
        self.QMLsetText(e.data.text)

    # Props
    def QMLgetText(self):
        return self._text

    def QMLsetText(self, text: str):
        self._text = text
        self.textChanged.emit(text)

    text = Property(str, QMLgetText, QMLsetText, notify=textChanged)

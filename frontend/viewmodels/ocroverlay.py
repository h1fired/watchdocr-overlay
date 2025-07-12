from common.event import Event
from frontend.common.mvvm import ViewModel
from src.ocr.service import OCRTranslateService, OCRState
from PySide6.QtCore import Property, Slot, Signal, QRect
from PIL import Image


class OCROverlayViewModel(ViewModel):
    context_id = 'ocroverlaymodel'
    textChanged = Signal(str)
    modeChanged = Signal(int)

    def on_load(self):
        self._text = ''
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
        self.QMLsetText(e.data.text)

    def on_ocr_translate_state_change(self, e):
        match e.state:
            case OCRState.RECOGNIZING:
                self.QMLsetMode(1)
            case OCRState.FINISHED:
                self.QMLsetMode(2)

    # Props
    def QMLgetText(self):
        return self._text

    def QMLsetText(self, text: str):
        self._text = text
        self.textChanged.emit(text)

    text = Property(str, QMLgetText, QMLsetText, notify=textChanged)

    def QMLgetMode(self):
        return self._mode

    def QMLsetMode(self, mode: int):
        self._mode = mode
        self.modeChanged.emit(mode)

    mode = Property(int, QMLgetMode, QMLsetMode, notify=modeChanged)

    @Slot(QRect)
    def QMLareaSelected(self, rect: QRect):
        print(rect)
        s = self.get_service(OCRTranslateService)
        s.recognize(Image.open('test.webp'))

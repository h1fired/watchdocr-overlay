from common.event import Event
from frontend.common.mvvm import ViewModel
from src.ocr.service import OCRTranslateService
from PySide6.QtCore import Slot, Signal, QRect, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication
from config import config


class ScreenManager(QObject):
    @Slot(result=QRect)
    def virtualScreensGeometry(self):
        rect = QRect()
        for i, screen in enumerate(QGuiApplication.screens()):
            if i == 0:
                rect = screen.geometry()
            else:
                rect = screen.geometry().united(rect)
        return rect

    @Slot(result=QRect)
    def primaryScreenGeometry(self):
        return QGuiApplication.primaryScreen().geometry()

    @Slot(result=list)
    def screensGeometries(self):
        return [s.geometry() for s in QGuiApplication.screens()]


class OCROverlayViewModel(ViewModel):
    context_id = 'ocroverlaymodel'
    responseReceived = Signal()
    textCopied = Signal()

    def __init__(self, engine, accessor, event_system):
        super().__init__(engine, accessor, event_system)
        self._screen_manager = ScreenManager()

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

    @Slot(result=QObject)
    def QMLscreenManager(self):
        return self._screen_manager

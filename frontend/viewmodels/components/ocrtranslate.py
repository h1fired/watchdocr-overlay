from common.event import Event
from frontend.common.mvvm_qml import QmlViewModel
from src.tocr.service import TOcrService
from src.translator.service import TranslationService
from PySide6.QtCore import Slot, Signal, QRect


class OcrTranslateViewModel(QmlViewModel):
    _name = 'OcrTranslate'

    responseReceived = Signal(dict)
    detailsReceived = Signal(tuple)

    def onLoaded(self):
        Event.subscribe(
            system=self.events,
            event=TOcrService.Events.RESPONSE_RECEIVED,
            handler=self.onOcrTranslateResponseReceive
        )

    def onOcrTranslateResponseReceive(self, e):
        data = {
            'state': e.status.value,
            'text': e.text
        }
        self.responseReceived.emit(data)
        self.detailsReceived.emit(e.details.values())

    @Slot(QRect, str, str)
    def translateArea(self, rect: QRect, _from: str, to: str):
        box = (
            rect.x(), rect.y(),
            rect.x() + rect.width(), rect.y() + rect.height()
        )

        translation_s = self.accessor.get(TranslationService)
        backend = translation_s.backends().current().value
        source_languages = backend.source_languages()
        id_from = source_languages.verbose_to_id(_from)
        target_languages = backend.target_languages()
        id_to = target_languages.verbose_to_id(to)

        s = self.accessor.get(TOcrService)
        s.terminate()
        s.recognize(box, id_from, id_to)

    @Slot()
    def terminateTask(self):
        ocr_translate_s = self.accessor.get(TOcrService)
        ocr_translate_s.terminate()

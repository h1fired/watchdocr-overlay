from common.service import Service
from common.event import IEvent
from src.tocr.ocrtranslate import OCRTranslateManager, OCRData


class _OCRTranslateResponseEvent(IEvent):
    data: OCRData


class OCRTranslateService(Service):

    class Events:
        RESPONSE_RECEIVED = _OCRTranslateResponseEvent

    def on_init(self):
        self._tocr = OCRTranslateManager()
        self._tocr.obs_data.register(lambda d: self.event.dispatch(
            event=self.Events.RESPONSE_RECEIVED,
            data={'data': d}
        ))

    def recognize(self, box: tuple[int, int, int, int]):
        self._tocr.recognize(box)

    def ocr(self):
        return self._tocr.ocr()

    def translator(self):
        return self._tocr.translator()

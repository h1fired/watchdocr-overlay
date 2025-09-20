from common.service import Service
from common.event import IEvent
from src.tocr.ocrtranslate import OCRTranslateManager, OCRData


class _OCRTranslateResponseEvent(IEvent):
    data: OCRData


class OCRTranslateService(Service):

    class Events:
        RESPONSE_RECEIVED = _OCRTranslateResponseEvent

    def on_init(self):
        self._ocr = OCRTranslateManager()
        self._ocr.obs_data.register(lambda d: self.event.dispatch(
            event=self.Events.RESPONSE_RECEIVED,
            data={'data': d}
        ))

    def recognize(
        self,
        window_box: tuple[int, int, int, int],
        target_language: str = 'EN'
    ):
        self._ocr.recognize(window_box, target_language)

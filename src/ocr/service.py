from common.service import Service
from common.event import IEvent
from .ocr import OCRTranslateManager, OCRData, OCRState


class _OCRTranslateStateChangeEvent(IEvent):
    state: OCRState


class _OCRTranslateDataReceiveEvent(IEvent):
    data: OCRData


class OCRTranslateService(Service):

    class Events:
        STATE_CHANGE = _OCRTranslateStateChangeEvent
        DATA_RECEIVE = _OCRTranslateDataReceiveEvent

    def on_init(self):
        self._ocr = OCRTranslateManager()
        self._ocr.obs_state.register(lambda s: self.event.dispatch(
            event=self.Events.STATE_CHANGE,
            data={'state': s}
        ))
        self._ocr.obs_data.register(lambda d: self.event.dispatch(
            event=self.Events.DATA_RECEIVE,
            data={'data': d}
        ))

    def recognize(
        self,
        window_box: tuple[int, int, int, int],
        target_language: str = 'EN'
    ):
        self._ocr.recognize(window_box, target_language)

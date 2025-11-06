from common.service import Service
from common.event import IEvent
from src.ocr.ocr import Ocr, OcrMode
from PIL import Image


class _OcrOutputReceiveEvent(IEvent):
    output: dict


class _OcrModeChangeEvent(IEvent):
    mode: OcrMode


class OcrService(Service):

    class Events:
        OUTPUT_RECEIVE = _OcrOutputReceiveEvent
        MODE_CHANGE = _OcrModeChangeEvent

    def on_init(self):
        self._ocr = Ocr()
        self.event.from_observable(
            observable=self._ocr.observable(),
            event=self.Events.OUTPUT_RECEIVE,
            fields=('output',)
        )

    def propagate_shared_objects(self):
        return {'ocr': self._ocr}

    def recognize(self, image: Image.Image):
        self._ocr.process_area(image)

    def backends(self):
        return self._ocr.backends()

    def change_mode(self, mode: OcrMode):
        self._ocr.change_mode(mode)
        self.event.dispatch(
            event=self.Events.MODE_CHANGE,
            data={'mode', mode}
        )

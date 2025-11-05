from common.service import Service
from common.event import IEvent
from src.ocr.ocr import Ocr
from PIL import Image


class _OcrOutputReceiveEvent(IEvent):
    output: dict


class OcrService(Service):

    class Events:
        OUTPUT_RECEIVE = _OcrOutputReceiveEvent

    def on_init(self):
        self._ocr = Ocr()
        self.event.from_observable(
            observable=self._ocr.observable(),
            event=self.Events.OUTPUT_RECEIVE,
            fields=('output',)
        )

    def recognize(self, image: Image.Image):
        self._ocr.process_area(image)

    def backends(self):
        return self._ocr.backends()

    def propagate_shared_objects(self):
        return {'ocr': self._ocr}

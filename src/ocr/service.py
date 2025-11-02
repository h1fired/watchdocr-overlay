from common.service import Service
from common.event import IEvent
from src.ocr.ocr import OCR
from PIL import Image


class _OcrOutputReceiveEvent(IEvent):
    output: dict


class OcrService(Service):

    class Events:
        OUTPUT_RECEIVE = _OcrOutputReceiveEvent

    def on_init(self):
        self._ocr = OCR()

    def recognize(self, image: Image.Image):
        output = self._ocr.recognize(image)
        self.event.dispatch(self.Events.OUTPUT_RECEIVE, {'output': output})
        return output

    def backends(self):
        return self._ocr.backends()

    def propagate_shared_objects(self):
        return {'ocr': self._ocr}

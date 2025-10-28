from common.service import Service
from src.ocr.ocr import OCR
from PIL import Image


class OcrService(Service):
    def on_init(self):
        self._ocr = OCR()

    def recognize(self, image: Image.Image):
        return self._ocr.recognize(image)

    def backends(self):
        return self._ocr.backends()

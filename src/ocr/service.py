from common.service import Service
from .ocr import OCRTranslateManager


class OCRTranslateService(Service):
    def on_init(self):
        self._ocr = OCRTranslateManager()

    def on_full_init(self):
        self._ocr.recognize('test.webp')

    def recognize(self, image):
        self._ocr.recognize(image)

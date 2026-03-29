from PIL import Image
from src.watchdocr.plugins.tesseractocr.__main__ import TesseractOcrPlugin


class Ocr:
    def __init__(self):
        self._api = TesseractOcrPlugin()
        self._api.on_load()

    def recognize(self, image: Image.Image):
        return self._api.recognize(image)

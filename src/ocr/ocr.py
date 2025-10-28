from src.ocr.backends import OcrBackendManager
from src.ocr.backends.gemini import GeminiOCRBackend
from src.ocr.filtering import OCRImageFilter
from PIL import Image


backends = [
    GeminiOCRBackend
]


class OCR:
    def __init__(self):
        self._backends = OcrBackendManager(backends)

    def recognize(self, image: Image.Image):
        adjusted_image = OCRImageFilter.adjust(image)
        backend = self._backends.current()
        raw_text = backend.recognize(adjusted_image)
        return raw_text

    def backends(self):
        return self._backends

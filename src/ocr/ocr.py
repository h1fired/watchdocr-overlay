from .backends import OCRBackendManager
from .backends.tesseract import TesseractOCRBackend
from .backends.gemini import GeminiOCRBackend
from .filtering import OCRImageFilter
from PIL import Image


backends = [
    TesseractOCRBackend,
    GeminiOCRBackend
]


class OCR:
    def __init__(self):
        self._backends = OCRBackendManager(backends)

    def recognize(self, image: Image.Image):
        adjusted_image = OCRImageFilter.adjust(image)
        backend = self._backends.current()
        raw_text = backend.recognize(adjusted_image)
        return raw_text

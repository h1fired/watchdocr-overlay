from src.ocr.backends import OcrBackendManager, OcrStatus
from src.ocr.backends.gemini import GeminiOcrBackend
from src.ocr.backends.tesseract import TesseractOcrBackend
from src.ocr.filtering import OCRImageFilter, OCRImageOptimizer
from PIL import Image
from config import config


backends = [
    GeminiOcrBackend,
    TesseractOcrBackend
]


class OCR:
    def __init__(self):
        self._backends = OcrBackendManager(backends)

    def recognize(self, image: Image.Image):
        OCRImageOptimizer.optimize_size(image, config.MAX_IMAGE_RESOLUTION)
        adjusted_image = OCRImageFilter.adjust(image)
        backend = self._backends.current()
        response = backend.recognize(adjusted_image)
        return response

    def backends(self):
        return self._backends

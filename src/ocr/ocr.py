from .backends.tesseract import TesseractOCRBackend
from .filtering import OCRImageFilter
from PIL import Image


class OCR:
    def __init__(self, backend=TesseractOCRBackend):
        self._backend = backend()

    def recognize(self, image: Image.Image):
        adjusted_image = OCRImageFilter.adjust(image)
        raw_text = self._backend.recognize(adjusted_image)
        return raw_text

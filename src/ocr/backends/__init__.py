from PIL import Image


class OCRBackend:

    def recognize(self, image: Image.Image):
        pass


class DummyOCRBackend(OCRBackend):
    def recognize(self, image):
        return "Dummy OCR text for development testing."
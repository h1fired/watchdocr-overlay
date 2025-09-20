from . import OCRBackend
import pytesseract


pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


class TesseractOCRBackend(OCRBackend):
    def recognize(self, image):
        return pytesseract.image_to_string(image)

from common.task import TaskManager
from common.observer import Observer
from dataclasses import dataclass
from PIL import ImageFile
import pytesseract


pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


@dataclass
class OCRData:
    text: str


class OCRTranslate:
    def recognize(self, image: ImageFile):
        text = pytesseract.image_to_string(image)
        data = OCRData(text)
        return data


class OCRTranslateManager:
    obs_data = Observer()

    def __init__(self):
        self._ocr = OCRTranslate()

    def recognize(self, image: ImageFile):
        tasks = TaskManager()
        f = tasks.execute(lambda t: self._ocr.recognize(image))
        f.observe(on_result=self.obs_data.notify)

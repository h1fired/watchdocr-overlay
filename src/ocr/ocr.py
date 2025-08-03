from common.task import TaskManager
from common.observer import TypedObserver
from dataclasses import dataclass
from enum import IntEnum
import pytesseract
from .window import grab_window_area
from .spell import clean_text
from .translate.translate import Translator


pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


class OCRDataState(IntEnum):
    SUCCESS = 0
    ERROR = 1
    RECOGNIZING = 2


class Messages:
    RECOGNIZING = 'Recognizing...'
    EMPTY_RECOGNITION = 'Error: Cannot recognize text'


@dataclass
class OCRData:
    state: OCRDataState
    text: str


class OCRTranslate:
    def __init__(self):
        self._translator = Translator()
        self._recognizing = False

    def recognize(
        self,
        window_box: tuple[int, int, int, int],
        target_language: str = 'EN'
    ):
        if self._recognizing:
            raise RuntimeError('OCRTranslate already recognizing')

        image = grab_window_area(window_box)
        text = pytesseract.image_to_string(image)
        text = clean_text(text)

        if text:
            text = self._translator.translate(text, target_language)
            data = OCRData(OCRDataState.SUCCESS, text)
        else:
            data = OCRData(OCRDataState.ERROR, Messages.EMPTY_RECOGNITION)

        return data


class OCRTranslateManager:
    obs_data = TypedObserver(OCRData)

    def __init__(self):
        self._ocr = OCRTranslate()

    def recognize(
        self,
        window_box: tuple[int, int, int, int],
        target_language: str = 'EN'
    ):
        data = OCRData(OCRDataState.RECOGNIZING, Messages.RECOGNIZING)
        self.obs_data.notify(data)

        manager = TaskManager()
        future = manager.execute(lambda _: self._ocr.recognize(
            window_box=window_box,
            target_language=target_language
        ))
        future.observe(on_result=self._on_result)

    def _on_result(self, data):
        self.obs_data.notify(data)

from common.task import TaskManager
from common.observer import Observer
from dataclasses import dataclass
import pytesseract
from enum import IntEnum
from .window import grab_window_area
from .spell import clean_text
from .translate.translate import Translator


pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


class OCRState(IntEnum):
    STAND_BY = 0
    RECOGNIZING = 1
    FINISHED = 2
    ERROR = 3


class Messages:
    EMPTY_RECOGNITION = '*Error: Cannot recognize text*'


@dataclass
class OCRData:
    text: str


class OCRTranslate:
    def __init__(self):
        self._translator = Translator()

    def recognize(self, window_box: tuple[int, int, int, int]):
        image = grab_window_area(window_box)
        text = pytesseract.image_to_string(image)
        text = clean_text(text)
        if text:
            text = self._translator.translate(text)
        else:
            text = Messages.EMPTY_RECOGNITION
        data = OCRData(text)
        return data


class OCRTranslateManager:
    obs_data = Observer()
    obs_state = Observer()

    def __init__(self):
        self._ocr = OCRTranslate()
        self._state = OCRState.STAND_BY

    def recognize(self, window_box: tuple[int, int, int, int]):
        if self._state == OCRState.RECOGNIZING:
            raise RuntimeError('OCR translation already started')
        self._state = OCRState.RECOGNIZING
        self.obs_state.notify(OCRState.RECOGNIZING)
        tasks = TaskManager()
        f = tasks.execute(lambda t: self._ocr.recognize(window_box))
        f.observe(
            on_finish=self._on_finish,
            on_result=self._on_result
        )

    def _on_finish(self):
        self._state = OCRState.FINISHED
        self.obs_state.notify(OCRState.FINISHED)

    def _on_result(self, data):
        self.obs_data.notify(data)

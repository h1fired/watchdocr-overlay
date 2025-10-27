from common.task import TaskManager
from common.observable import TypedObservable
from dataclasses import dataclass
from enum import IntEnum
from src.tocr.window import grab_window_area
from src.ocr.ocr import OCR
from src.translator.translate import Translator


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
        self._ocr = OCR()
        self._translator = Translator()
        self._recognizing = False

    def recognize(
        self,
        box: tuple[int, int, int, int],
    ):
        if self._recognizing:
            raise RuntimeError('OCRTranslate already recognizing')

        image = grab_window_area(box)
        text = self._ocr.recognize(image)

        if text:
            data = OCRData(OCRDataState.SUCCESS, text)
        else:
            data = OCRData(OCRDataState.ERROR, Messages.EMPTY_RECOGNITION)

        return data


class OCRTranslateManager:
    obs_data = TypedObservable(OCRData)

    def __init__(self):
        self._ocr = OCRTranslate()

    def recognize(
        self,
        box: tuple[int, int, int, int],
    ):
        data = OCRData(OCRDataState.RECOGNIZING, Messages.RECOGNIZING)
        self.obs_data.notify(data)

        manager = TaskManager()
        future = manager.execute(lambda _: self._ocr.recognize(box))
        future.observe(on_result=self._on_result)

    def _on_result(self, data):
        self.obs_data.notify(data)

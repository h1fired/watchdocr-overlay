from common.observable import TypedObservable
from common.pipeline import ServicePipeline
from src.ocr.ocr import Ocr
from src.ocr.service import OcrService
from src.translator.service import TranslationService
from enum import IntEnum


class TOcrMode(IntEnum):
    SINGLE = 0


class TOcrStatus(IntEnum):
    ERROR = 0
    SUCCESS = 1
    RECOGNIZING = 2


class TOcr:
    def __init__(self, ocr: Ocr, eventsys, accessor):
        self._ocr = ocr
        self._obs_data = TypedObservable(dict)
        self._pipeline = TOcrPipeline(eventsys, accessor, self._obs_data)
        self._pipeline.activate()

    def recognize(self, box: tuple[int, int, int, int], _from: str, to: str):
        self._ocr.process_area(box)

    def terminate(self):
        self._ocr.terminate()

    def observable(self):
        return self._pipeline.observable()


class TOcrPipeline(ServicePipeline):
    services = []

    def __init__(self, eventsys, accessor, observable):
        super().__init__(eventsys, accessor)
        self._observable = observable

    def create_pipeline(self):
        return (
            (OcrService.Events.OUTPUT_RECEIVE, self.handle),
        )

    def handle(self, e):
        self.redirect_to_observer(
            observable=self._observable,
            data={
                'status': TOcrStatus.SUCCESS,
                'text': e.output['text']
            }
        )

    def observable(self):
        return self._observable

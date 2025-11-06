from common.observable import TypedObservable
from common.pipeline import ServicePipeline
from src.ocr.ocr import Ocr, OcrStatus
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
        self._pipeline.inject_data(1, {'from': _from, 'to': to})
        self._ocr.process_area(box)

    def terminate(self):
        self._ocr.terminate()

    def observable(self):
        return self._pipeline.observable()


class TOcrPipeline(ServicePipeline):
    services = (TranslationService,)

    def __init__(self, eventsys, accessor, observable):
        super().__init__(eventsys, accessor)
        self._observable = observable

    def create_pipeline(self):
        return (
            (OcrService.Events.OUTPUT_RECEIVE, self.handle_ocr_output),
            (TranslationService.Events.OUTPUT_RECEIVE, self.handle_translation_output),
        )

    def handle_ocr_output(self, e):
        if e.output['status'] == OcrStatus.ERROR:
            self.redirect_to_observer(
                observable=self._observable,
                data={
                    'status': TOcrStatus(e.output['status'].value),
                    'text': e.output['text']
                }
            )
            return

        translation_s = self.get_service(TranslationService)
        inj = self.get_injected_data()
        translation_s.translate(e.output['text'], inj['from'], inj['to'])

    def handle_translation_output(self, e):
        self.redirect_to_observer(
            observable=self._observable,
            data={
                'status': TOcrStatus(e.output['status'].value),
                'text': e.output['text']
            }
        )

    def observable(self):
        return self._observable

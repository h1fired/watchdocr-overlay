from common.service import Service
from common.event import IEvent
from common.task import TaskManager
from common.pipeline import Pipeline
from src.ocr.service import OcrService
from src.translator.service import TranslationService
from src.grabber.service import ImageGrabberService
from enum import IntEnum


class TOcrStatus(IntEnum):
    ERROR = 0
    SUCCESS = 1
    RECOGNIZING = 2


class _TOcrResponceReceiveEvent(IEvent):
    status: TOcrStatus
    text: str


class TOcrService(Service):

    class Events:
        RESPONSE_RECEIVED = _TOcrResponceReceiveEvent

    def on_full_init(self):
        self._p = OcrTranslatePipeline(self.get_related, self.event)
        self._p.activate()

    def recognize(self, box: tuple[int, int, int, int], _from: str, to: str):
        self.event.dispatch(
            event=self.Events.RESPONSE_RECEIVED,
            data={
                'status': TOcrStatus.RECOGNIZING,
                'text': 'Recognizing...'
            }
        )
        self._p.inject_data(1, {'from': _from, 'to': to})
        self._p.process(box)

    def terminate(self):
        self._p.terminate()

    def on_task_finish(self, result):
        self.event.dispatch(
            event=self.Events.RESPONSE_RECEIVED,
            data={
                'status': result['status'],
                'text': result['text']
            }
        )


# Test
class OcrTranslatePipeline(Pipeline):
    services = (ImageGrabberService, OcrService, TranslationService)
    tasks = ('task.ocrtranslate.recognize', 'task.ocrtranslate.translate')

    def process(self, box: tuple[int, int, int, int]):
        s = self.get_service(ImageGrabberService)
        s.grab_window_area(box)

    def terminate(self):
        for id in self.tasks:
            if TaskManager.objects().exists(id):
                task = TaskManager.objects().get(id)
                task.cancel()
                task.wait()

    def create_pipeline(self):
        return (
            (ImageGrabberService.Events.IMAGE_CAPTURE, self.handle_grabber_image_receive),
            (OcrService.Events.OUTPUT_RECEIVE, self.handle_ocr_output_receive),
            (TranslationService.Events.OUTPUT_RECEIVE, self.handle_translation_output_receive)
        )

    def handle_grabber_image_receive(self, e):
        s = self.get_service(OcrService)
        TaskManager.execute(
            task=lambda _: s.recognize(e.image),
            id=self.tasks[0]
        )

    def handle_ocr_output_receive(self, e):
        inj_data = self.get_injected_data()
        s = self.get_service(TranslationService)
        TaskManager.execute(
            task=lambda _: s.translate(
                e.output['text'],
                inj_data['from'],
                inj_data['to']
            ),
            id=self.tasks[1]
        )

    def handle_translation_output_receive(self, e):
        self.redirect_to(
            event=TOcrService.Events.RESPONSE_RECEIVED,
            data={'status': TOcrStatus.SUCCESS, 'text': e.output['text']}
        )

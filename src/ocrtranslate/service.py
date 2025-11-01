from common.service import Service
from common.event import IEvent
from common.task import TaskManager, Pipeline
from src.ocr.service import OcrService
from src.translator.service import TranslationService
from src.grabber.service import ImageGrabberService
from enum import IntEnum


TASK_NAME = 'task.ocrtranslate.recognition'


class OcrTranslateStatus(IntEnum):
    ERROR = 0
    SUCCESS = 1
    RECOGNIZING = 2


class OcrTranslateRecognitionPipeline(Pipeline):
    def __init__(self, box, _from, to, ocr_s, translation_s, image_grabber_s):
        super().__init__()
        self._box = box
        self._from = _from
        self._to = to
        self._ocr_s = ocr_s
        self._translation_s = translation_s
        self._grabber_s = image_grabber_s

    def stage1(self, data):
        return self._grabber_s.grab_window_area(self._box)

    def stage2(self, image):
        return self._ocr_s.recognize(image)

    def stage3(self, result):
        result = self._translation_s.translate(result['text'], self._from, self._to)
        return {'status': OcrTranslateStatus.SUCCESS, 'text': result['text']}


class _OcrTranslateResponceReceiveEvent(IEvent):
    status: OcrTranslateStatus
    text: str


class OcrTranslateService(Service):

    class Events:
        RESPONSE_RECEIVED = _OcrTranslateResponceReceiveEvent

    def recognize(self, box: tuple[int, int, int, int], _from: str, to: str):
        self.event.dispatch(
            event=self.Events.RESPONSE_RECEIVED,
            data={
                'status': OcrTranslateStatus.RECOGNIZING,
                'text': 'Recognizing...'
            }
        )

        ocr_s = self.get_related(OcrService)
        translation_s = self.get_related(TranslationService)
        image_grabber_s = self.get_related(ImageGrabberService)
        pipeline = OcrTranslateRecognitionPipeline(box, _from, to, ocr_s, translation_s, image_grabber_s)
        future = TaskManager.execute(pipeline, id=TASK_NAME)
        future.observe(on_finish=lambda: self.on_task_finish(future.result()))

    def terminate(self):
        if TaskManager.objects().exists(TASK_NAME):
            task = TaskManager.objects().get(TASK_NAME)
            task.cancel()
            task.wait()

    def on_task_finish(self, result):
        self.event.dispatch(
            event=self.Events.RESPONSE_RECEIVED,
            data={
                'status': result['status'],
                'text': result['text']
            }
        )

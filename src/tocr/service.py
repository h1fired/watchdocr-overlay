from common.service import Service
from common.event import IEvent
from common.task import TaskManager, Pipeline
from src.tocr.window import grab_window_area
from src.ocr.service import OcrService
from enum import IntEnum


TASK_NAME = 'task.ocrtranslate.recognition'


class OcrTranslateStatus(IntEnum):
    ERROR = 0
    SUCCESS = 1
    RECOGNIZING = 2


class OcrTranslateRecognitionPipeline(Pipeline):
    def __init__(self, box, ocr_s):
        super().__init__()
        self._box = box
        self._ocr_s = ocr_s

    def stage1(self, data):
        return grab_window_area(self._box)

    def stage2(self, image):
        return self._ocr_s.recognize(image)


class _OcrTranslateResponceReceiveEvent(IEvent):
    status: OcrTranslateStatus
    text: str


class OcrTranslateService(Service):

    class Events:
        RESPONSE_RECEIVED = _OcrTranslateResponceReceiveEvent

    def recognize(self, box: tuple[int, int, int, int]):
        self.event.dispatch(
            event=self.Events.RESPONSE_RECEIVED,
            data={
                'status': OcrTranslateStatus.RECOGNIZING,
                'text': 'Recognizing...'
            }
        )

        ocr_s = self.get_related(OcrService)
        pipeline = OcrTranslateRecognitionPipeline(box, ocr_s)
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
                'status': OcrTranslateStatus(result['status']),
                'text': result['text']
            }
        )

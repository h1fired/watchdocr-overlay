from common.service import Service
from common.event import IEvent
from common.task import TaskManager, Task
from src.tocr.window import grab_window_area
from src.ocr.service import OcrService


class _OcrTranslateTextReceiveEvent(IEvent):
    status: int
    text: str


class OcrTranslateService(Service):

    class Events:
        TEXT_RECEIVED = _OcrTranslateTextReceiveEvent

    def recognize(self, box: tuple[int, int, int, int]):
        ocr_s = self.get_related(OcrService)
        task = OcrTranslateRecognizeTask(box, ocr_s)
        future = TaskManager.execute(task)
        future.observe(on_result=self.on_task_result)

    def on_task_result(self, result):
        self.event.dispatch(
            event=self.Events.TEXT_RECEIVED,
            data={
                'status': int(result['status'].value),
                'text': result['text']
            }
        )


class OcrTranslateRecognizeTask(Task):
    def __init__(self, box, ocr):
        super().__init__()
        self._box = box
        self._ocr = ocr

    def executable(self, token):
        image = grab_window_area(self._box)
        response = self._ocr.recognize(image)
        return response

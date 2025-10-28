from common.service import Service
from common.event import IEvent
from src.tocr.window import grab_window_area
from src.ocr.service import OcrService


class _OcrTranslateTextReceiveEvent(IEvent):
    status: int
    text: str


class OcrTranslateService(Service):

    class Events:
        TEXT_RECEIVED = _OcrTranslateTextReceiveEvent

    def recognize(self, box: tuple[int, int, int, int]):
        image = grab_window_area(box)

        ocr_s = self.get_related(OcrService)
        response = ocr_s.recognize(image)

        self.event.dispatch(
            event=self.Events.TEXT_RECEIVED,
            data={
                'status': int(response['status'].value),
                'text': response['text']
            }
        )

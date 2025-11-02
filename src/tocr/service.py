from common.service import Service
from common.event import IEvent
from src.tocr.manager import TOcr, TOcrStatus
from src.ocr.service import OcrService


class _TOcrResponceReceiveEvent(IEvent):
    status: TOcrStatus
    text: str


class TOcrService(Service):

    class Events:
        RESPONSE_RECEIVED = _TOcrResponceReceiveEvent

    def on_init(self):
        ocr_s = self.get_related(OcrService)
        self._tocr = TOcr(ocr_s, self.event, self.get_related)
        self._tocr.obs_output.register(self.on_ocr_output)

    def recognize(self, box: tuple[int, int, int, int], _from: str, to: str):
        self._tocr.process_area(box, _from, to)

    def terminate(self):
        self._tocr.terminate()

    def on_ocr_output(self, output):
        self.event.dispatch(
            event=self.Events.RESPONSE_RECEIVED,
            data={
                'status': output['status'],
                'text': output['text']
            }
        )

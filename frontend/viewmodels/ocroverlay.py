from common.event import Event
from frontend.common.mvvm import ViewModel
from src.ocr.service import OCRTranslateService


class OCROverlayViewModel(ViewModel):
    context_id = 'ocroverlay'

    def on_load(self):
        # ocr_translate_s = self.get_service(OCRTranslateService)

        Event.subscribe(
            system=self.event(),
            event=OCRTranslateService.Events.DATA_RECEIVE,
            handler=self.on_ocr_translate_data_receive
        )

    def on_ocr_translate_data_receive(self, e):
        print(e)

from src.ocr.backends import OcrBackend, OcrStatus
from tesserocr import PyTessBaseAPI, PSM, OEM


DATA_MODELS_DIR = 'data/tessdata-4.1.0'


class TesseractOcrBackend(OcrBackend):
    name = 'Tesseract'

    def __init__(self):
        self._api = PyTessBaseAPI(
            path=DATA_MODELS_DIR,
            oem=OEM.LSTM_ONLY,
            psm=PSM.SPARSE_TEXT_OSD
        )

    def recognize(self, image):
        try:
            self._api.SetImage(image)
            text = self._api.GetUTF8Text()
        except Exception as e:
            return {'status': OcrStatus.ERROR, 'text': repr(e)}
        return {'status': OcrStatus.SUCCESS, 'text': text}

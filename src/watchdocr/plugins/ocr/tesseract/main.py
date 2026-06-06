from tesserocr import PyTessBaseAPI, PSM, OEM, RIL, iterate_level
from PIL import Image
from src.watchdocr.plugins.ocr import OcrPlugin, OcrData
from src.watchdocr.plugins.ocr.tesseract.filter import OcrImageFilter


__plugin_meta__ = {
    'id': 'watchdocr.ocr.tesseract',
    'name': 'TesseractOCR',
    'version': (0, 1, 0)
}
__plugin_main__ = 'TesseractOcrPlugin'


DATA_MODELS_DIR = 'data/tessdata-main'


class TesseractOcrPlugin(OcrPlugin):
    def on_startup(self):
        self._api = PyTessBaseAPI(
            path=DATA_MODELS_DIR,
            oem=OEM.LSTM_ONLY,
            psm=PSM.AUTO
        )

    def _optimize_image(self, image: Image.Image):
        return OcrImageFilter.adjust(image)

    def recognize(self, image: Image.Image):
        try:
            image = self._optimize_image(image)  # Prepare image

            self._api.SetImage(image)

            text = self._api.GetUTF8Text()
            global_conf = self._api.MeanTextConf()
            boxes = []

            # Get components parameters (words, boxes, confidences)
            ri = self._api.GetIterator()
            level = RIL.WORD
            for r in iterate_level(ri, level):
                word = r.GetUTF8Text(level)
                box = r.BoundingBox(level)
                conf = r.Confidence(level)
                boxes.append((word, box, conf))
            return OcrData(text, boxes, global_conf)
        except Exception:
            return OcrData('', tuple(), 0)

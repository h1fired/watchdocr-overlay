from tesserocr import PyTessBaseAPI, PSM, OEM, RIL, iterate_level
from PIL import Image


DATA_MODELS_DIR = 'data/tessdata-main'


class OcrData:
    def __init__(
        self, text: str | None,
        boxes: tuple,
        confidence: int
    ):
        self._text = text
        self._boxes = boxes
        self._conf = confidence

    def boxes(self):
        return self._boxes

    def text(self):
        return self._text

    def confidence(self):
        return self._conf


class TesseractOcrPlugin:
    def on_load(self):
        self._api = PyTessBaseAPI(
            path=DATA_MODELS_DIR,
            oem=OEM.LSTM_ONLY,
            psm=PSM.AUTO
        )

    def recognize(self, image: Image.Image):
        try:
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

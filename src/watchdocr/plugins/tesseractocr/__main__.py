from tesserocr import PyTessBaseAPI, PSM, OEM, RIL, iterate_level


DATA_MODELS_DIR = 'data/tessdata-4.1.0'


class OcrData:
    def __init__(self, text: str | None, boxes: tuple):
        self._text = text
        self._boxes = boxes

    def boxes(self):
        return self._boxes

    def text(self):
        return self._text


class TesseractOcrPlugin:
    def on_load(self):
        self._api = PyTessBaseAPI(
            path=DATA_MODELS_DIR,
            oem=OEM.LSTM_ONLY,
            psm=PSM.SPARSE_TEXT_OSD
        )

    def recognize(self, image, scaler):
        try:
            self._api.SetImage(image)

            text = self._api.GetUTF8Text()
            boxes = []

            # Get components parameters (words, boxes, confidences)
            ri = self._api.GetIterator()
            level = RIL.WORD
            for r in iterate_level(ri, level):
                word = r.GetUTF8Text(level)
                box = self.rescale_box(r.BoundingBox(level), scaler)
                conf = r.Confidence(level)
                boxes.append((word, box, conf))
            return OcrData(text, boxes)
        except Exception:
            return OcrData(None, '')

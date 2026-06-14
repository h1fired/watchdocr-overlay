from src.watchdocr.plugins.ocr import OcrPlugin, OcrData
from PIL import Image
from rapidocr import RapidOCR


__plugin_meta__ = {
    'id': 'watchdocr.ocr.rapid',
    'name': 'RapidOCR',
    'version': (0, 1, 0)
}
__plugin_main__ = 'RapidOcrPlugin'


class RapidOcrPlugin(OcrPlugin):
    def on_startup(self):
        self._api = RapidOCR()

    def get_priority(self):
        return 1

    def get_provider_name(self):
        return 'Rapid'

    def recognize(self, image: Image.Image):
        try:
            image = self.filter_image(image)

            res = self._api(image)
            if not len(res.txts):
                raise
            text = ' '.join(res.txts)
            text = self.cleanup_text(text)
            global_conf = int((sum(res.scores) / len(res.scores)) * 100)
            boxes = []
            for i, b in enumerate(res.boxes):
                a = int(b[0][0]), int(b[0][1]), int(b[2][0]), int(b[2][1])
                boxes.append((res.txts[i], a, res.scores[i]))

            return OcrData(text, tuple(boxes), global_conf)
        except Exception:
            return OcrData('', tuple(), 0)

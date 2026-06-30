from src.watchdocr.plugins.ocr import OcrPlugin, OcrData, OcrOptimization
from src.watchdocr.plugins.ocr.windows_one.engine import OcrEngine, OcrLine
from PIL import Image
import os


__plugin_meta__ = {
    'id': 'watchdocr.ocr.windows_one',
    'name': 'WindowsOneOCR',
    'version': (0, 1, 0)
}
__plugin_main__ = 'WindowsOneOcrPlugin'


DLLS_PATH = os.path.normpath('src/watchdocr/plugins/ocr/windows_one/data/')


class WindowsOneOcrPlugin(OcrPlugin):

    def on_startup(self):
        self._api = OcrEngine(dlls_path=DLLS_PATH)

    def get_priority(self):
        return 1

    def get_provider_name(self):
        return 'WindowsOne'

    def recognizable(self, image: Image.Image):
        image, scale = self.process_image(image)
        res = self._api.recognize(image)
        boxes = self._parse_boxes(res.lines, scale)
        return OcrData(True, res.text, tuple(boxes), 0.)

    def _parse_boxes(self, rlines: tuple[OcrLine, ...], scale: float):
        boxes = []
        for line in rlines:
            words = line.words

            if words:
                xs = [coord for w in words for coord in w.boundings[0::2]]
                ys = [coord for w in words for coord in w.boundings[1::2]]
                confidences = [w.confidence for w in words if w.confidence is not None]
                line_confidence = sum(confidences) / len(confidences) if confidences else 0.
            elif line.boundings:
                xs = line.boundings[0::2]
                ys = line.boundings[1::2]
                line_confidence = 0.
            else:
                continue

            x, y, x2, y2 = min(xs), min(ys), max(xs), max(ys)

            boxes.append((
                line.text,
                (
                    int(x / scale),
                    int(y / scale),
                    int(x2 / scale),
                    int(y2 / scale)
                ),
                line_confidence
            ))
        return boxes

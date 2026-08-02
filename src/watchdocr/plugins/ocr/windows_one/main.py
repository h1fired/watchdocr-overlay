from src.common.plugin import DownloadResource, DownloadablePlugin
from src.watchdocr.plugins.ocr import OcrPlugin, OcrData, OcrBoxData
from src.watchdocr.plugins.ocr.windows_one.engine import OcrEngine, OcrLine
from PIL import Image


__plugin_meta__ = {
    'id': 'watchdocr-ocr-windowsone',
    'name': 'WindowsOneOCR',
    'version': (0, 1, 0)
}
__plugin_main__ = 'WindowsOneOcrPlugin'


RESOURCE_PATH = 'https://github.com/h1fired/watchdocr-overlay/releases/download/v0.1.0/watchdocr_windowsone_ocr_data.zip'


class WindowsOneOcrPlugin(OcrPlugin, DownloadablePlugin):
    _id = 'windowsone_ocr'

    def on_after_download(self):
        dlls_path = self.get_resource_path()
        self._api = OcrEngine(dlls_path=dlls_path)

    def get_download_resource(self):
        return DownloadResource(RESOURCE_PATH)

    def get_priority(self):
        return 1

    def get_provider_name(self):
        return 'WindowsOne'

    def recognizable(self, image: Image.Image, scale: float):
        res = self._api.recognize(image)
        boxes = self._parse_boxes(res.lines, scale)
        return OcrData(True, res.text, tuple(boxes), 0.)

    def _parse_boxes(self, rlines: tuple[OcrLine, ...], scale: float):
        boxes = []
        for line in rlines:
            words = line.words

            if words:
                confs = [w.confidence for w in words if w.confidence is not None]
                line_confidence = sum(confs) / len(confs) if confs else 0.
            elif line.boundings:
                line_confidence = 0.
            else:
                continue

            line_coordinates = tuple([int(b / scale) for b in line.boundings])
            line_boundings = self._coords_to_boundings(line.boundings)

            box = OcrBoxData(
                text=line.text,
                boundings=line_boundings,
                confidence=line_confidence,
                coordinates=line_coordinates,
                has_perspective=True
            )
            boxes.append(box)
        return boxes

    def _coords_to_boundings(self, bbox: tuple[int, ...]):
        xs = bbox[0::2]
        ys = bbox[1::2]

        x1 = min(xs)
        y1 = min(ys)
        x2 = max(xs)
        y2 = max(ys)

        return (x1, y1, x2, y2)

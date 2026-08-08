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


RESOURCE_URL = 'https://github.com/h1fired/watchdocr-overlay/releases/download/v0.1.0/watchdocr_windowsone_ocr_data.zip'
RESOURCE_SHA256 = '03c4b49f0f4e863b1027e19ae84575c2c399870818d9c56bfc347e09711f74bf'


class WindowsOneOcrPlugin(OcrPlugin, DownloadablePlugin):
    _id = 'windowsone_ocr'

    def on_after_download(self):
        dlls_path = self.get_resource_path()
        self._api = OcrEngine(dlls_path=dlls_path)

    def get_download_resource(self):
        return DownloadResource(
            url=RESOURCE_URL,
            sha256=RESOURCE_SHA256
        )

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

            box = OcrBoxData(
                text=line.text,
                coordinates=line_coordinates,
                confidence=line_confidence,
                has_perspective=True
            )
            boxes.append(box)
        return boxes

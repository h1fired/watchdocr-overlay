from src.backend.plugins.ocr import OcrPlugin, OcrData
from PIL import Image


__plugin_meta__ = {
    'id': 'watchdocr-ocr-dummy',
    'name': 'DummyOCR',
    'version': (0, 1, 0)
}
__plugin_main__ = 'DummyOcrPlugin'


class DummyOcrPlugin(OcrPlugin):
    def get_provider_name(self):
        return 'Dummy'

    def recognizable(self, image: Image.Image, scale: float):
        return OcrData(True, 'Dummy text', tuple(), 0., True)

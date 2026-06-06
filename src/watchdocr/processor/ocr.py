from src.common.plugin import PluginManager
from src.watchdocr.plugins.ocr import OcrPlugin
from PIL import Image


class Ocr:
    def __init__(self, plugins_manager: PluginManager):
        self._plugins_manager = plugins_manager

    def recognize(self, image: Image.Image):
        apis = self._plugins_manager.get_realizations(OcrPlugin)
        if not len(apis):
            raise ValueError('OCR backend plugins not found')
        api = apis[0]
        return api.recognize(image)

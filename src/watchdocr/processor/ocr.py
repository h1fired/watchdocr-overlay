from src.common.plugin import PluginManager
from src.watchdocr.plugins.ocr import OcrPlugin
from src.common.utils.logging import log
from PIL import Image


class Ocr:
    def __init__(self, plugins_manager: PluginManager):
        self._plugins_manager = plugins_manager

    def recognize(self, image: Image.Image):
        apis = self._plugins_manager.get_realizations(OcrPlugin)
        if not len(apis):
            log.error('No OCR backend plugins found!', extra={'title': 'OCR'})
            raise ValueError('OCR backend plugins not found')
        api = sorted(apis, key=lambda e: e.get_priority())[0]
        return api.recognize(image)

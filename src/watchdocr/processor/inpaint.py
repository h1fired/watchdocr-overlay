from src.common.plugin import PluginManager
from src.watchdocr.plugins.image.textremover import ImageTextRemoverPlugin
from src.common.utils.logging import log
from PIL import Image


class ImageTextRemover:
    def __init__(self, plugins_manager: PluginManager):
        self._plugins_manager = plugins_manager

    def filter_image(self, image: Image.Image, boxes: tuple):
        apis = self._plugins_manager.get_realizations(ImageTextRemoverPlugin)
        if not len(apis):
            log.error(
                'No text remover backend plugins found!',
                extra={'title': 'TEXT REMOVER'}
            )
            raise ValueError('Text remover backend plugins not found')
        api = sorted(apis, key=lambda e: e.get_priority())[0]
        return api.filter_image(image)

from src.common.plugin import PluginManager
from src.watchdocr.plugins.image.textremover import ImageTextRemoverPlugin
from src.common.utils.logging import log
from PIL import Image
import numpy as np
import cv2


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

        mask = self._create_mask(image.width, image.height, boxes)

        return api.filter_image(image, mask)

    def _create_mask(self, width: int, height: int, boxes: tuple):
        mask = np.zeros((height, width), dtype=np.uint8)
        for x, y, w, h in boxes:
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, thickness=-1)
        return Image.fromarray(mask)

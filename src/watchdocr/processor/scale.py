from src.watchdocr.plugins.ocr import OcrData
from config import config
from typing import Callable
import math


ADAPTIVE_MODE = 'adaptive'


def quad_height(coordinates: tuple[int, ...]):
    '''Average length of left and right edges, works for rotated text'''
    if len(coordinates) != 8:
        return 0.
    x1, y1, x2, y2, x3, y3, x4, y4 = coordinates
    left = math.hypot(x4 - x1, y4 - y1)
    right = math.hypot(x3 - x2, y3 - y2)
    return (left + right) / 2


class RecognitionScaler:
    '''
    Chooses the scale image is shrunk by before OCR.

    In adaptive mode the smallest text line of the previous recognition
    of the same selection area gets target height. Image is never enlarged.
    '''

    def __init__(self, mode_provider: Callable[[], str]):
        self._mode_provider = mode_provider
        self._area: tuple[int, int, int, int] | None = None
        self._text_height: float | None = None

    def scale_for(
        self,
        area: tuple[int, int, int, int],
        image_size: tuple[int, int],
        min_image_size: int
    ):
        scale = self._base_scale(image_size)

        if area != self._area or not self._text_height:
            return scale
        if self._mode_provider() != ADAPTIVE_MODE:
            return scale

        # Keeps image acceptable for the backend
        adaptive = max(
            config.OCR_ADAPTIVE_TEXT_HEIGHT / self._text_height,
            config.OCR_ADAPTIVE_MIN_SCALE,
            min_image_size / max(min(image_size), 1)
        )
        return min(scale, adaptive)

    def retry_scale(
        self,
        scale: float,
        image_size: tuple[int, int],
        data: OcrData
    ):
        # Shrunk too much (text got smaller), retry with full image
        base_scale = self._base_scale(image_size)
        if scale < base_scale and data.success and not data.boxes:
            return base_scale
        return None

    def remember(self, area: tuple[int, int, int, int], data: OcrData):
        heights = [
            h for b in data.boxes
            if (h := quad_height(b.coordinates)) > 0
        ] if data.success else []

        self._area = area
        self._text_height = min(heights) if heights else None

    @staticmethod
    def _base_scale(image_size: tuple[int, int]):
        # Decrease size of image if it bigger that max size
        w, h = image_size
        max_size = config.OCR_MAX_RECOGNITION_RES
        if w > max_size or h > max_size:
            return min(max_size / w, max_size / h)
        return 1.0

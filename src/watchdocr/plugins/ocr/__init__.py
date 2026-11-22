from src.common.plugin import LaunchPlugin, EventPlugin, PriorityPlugin
from src.watchdocr.plugins.ocr.filter import OcrImageFilter
from PIL import Image
from dataclasses import dataclass, asdict
from enum import IntFlag
import asyncio
import math
import re


@dataclass(slots=True, frozen=True)
class OcrBoxData:
    text: str
    coordinates: tuple[int, ...] = (0, 0, 0, 0, 0, 0, 0, 0)
    confidence: float = 0.


@dataclass(slots=True, frozen=True)
class OcrData:
    success: bool
    text: str
    boxes: tuple[OcrBoxData, ...]
    confidence: float
    has_perspective: bool = False

    def to_dict(self):
        return asdict(self)


class OcrOptimization(IntFlag):
    NONE = 0
    FILTER_GRAYSCALE = 1 << 2
    FILTER_SHADOW_REMOVE = 1 << 3


class OcrPlugin(LaunchPlugin, EventPlugin, PriorityPlugin):

    class Capabilities:
        optimizations = OcrOptimization.NONE
        min_image_size = 0  # Smallest image side the backend accepts

    def __init__(self):
        super().__init__()
        self._optimizations = self.Capabilities.optimizations

    async def recognize(
        self,
        image: Image.Image,
        scale: float = 1.0
    ) -> OcrData:
        try:
            # Resizing and filtering is CPU heavy, run it in thread
            image = await asyncio.to_thread(self.process_image, image, scale)
            return await self.recognizable(image, scale)
        except Exception as e:
            return OcrData(
                success=False,
                text=f'Failed to recognize text! Error: {e}',
                boxes=tuple(),
                confidence=0.
            )

    async def recognizable(self, image: Image.Image, scale: float) -> OcrData:
        raise NotImplementedError

    def get_provider_name(self):
        return 'Unknown'

    def provided_offset(self):
        return (0, 0)

    def cleanup_text(self, text: str):
        ctext = re.sub(r'[ \t]+', ' ', text)  # Clean multiple whitespaces
        ctext = re.sub(r'\n+', '\n', ctext)  # Clean newlines mid-sentence
        ctext = re.sub(r'\n{3,}', '\n\n', ctext)  # Clean excessive blank lines
        return ctext

    def process_image(self, image: Image.Image, scale: float):
        if self._optimizations != OcrOptimization.NONE:
            if OcrOptimization.FILTER_GRAYSCALE & self._optimizations:
                image = OcrImageFilter.adjust_to_grayscale(image)
            if OcrOptimization.FILTER_SHADOW_REMOVE & self._optimizations:
                image = OcrImageFilter.adjust_shadow_remove(image)

        if scale != 1.0:
            w, h = image.size
            new_w = math.ceil(w * scale)
            new_h = math.ceil(h * scale)
            image = image.resize((new_w, new_h), Image.Resampling.BILINEAR)

        return image

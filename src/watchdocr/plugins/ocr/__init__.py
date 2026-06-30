from src.common.plugin import LaunchPlugin, EventPlugin, PriorityPlugin
from src.watchdocr.plugins.ocr.filter import OcrImageFilter
from PIL import Image
from dataclasses import dataclass
from enum import IntFlag
import re


@dataclass(slots=True, frozen=True)
class OcrData:
    success: bool
    text: str
    boxes: tuple
    confidence: float


class OcrOptimization(IntFlag):
    NONE = 0
    ADAPTIVE_SIZE = 1 << 0
    FILTER_GRAYSCALE = 1 << 2
    FILTER_SHADOW_REMOVE = 1 << 3


class OcrPlugin(LaunchPlugin, EventPlugin, PriorityPlugin):

    class Options:
        optimizations = OcrOptimization.NONE

    def __init__(self):
        super().__init__()
        self._optimizations = self.Options.optimizations

    def recognize(self, image: Image.Image) -> OcrData:
        try:
            return self.recognizable(image)
        except Exception as e:
            return OcrData(
                success=False,
                text=f'Failed to recognize text! Error: {e}',
                boxes=tuple(),
                confidence=0.
            )

    def recognizable(self, image: Image.Image) -> OcrData:
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

    def process_image(self, image: Image.Image):
        # Change image mode to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Scale image based on image height
        w, h = image.size

        scale = 1.0
        if OcrOptimization.ADAPTIVE_SIZE & self._optimizations:
            scale = 4.0 if h < 150 else 3.0 if h < 300 else 2.0 if h < 600 else 1.0
        if OcrOptimization.FILTER_GRAYSCALE & self._optimizations:
            image = OcrImageFilter.adjust_to_grayscale(image)
        if OcrOptimization.FILTER_SHADOW_REMOVE & self._optimizations:
            image = OcrImageFilter.adjust_shadow_remove(image)

        if scale != 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        return image, scale

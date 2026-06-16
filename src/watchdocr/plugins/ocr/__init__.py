from src.common.plugin import LaunchPlugin, EventPlugin, PriorityPlugin
from src.watchdocr.plugins.ocr.filter import OcrImageFilter
from PIL import Image
from dataclasses import dataclass
import re


@dataclass(slots=True, frozen=True)
class OcrData:
    text: str
    boxes: tuple
    confidence: float


class OcrPlugin(LaunchPlugin, EventPlugin, PriorityPlugin):
    def recognize(self, image: Image.Image) -> OcrData:
        raise NotImplementedError

    def get_provider_name(self):
        return 'Unknown'

    def provided_offset(self):
        return (0, 0)

    def cleanup_text(self, text: str):
        ctext = re.sub(r'[ \t]+', ' ', text)  # Clean multiple whitespaces
        ctext = re.sub(r'\n+', '\n', text)  # Clean newlines mid-sentence
        ctext = re.sub(r'\n{3,}', '\n\n', text)  # Clean excessive blank lines
        return ctext

    def process_image(self, image: Image.Image):
        # Change image mode to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Scale image based on image height
        w, h = image.size

        if h < 300:
            scale_factor = 3.0
        elif h < 600:
            scale_factor = 2.0
        else:
            scale_factor = 1.0

        if scale_factor != 1.0:
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        return image, scale_factor

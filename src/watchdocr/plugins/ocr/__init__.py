from src.common.plugin import LaunchPlugin, EventPlugin, PriorityPlugin
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

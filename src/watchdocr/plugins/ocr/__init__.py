from src.common.plugin import LaunchPlugin, EventPlugin
from PIL import Image
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class OcrData:
    text: str
    boxes: tuple
    confidence: float


class OcrPlugin(LaunchPlugin, EventPlugin):
    def recognize(self, image: Image.Image) -> OcrData:
        raise NotImplementedError

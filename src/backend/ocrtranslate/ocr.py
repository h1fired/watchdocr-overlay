from src.backend.common.plugin import PluginManager
from src.backend.common.utils.logging import log
from src.backend.plugins.ocr import OcrPlugin, OcrBoxData
from PIL import Image
from pydantic import BaseModel, ConfigDict, field_validator


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


class OcrBox(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

    confidence: float
    coordinates: tuple[int, int, int, int, int, int, int, int]

    @field_validator('confidence')
    @classmethod
    def _check_confidence(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError('Confidence must be within [0.0, 1.0]')
        return v

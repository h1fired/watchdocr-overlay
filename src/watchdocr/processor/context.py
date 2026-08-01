from pydantic import BaseModel, ConfigDict, field_validator
from PIL import Image
from typing import Optional


LOG_CONTEXT = 'Runtime Context'


class ContextModel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

    def clear(self):
        for name, info in self.__class__.model_fields.items():
            default_value = info.default if info.default is not None else None
            setattr(self, name, default_value)


class RuntimeConfig(ContextModel):
    boundings: tuple[int, int, int, int] = (0, 0, 0, 0)
    source_language: str = ''
    target_language: str = ''


class OcrBox(ContextModel):
    boundings: tuple[int, int, int, int]
    confidence: float

    @field_validator('confidence')
    @classmethod
    def _check_confidence(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError('Confidence must be within [0.0, 1.0]')
        return v


class OcrContext(ContextModel):
    success: bool = False
    ignore: bool = False

    text: str = ''
    boxes: tuple[OcrBox, ...] = ()
    parts: tuple[str, ...] = ()
    total_confidence: float = 0.


class TranslationContext(ContextModel):
    success: bool = False

    text: str = ''
    parts: tuple[str, ...] = ()


class WatchdOcrRuntimeContext(ContextModel):
    config: RuntimeConfig = RuntimeConfig()
    ocr: OcrContext = OcrContext()
    translation: TranslationContext = TranslationContext()
    image: Optional[Image.Image] = None

    def update_config(self, data: dict):
        for key, value in data.items():
            setattr(self.config, key, value)

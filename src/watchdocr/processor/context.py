from src.common.utils.logging import log
from src.watchdocr.processor.ocr import OcrBoxData
from dataclasses import dataclass, fields, field, is_dataclass
from PIL import Image
from typing import Any


LOG_CONTEXT = 'Runtime Context'


class ReadOnlyProxy:
    def __init__(self, target: Any):
        super().__setattr__('_target', target)

    def __setattr__(self, *_):
        raise AttributeError('Read-only proxy enabled, attrs modify not allowed')

    def __getattr__(self, name):
        value = getattr(self._target, name)
        if is_dataclass(value) and not isinstance(value, type):
            return ReadOnlyProxy(value)
        return value

    def __repr__(self):
        return f'ReadOnlyProxy({self._target!r})'


@dataclass(slots=True)
class RuntimeConfig:
    boundings: tuple = (0, 0, 0, 0)

    source_language: str = ''
    target_language: str = ''

    def clear(self):
        self.boundings = (0, 0, 0, 0)
        self.source_language = ''
        self.target_language = ''


@dataclass(slots=True)
class OcrBox:
    boundings: tuple
    confidence: float


@dataclass(slots=True)
class OcrContext:
    success: bool = False
    ignore: bool = False

    text: str = ''
    boxes: tuple[OcrBox, ...] = tuple()
    parts: list[str] = field(default_factory=list)
    total_confidence: float = 0.

    def clear(self):
        self.success = None
        self.ignore = False

        self.text = ''
        self.boxes = tuple()
        self.parts = {}
        self.total_confidence = 0.


@dataclass(slots=True)
class TranslationContext:
    success: bool = False

    text: str = ''
    parts: list[str] = field(default_factory=list)

    def clear(self):
        self.success = False

        self.text = ''
        self.parts = {}


@dataclass(slots=True)
class WatchdOcrRuntimeContext:
    config: RuntimeConfig = field(default_factory=RuntimeConfig)

    ocr: OcrContext = field(default_factory=OcrContext)
    translation: TranslationContext = field(default_factory=TranslationContext)

    image: Image.Image | None = None

    def clear(self):
        self.config.clear()

        self.image = None

        self.ocr.clear()
        self.translation.clear()

    def update_config(self, data: dict, __target: Any | None = None):
        target = __target if __target is not None else self.config
        field_names = {f.name for f in fields(target)}

        for key, value in data.items():
            if key not in field_names:
                log.warning(
                    'Invalid context field provided (%s). Ignore',
                    key,
                    extra={'title': LOG_CONTEXT})
                continue

            curr_field = getattr(target, key)

            if is_dataclass(curr_field) and isinstance(value, dict):
                self.update_config(value, curr_field)
            else:
                setattr(target, key, value)

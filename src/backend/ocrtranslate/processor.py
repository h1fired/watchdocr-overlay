from src.backend.ocrtranslate.pipeline import OcrTranslationPipeline
from src.backend.ocrtranslate.runner import (
    OcrTranslationRunner,
    OcrTranslationTask,
    ExecutionStrategy
)
from src.backend.ocrtranslate.ocr import Ocr
from src.backend.ocrtranslate.translator import Translator
from src.common.plugin import PluginManager


class OcrTranslationProcessor:
    def __init__(self, plugins: PluginManager):
        self._ocr = Ocr(plugins_manager=plugins)
        self._translator = Translator(plugins_manager=plugins)
        self._pipeline = OcrTranslationPipeline(plugins_manager=plugins)
        self._runner = OcrTranslationRunner(
            pipeline=self._pipeline,
            dependencies={
                'ocr': {
                    'ocr': self._ocr,
                },
                'translation': {
                    'translator': self._translator
                }
            }
        )

from src.backend.ocrtranslate.pipeline import OcrTranslationPipeline
from src.backend.ocrtranslate.runner import (
    OcrTranslationRunner,
    OcrTranslationTask,
    ExecutionStrategy
)
from src.backend.ocrtranslate.ocr import Ocr
from src.backend.ocrtranslate.translator import Translator
from src.common.plugin import PluginManager
from typing import Callable


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

    async def start(self):
        await self._runner.start()

    async def stop(self):
        await self._runner.stop()

    async def request(self, task: OcrTranslationTask):
        await self._runner.put(task)

    def add_output_callback(self, cb: Callable):
        self._runner.add_output_callback(cb)

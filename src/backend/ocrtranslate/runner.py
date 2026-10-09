from src.backend.core.runner import Runner
from src.backend.core.pipeline import PipelineConfig
from src.backend.ocrtranslate.pipeline import OcrTranslationPipeline
from pydantic import BaseModel, ConfigDict
from enum import IntEnum
from typing import Any, Callable


class ExecutionStrategy(IntEnum):
    ALL = 1
    OCR_ONLY = 2
    RETRANSLATE = 3


class OcrTranslationTask(BaseModel):
    model_config = ConfigDict(frozen=True)

    strategy: ExecutionStrategy
    context_data: dict[str, dict] = {}


class OcrTranslationRunner(Runner):
    def __init__(
        self,
        pipeline: OcrTranslationPipeline,
        dependencies: dict[str, Any]
    ):
        super().__init__()
        self._pipeline = pipeline
        self._dependencies = dependencies
        self._cb_output = None

    async def put(self, item: OcrTranslationTask):
        return await super().put(item)

    async def handle_item(self, item: OcrTranslationTask):
        config = PipelineConfig()

        strategy, data = item.strategy, item.context_data
        config.force_context_data = data
        if strategy == ExecutionStrategy.ALL:
            pass
        elif strategy == ExecutionStrategy.OCR_ONLY:
            config.ignored_stages = ['translation']
        elif strategy == ExecutionStrategy.RETRANSLATE:
            config.allowed_stages = ['translation']

        config.dependencies = self._dependencies

        output = await self._pipeline.run(config)
        if self._cb_output:
            await self._cb_output(output)

    def add_output_callback(self, cb: Callable):
        self._cb_output = cb

from src.backend.core.runner import Runner
from src.backend.core.pipeline import PipelineConfig
from src.backend.ocrtranslate.pipeline import OcrTranslationPipeline
from pydantic import BaseModel, ConfigDict
from enum import IntEnum
from typing import Any


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

    async def put(self, item: OcrTranslationTask):
        return await super().put(item)

    async def handle_item(self, item: OcrTranslationTask):
        config = PipelineConfig()

        strategy, data = item.strategy, item.context_data
        if strategy == ExecutionStrategy.ALL:
            pass
        elif strategy == ExecutionStrategy.OCR_ONLY:
            config.ignored_stages = ['translation']
        elif strategy == ExecutionStrategy.RETRANSLATE:
            config.force_context_data = data
            config.allowed_stages = ['translation']

        config.dependencies = self._dependencies

        # TODO: Need to emit output (callback etc.)
        _ = await self._pipeline.run(config)

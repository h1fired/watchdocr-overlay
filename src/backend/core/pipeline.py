from pydantic import BaseModel, ConfigDict
from typing import Sequence, Dict, Any
from types import SimpleNamespace
from src.backend.common.ex import UniqueError


class StageContext(BaseModel):
    pass


class Stage:
    name: str
    context_model: type[StageContext]

    def __init__(self, **kwargs):
        assert hasattr(self, 'name')
        assert hasattr(self, 'context_model'), '"context_model" property is not set'
        self._deps = SimpleNamespace(**kwargs)

    async def run(
        self,
        prev_ctx: StageContext | None = None,
        force_data: dict[str, Any] = {}
    ):
        ctx = self.context_model()

        if len(force_data):
            for name, attr in force_data.items():
                setattr(ctx, name, attr)

        return await self.runnable(ctx, prev_ctx)

    async def runnable(
        self,
        ctx: StageContext,
        prev_ctx: StageContext | None = None
    ) -> StageContext:
        raise NotImplementedError

    @property
    def deps(self):
        return self._deps


class PipelineSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    stages: list[type[Stage]]
    output_model: type['PipelineOutput']


class PipelineConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    skip_stages: list[str] = []
    dependencies: dict[str, dict] = {}
    force_context_data: dict[str, dict] = {}


class Pipeline:
    spec: PipelineSpec

    def __init__(self):
        assert hasattr(self, 'spec'), '"spec" property is not set'
        if not self._validate_stages_uniqueness(self.spec.stages):
            raise UniqueError('Stages IDs are not unique')

    async def run(self, config: PipelineConfig = PipelineConfig()):
        stages: Sequence[Stage] = []
        for s in self.spec.stages:
            obj = s(**config.dependencies.get(s.name, {}))
            stages.append(obj)

        ctxs = {}
        prev_ctx = None
        for stage in stages:
            force_data = config.force_context_data.get(stage.name, {})
            if stage.name in config.skip_stages:
                prev_ctx = stage.context_model(**force_data)
            else:
                prev_ctx = await stage.run(prev_ctx, force_data)
            ctxs[stage.name] = prev_ctx

        output = self.spec.output_model()
        return await self.handle_output(ctxs, output)

    async def handle_output(
        self,
        ctxs: Dict[str, StageContext],
        output: 'PipelineOutput'
    ):
        return output

    def _validate_stages_uniqueness(self, stages: Sequence[type[Stage]]):
        names = [s.name for s in stages]
        unique_names = set(names)
        return len(names) == len(unique_names)


class PipelineOutput(BaseModel):
    pass

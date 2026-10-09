from pydantic import BaseModel, ConfigDict
from typing import Sequence, Dict, Any
from types import SimpleNamespace
from src.backend.common.ex import UniqueError
from src.backend.core.plugin import PluginManager


class StageContext(BaseModel):
    model_config = ConfigDict(validate_assignment=True)


class Stage:
    name: str
    context_model: type[StageContext]

    def __init__(self, plugins_manager: PluginManager, **kwargs):
        assert hasattr(self, 'name')
        assert hasattr(self, 'context_model'), '"context_model" property is not set'
        self._deps = SimpleNamespace(**kwargs)
        self._plugins = plugins_manager

    @property
    def plugins(self):
        return self._plugins

    async def run(
        self,
        prev_ctx: StageContext | None = None,
        force_data: dict[str, Any] = {}
    ):
        ctx = self.context_model()

        if len(force_data):
            for name, attr in force_data.items():
                setattr(ctx, name, attr)

        ctx = await self.runnable(ctx, prev_ctx)
        if not ctx:
            raise RuntimeError('Stage should return context object, not None')
        return ctx

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
    ignored_stages: list[str] = []
    allowed_stages: list[str] = []
    dependencies: dict[str, dict] = {}
    force_context_data: dict[str, dict] = {}


class Pipeline:
    spec: PipelineSpec

    def __init__(self, plugins_manager: PluginManager):
        assert hasattr(self, 'spec'), '"spec" property is not set'
        if not self._validate_stages_uniqueness(self.spec.stages):
            raise UniqueError('Stages IDs are not unique')
        self._plugins = plugins_manager

    @property
    def plugins(self):
        return self._plugins

    async def run(self, config: PipelineConfig = PipelineConfig()):
        stages: Sequence[Stage] = []
        for s in self.spec.stages:
            dependencies = config.dependencies.get(s.name, {})
            obj = s(
                plugins_manager=self._plugins,
                **dependencies
            )
            stages.append(obj)

        ctxs = {}
        prev_ctx = None
        for stage in stages:
            force_data = config.force_context_data.get(stage.name, {})

            if not self._stage_allowed(stage, config):
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

    def _stage_allowed(self, stage: type[Stage], config: PipelineConfig):
        stage_allowed = True
        if ass := config.allowed_stages:
            stage_allowed = stage.name in ass
        elif iss := config.ignored_stages:
            stage_allowed = stage.name not in iss
        return stage_allowed


class PipelineOutput(BaseModel):
    pass

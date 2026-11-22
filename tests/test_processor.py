from src.watchdocr.processor.context import WatchdOcrRuntimeContext
from src.watchdocr.processor.processor import (
    WatchdOcrRunner,
    WatchdOcrPipeline,
    WatchdOcrProcessorStatus,
    PipelineStrategy,
    StrategyTask,
    merge_strategies
)
from src.watchdocr.plugins.translation import TranslationData
import asyncio
import pytest


class FakePipeline:
    def __init__(self, block=False):
        self.started = []
        self.block = block
        self.release = asyncio.Event()
        self.text = None  # Constant text instead of unique one per execution

    async def execute(self, ctx, strategy):
        self.started.append((strategy, ctx.config.boundings))
        if self.block:
            await self.release.wait()
        ctx.ocr.text = self.text or f'text-{len(self.started)}'


class Recorder:
    def __init__(self, runner: WatchdOcrRunner):
        self.outputs = []
        self.statuses = []
        self.previews = []
        runner.register_output_callback(self.outputs.append)
        runner.register_status_callback(self.statuses.append)
        runner.register_area_preview_callback(self.previews.append)


def create_runner(block=False):
    pipeline = FakePipeline(block)
    runner = WatchdOcrRunner(pipeline)
    recorder = Recorder(runner)
    runner.start()
    return runner, pipeline, recorder


def task(strategy: PipelineStrategy, skip_unchanged=False, **context_data):
    return StrategyTask(
        strategy=strategy,
        context_data=context_data,
        skip_unchanged=skip_unchanged
    )


async def test_pipeline_output_is_sent():
    runner, pipeline, recorder = create_runner()

    await runner.put(task(PipelineStrategy.OCR_TRANSLATION, boundings=(1, 2, 3, 4)))

    assert pipeline.started == [(PipelineStrategy.OCR_TRANSLATION, (1, 2, 3, 4))]
    assert [o.original_text for o in recorder.outputs] == ['text-1']
    assert recorder.statuses == [
        WatchdOcrProcessorStatus.RECOGNIZING,
        WatchdOcrProcessorStatus.IDLE
    ]
    assert len(recorder.previews) == 1


async def test_context_change_is_applied_without_pipeline():
    runner, pipeline, _ = create_runner()

    result = runner.put(task(PipelineStrategy.ONLY_CONTEXT_CHANGE, boundings=(1, 2, 3, 4)))

    assert result is None
    assert pipeline.started == []
    assert runner.config().boundings == (1, 2, 3, 4)


async def test_new_pipeline_cancels_running_one():
    runner, pipeline, recorder = create_runner(block=True)

    first = runner.put(task(PipelineStrategy.OCR_TRANSLATION, boundings=(1, 1, 1, 1)))
    await asyncio.sleep(0)
    second = runner.put(task(PipelineStrategy.OCR_TRANSLATION, boundings=(2, 2, 2, 2)))
    pipeline.release.set()
    await asyncio.wait((first, second))

    assert first.cancelled()
    assert pipeline.started[-1] == (PipelineStrategy.OCR_TRANSLATION, (2, 2, 2, 2))
    assert [o.original_text for o in recorder.outputs] == ['text-2']
    assert recorder.statuses == [
        WatchdOcrProcessorStatus.RECOGNIZING,
        WatchdOcrProcessorStatus.RECOGNIZING,
        WatchdOcrProcessorStatus.IDLE
    ]


async def test_cancelled_pipeline_strategy_is_merged():
    runner, pipeline, _ = create_runner(block=True)

    runner.put(task(PipelineStrategy.OCR_ONLY))
    await asyncio.sleep(0)
    second = runner.put(task(PipelineStrategy.TRANSLATION_ONLY, target_language='UK'))
    pipeline.release.set()
    await second

    assert pipeline.started[-1][0] == PipelineStrategy.OCR_TRANSLATION


async def test_stop_cancels_running_pipeline():
    runner, pipeline, recorder = create_runner()
    await runner.put(task(PipelineStrategy.OCR_TRANSLATION))

    pipeline.block = True
    running = runner.put(task(PipelineStrategy.OCR_TRANSLATION))
    await asyncio.sleep(0)
    await runner.stop()

    assert running.cancelled()
    assert not runner.is_running()
    assert recorder.statuses[-1] == WatchdOcrProcessorStatus.IDLE
    assert len(recorder.outputs) == 1
    # Context of cancelled pipeline is not applied
    assert runner.context().ocr.text == 'text-1'


async def test_put_skipped_when_runner_stopped():
    runner, pipeline, _ = create_runner()
    await runner.stop()

    result = runner.put(task(PipelineStrategy.OCR_TRANSLATION))

    assert result is None
    assert pipeline.started == []


@pytest.mark.parametrize('strategies, expected', [
    ((PipelineStrategy.OCR_ONLY, PipelineStrategy.TRANSLATION_ONLY), PipelineStrategy.OCR_TRANSLATION),
    ((PipelineStrategy.OCR_TRANSLATION, PipelineStrategy.TRANSLATION_ONLY), PipelineStrategy.OCR_TRANSLATION),
    ((PipelineStrategy.TRANSLATION_ONLY, PipelineStrategy.TRANSLATION_ONLY), PipelineStrategy.TRANSLATION_ONLY),
    ((PipelineStrategy.OCR_ONLY, PipelineStrategy.ONLY_CONTEXT_CHANGE), PipelineStrategy.OCR_ONLY),
])
def test_merge_strategies(strategies, expected):
    assert merge_strategies(*strategies) == expected


# Pipeline hooks
class FakePluginManager:
    def __init__(self):
        self.hooks = []

    async def call_hook(self, id, data, *args, **kwargs):
        self.hooks.append(id)
        return data


class FakeTranslator:
    def __init__(self):
        self.release = asyncio.Event()

    async def translate(self, text, source_lang, target_lang):
        await self.release.wait()
        return TranslationData(True, text, text)


async def test_cancelled_pipeline_skips_finish_hooks():
    plugins = FakePluginManager()
    translator = FakeTranslator()
    pipeline = WatchdOcrPipeline(plugins, ocr=None, translator=translator)
    ctx = WatchdOcrRuntimeContext()
    ctx.ocr.success = True

    execution = asyncio.create_task(pipeline.execute(ctx, PipelineStrategy.TRANSLATION_ONLY))
    await asyncio.sleep(0)
    execution.cancel()
    await asyncio.wait((execution,))

    assert plugins.hooks == ['watchdocr.processor_pipeline.start']


async def test_finished_pipeline_calls_all_hooks():
    plugins = FakePluginManager()
    translator = FakeTranslator()
    translator.release.set()
    pipeline = WatchdOcrPipeline(plugins, ocr=None, translator=translator)
    ctx = WatchdOcrRuntimeContext()
    ctx.ocr.success = True

    await pipeline.execute(ctx, PipelineStrategy.TRANSLATION_ONLY)

    assert plugins.hooks == [
        'watchdocr.processor_pipeline.start',
        'watchdocr.processor_pipeline.output_text',
        'watchdocr.processor_pipeline.finish'
    ]


# Unchanged results
async def test_unchanged_output_is_skipped():
    runner, pipeline, recorder = create_runner()
    pipeline.text = 'same'

    await runner.put(task(PipelineStrategy.OCR_TRANSLATION, skip_unchanged=True))
    await runner.put(task(PipelineStrategy.OCR_TRANSLATION, skip_unchanged=True))

    assert len(recorder.outputs) == 1
    assert len(recorder.previews) == 1
    assert recorder.statuses[-1] == WatchdOcrProcessorStatus.IDLE


async def test_unchanged_output_is_sent_without_skip_flag():
    runner, pipeline, recorder = create_runner()
    pipeline.text = 'same'

    await runner.put(task(PipelineStrategy.OCR_TRANSLATION, skip_unchanged=True))
    await runner.put(task(PipelineStrategy.OCR_TRANSLATION))

    assert len(recorder.outputs) == 2


async def test_changed_output_is_sent_with_skip_flag():
    runner, pipeline, recorder = create_runner()

    await runner.put(task(PipelineStrategy.OCR_TRANSLATION, skip_unchanged=True))
    await runner.put(task(PipelineStrategy.OCR_TRANSLATION, skip_unchanged=True))

    assert [o.original_text for o in recorder.outputs] == ['text-1', 'text-2']


# OCR stage
class FakeOcr:
    def __init__(self):
        self.calls = 0

    async def recognize(self, image, area):
        self.calls += 1
        raise AssertionError('OCR must be skipped')


async def test_ocr_stage_keeps_hook_data_when_ignored():
    from src.watchdocr.processor.processor import OcrPipelineStage

    ocr = FakeOcr()
    stage = OcrPipelineStage(FakePluginManager(), ocr)
    ctx = WatchdOcrRuntimeContext()
    ctx.ocr.ignore = True
    ctx.ocr.success = True
    ctx.ocr.text = 'from hook'

    await stage.execute(ctx)

    assert ocr.calls == 0
    assert ctx.ocr.text == 'from hook'
    assert ctx.ocr.success
    assert not ctx.ocr.ignore

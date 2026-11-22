from src.common.utils.logging import log
from src.common.utils.timing import Stopwatch
from src.common.event import EventSystem, IEvent
from src.common.plugin import PluginManager
from src.watchdocr.processor.context import WatchdOcrRuntimeContext, RuntimeConfig, OcrBox
from src.watchdocr.processor.ocr import Ocr
from src.watchdocr.processor.translator import Translator
from src.watchdocr.processor.image import ScreenGrabber
from src.watchdocr.processor.adapter import OcrTranslatorTextAdapter
from pydantic import BaseModel, ConfigDict
from enum import IntEnum, auto
from PIL import Image
from typing import Callable
import asyncio


LOG_PROCESSOR = 'Processor'


# Pipeline
class PipelineStrategy(IntEnum):
    ONLY_CONTEXT_CHANGE = auto()
    OCR_ONLY = auto()
    TRANSLATION_ONLY = auto()
    OCR_TRANSLATION = auto()


class PipelineStage:
    def __init__(self, plugin_manager: PluginManager):
        self._plugin_manager = plugin_manager

    async def execute(self, ctx: WatchdOcrRuntimeContext):
        raise NotImplementedError

    @property
    def plugin_manager(self):
        return self._plugin_manager


class ImageGrabberStage(PipelineStage):
    async def execute(self, ctx):
        log.info(
            'Starting Image Grabber Pipeline Stage...',
            extra={'title': LOG_PROCESSOR}
        )

        ctx.image = None  # Clean up

        image = await asyncio.to_thread(
            ScreenGrabber.grab_screen_area,
            ctx.config.boundings
        )
        if not image:
            log.warning(
                'Screen grabber returned no image for boundings %s',
                ctx.config.boundings,
                extra={'title': LOG_PROCESSOR}
            )
            return

        # Call image process hook
        image = await self.plugin_manager.call_hook(
            id='watchdocr.image_grabber_pipeline.image_process',
            data=image,
            ctx=ctx
        )
        ctx.image = image  # Store image

        log.info(
            'Screen grabbed successfully (%dx%d). Running recognition...',
            image.width, image.height,
            extra={'title': LOG_PROCESSOR}
        )


class OcrPipelineStage(PipelineStage):
    def __init__(self, plugin_manager, ocr: Ocr):
        super().__init__(plugin_manager)
        self._ocr = ocr

    async def execute(self, ctx):
        log.info(
            'Starting OCR Pipeline Stage...',
            extra={'title': LOG_PROCESSOR}
        )

        # Skip OCR pipeline if ignore flag is set (created for hooks).
        # Checked before clean up, so data provided by hooks is kept
        if ctx.ocr.ignore:
            ctx.ocr.ignore = False
            return

        ctx.ocr.clear()  # Clean up

        data = await self._ocr.recognize(ctx.image, ctx.config.boundings)
        ctx.ocr.success = data.success

        if not data.success:
            return

        ctx.ocr.text = data.text
        ctx.ocr.total_confidence = data.confidence

        ctx.ocr.boxes = tuple(OcrBox(
            coordinates=b.coordinates,
            confidence=b.confidence,
        ) for b in data.boxes)
        ctx.ocr.parts = tuple(p.text for p in data.boxes)


class TranslationPipelineStage(PipelineStage):
    def __init__(self, plugin_manager, translator: Translator):
        super().__init__(plugin_manager)
        self._translator = translator

    async def execute(self, ctx):
        ctx.translation.clear()  # Clean up

        # Skip if OCR pipeline if failed
        if not ctx.ocr.success:
            return

        text_adapter = OcrTranslatorTextAdapter()
        mapped_text = text_adapter.generate_mapped_string(
            full_text=ctx.ocr.text,
            parts=ctx.ocr.parts
        )

        data = await self._translator.translate(
            text=mapped_text,
            source_lang=ctx.config.source_language,
            target_lang=ctx.config.target_language
        )

        ctx.translation.success = data.success
        if not data.success:
            log.error(
                'Translation failed (%s). Reusing original text.',
                data.translated_text,
                extra={'title': LOG_PROCESSOR}
            )

            ctx.translation.text = data.translated_text
            return

        # Generate translated boxes from output
        full_text, parts = text_adapter.unpack_mapped_string(data.translated_text)

        ctx.translation.text = full_text
        ctx.translation.parts = tuple(p for _, p in zip(ctx.ocr.parts, parts))


STRATEGY_STAGES: dict[PipelineStrategy, frozenset[str]] = {
    PipelineStrategy.ONLY_CONTEXT_CHANGE: frozenset(),
    PipelineStrategy.OCR_ONLY: frozenset({'image_grabber', 'ocr'}),
    PipelineStrategy.TRANSLATION_ONLY: frozenset({'translation'}),
    PipelineStrategy.OCR_TRANSLATION: frozenset({'image_grabber', 'ocr', 'translation'}),
}


def merge_strategies(*strategies: PipelineStrategy):
    stages = frozenset().union(*(STRATEGY_STAGES[s] for s in strategies))
    for strategy, strategy_stages in STRATEGY_STAGES.items():
        if strategy_stages == stages:
            return strategy
    raise ValueError(f'No strategy found for stages -> {stages}')


class WatchdOcrPipeline:
    def __init__(
        self,
        plugin_manager: PluginManager,
        ocr: Ocr,
        translator: Translator
    ):
        self._plugin_manager = plugin_manager
        self._stages: dict[str, PipelineStage] = {
            'image_grabber': ImageGrabberStage(plugin_manager),
            'ocr': OcrPipelineStage(plugin_manager, ocr),
            'translation': TranslationPipelineStage(plugin_manager, translator)
        }

    async def execute(
        self,
        ctx: WatchdOcrRuntimeContext,
        strategy: PipelineStrategy
    ):
        stopwatch = Stopwatch()

        # Call pipeline start hook
        with stopwatch.measure('start_hook'):
            await self._plugin_manager.call_hook(
                id='watchdocr.processor_pipeline.start',
                data=ctx,
            )

        active = STRATEGY_STAGES[strategy]
        for name, stage in self._stages.items():
            if name in active:
                with stopwatch.measure(name):
                    await stage.execute(ctx)

        # Call text output hook
        with stopwatch.measure('output_text_hook'):
            ctx.translation.text = await self._plugin_manager.call_hook(
                id='watchdocr.processor_pipeline.output_text',
                data=ctx.translation.text
            )

        # Call pipeline finish hook
        with stopwatch.measure('finish_hook'):
            await self._plugin_manager.call_hook(
                id='watchdocr.processor_pipeline.finish',
                data=ctx,
            )

        log.debug(
            'Pipeline %s timings: %s',
            strategy.name, stopwatch.summary(),
            extra={'title': LOG_PROCESSOR}
        )


# Output
class WatchdOcrOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    strategy: PipelineStrategy
    original_text: str
    translated_text: str
    boxes: tuple[OcrBox, ...]
    original_parts: tuple[str, ...]
    translated_parts: tuple[str, ...]
    total_confidence: float


# Processor
class WatchdOcrProcessorStatus(IntEnum):
    IDLE = 0
    RECOGNIZING = 1


class WatchdOcrRunner:
    def __init__(self, pipeline: WatchdOcrPipeline):
        self._ctx = WatchdOcrRuntimeContext()  # Context of last finished pipeline
        self._config = RuntimeConfig()  # Actual config for the next pipelines
        self._pipeline = pipeline
        self._task: asyncio.Task | None = None
        self._strategy: PipelineStrategy | None = None
        self._last_output: WatchdOcrOutput | None = None
        self._running = False
        self._output_callback = None
        self._status_callback = None
        self._area_preview_callback = None

    def put(self, task: 'StrategyTask'):
        log.debug(
            'Queueing strategy: %s', task.strategy.name,
            extra={'title': LOG_PROCESSOR}
        )

        # Context changes are applied immediately, running
        # pipeline works with config snapshot
        for key, value in task.context_data.items():
            setattr(self._config, key, value)

        if task.strategy == PipelineStrategy.ONLY_CONTEXT_CHANGE:
            return None

        if not self._running:
            log.warning(
                'WatchdOcrRunner is not running. Skipping strategy: %s',
                task.strategy.name,
                extra={'title': LOG_PROCESSOR}
            )
            return None

        # Latest wins: cancel current pipeline and restart it with merged
        # strategy, so changes requested by both of them are applied
        strategy = task.strategy
        if self._task and not self._task.done():
            strategy = merge_strategies(self._strategy, strategy)
            log.debug(
                'Cancelling current pipeline, restarting with strategy: %s',
                strategy.name,
                extra={'title': LOG_PROCESSOR}
            )
            self._task.cancel()

        self._strategy = strategy
        self._task = asyncio.create_task(self._execute(strategy, task.skip_unchanged))
        return self._task

    def start(self):
        log.info(
            'Starting WatchdOcrRunner...',
            extra={'title': LOG_PROCESSOR}
        )
        self._running = True

    async def stop(self):
        log.info(
            'Stopping WatchdOcrRunner...',
            extra={'title': LOG_PROCESSOR}
        )
        self._running = False
        task, self._task = self._task, None
        if task and not task.done():
            task.cancel()
            await asyncio.wait((task,))
        log.info(
            'WatchdOcrRunner stopped.',
            extra={'title': LOG_PROCESSOR}
        )

    def is_running(self):
        return self._running

    async def _execute(self, strategy: PipelineStrategy, skip_unchanged: bool):
        ctx = self._create_context()

        self._send_status(WatchdOcrProcessorStatus.RECOGNIZING)
        try:
            await self._pipeline.execute(ctx, strategy)
        except asyncio.CancelledError:
            log.debug(
                'Pipeline with strategy %s cancelled.', strategy.name,
                extra={'title': LOG_PROCESSOR}
            )
            raise
        except Exception:
            log.exception(
                'Pipeline with strategy %s failed.', strategy.name,
                extra={'title': LOG_PROCESSOR}
            )
            return
        finally:
            # Don't reset status if pipeline was replaced by a new one
            if self._task in (None, asyncio.current_task()):
                self._send_status(WatchdOcrProcessorStatus.IDLE)

        self._ctx = ctx

        output = self.create_output_data(strategy)

        # Nothing to update in UI if result is the same
        if skip_unchanged and output == self._last_output:
            log.debug(
                'Pipeline result is unchanged, skipping output.',
                extra={'title': LOG_PROCESSOR}
            )
            return
        self._last_output = output

        if self._output_callback:
            self._output_callback(output)

        if strategy in (PipelineStrategy.OCR_ONLY,
                        PipelineStrategy.OCR_TRANSLATION):
            self._send_area_preview(ctx.image)

    def _create_context(self):
        # Image is shared with the previous context,
        # pipeline stages are only replacing it
        return WatchdOcrRuntimeContext(
            config=self._config.model_copy(),
            ocr=self._ctx.ocr.model_copy(deep=True),
            translation=self._ctx.translation.model_copy(deep=True),
            image=self._ctx.image
        )

    def clean_current_pipelines(self):
        if self._task and not self._task.done():
            self._task.cancel()

    def create_output_data(self, strategy: PipelineStrategy):
        return WatchdOcrOutput(
            strategy=strategy,
            original_text=self._ctx.ocr.text,
            translated_text=self._ctx.translation.text,
            boxes=self._ctx.ocr.boxes,
            original_parts=self._ctx.ocr.parts,
            translated_parts=self._ctx.translation.parts,
            total_confidence=self._ctx.ocr.total_confidence
        )

    def context(self):
        return self._ctx.model_copy(deep=True)

    def config(self):
        return self._config.model_copy()

    def register_output_callback(self, cb: Callable[[WatchdOcrOutput], None]):
        self._output_callback = cb

    def register_status_callback(self, cb: Callable[[WatchdOcrProcessorStatus], None]):
        self._status_callback = cb

    def register_area_preview_callback(self, cb: Callable[[Image.Image], None]):
        self._area_preview_callback = cb

    def _send_status(self, status: WatchdOcrProcessorStatus):
        if self._status_callback:
            self._status_callback(status)

    def _send_area_preview(self, image: Image.Image):
        if self._area_preview_callback:
            self._area_preview_callback(image)


class StrategyTask(BaseModel):
    model_config = ConfigDict(frozen=True)

    strategy: PipelineStrategy
    context_data: dict
    skip_unchanged: bool = False  # Don't send output equal to the previous one


class WatchdOcrProcessor:
    def __init__(
        self,
        plugins_manager: PluginManager,
        event_system: EventSystem
    ):
        self._eventsys = event_system
        self._ocr = Ocr(plugins_manager)
        self._translator = Translator(plugins_manager)
        self._pipeline = WatchdOcrPipeline(
            plugin_manager=plugins_manager,
            ocr=self._ocr,
            translator=self._translator
        )
        self._runner = WatchdOcrRunner(self._pipeline)
        self._runner.register_output_callback(self._on_output)
        self._runner.register_status_callback(self._on_status)
        self._runner.register_area_preview_callback(self._on_area_preview)

    def run(self):
        log.info(
            'Starting WatchdOcrProcessor...',
            extra={'title': LOG_PROCESSOR}
        )
        self._runner.start()

    async def stop(self):
        log.info(
            'Stopping WatchdOcrProcessor...',
            extra={'title': LOG_PROCESSOR}
        )
        await self._runner.stop()

    def get_active(self):
        return self._runner.is_running()

    def queue_pipeline(
        self,
        strategy: PipelineStrategy,
        context_data: dict,
        skip_unchanged: bool = False
    ):
        log.info(
            'Queueing pipeline execution with strategy: %s',
            strategy.name,
            extra={'title': LOG_PROCESSOR}
        )

        task = StrategyTask(
            strategy=strategy,
            context_data=context_data,
            skip_unchanged=skip_unchanged
        )
        return self._runner.put(task)

    def context(self):
        return self._runner.context()

    def config(self):
        return self._runner.config()

    def _on_output(self, data: WatchdOcrOutput):
        self._eventsys.dispatch(
            event=Events.PROCESSOR_RESULT_RECEIVED,
            data={'data': data.model_dump()}
        )

    def _on_status(self, status: WatchdOcrProcessorStatus):
        self._eventsys.dispatch(
            event=Events.PROCESSOR_STATUS_CHANGED,
            data={'status': status}
        )

    def _on_area_preview(self, image: Image.Image):
        self._eventsys.dispatch(
            event=Events.PROCESSOR_AREA_IMAGE_CHANGED,
            data={'image': image}
        )

    def clean_current_pipelines(self):
        log.info(
            'Cancelling current runner pipeline...',
            extra={'title': LOG_PROCESSOR}
        )
        self._runner.clean_current_pipelines()


# Events
class ProcessorActiveChanged(IEvent):
    active: bool


class ProcessorResultReceivedEvent(IEvent):
    data: dict


class ProcessorStateChangeEvent(IEvent):
    status: WatchdOcrProcessorStatus


class ProcessorAreaImageChangeEvent(IEvent):
    image: Image.Image


class Events:
    PROCESSOR_ACTIVE_CHANGED = ProcessorActiveChanged
    PROCESSOR_RESULT_RECEIVED = ProcessorResultReceivedEvent
    PROCESSOR_STATUS_CHANGED = ProcessorStateChangeEvent
    PROCESSOR_AREA_IMAGE_CHANGED = ProcessorAreaImageChangeEvent

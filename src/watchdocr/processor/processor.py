from src.common.utils.logging import log
from src.common.event import EventSystem, IEvent
from src.common.plugin import PluginManager
from src.watchdocr.processor.context import WatchdOcrRuntimeContext, OcrBox
from src.watchdocr.processor.ocr import Ocr
from src.watchdocr.processor.translator import Translator
from src.watchdocr.processor.image import ScreenGrabber
from src.watchdocr.processor.adapter import OcrTranslatorTextAdapter
from pydantic import BaseModel, ConfigDict
from enum import IntEnum, auto
from threading import Thread, Event
from PIL import Image
from typing import Callable
import queue


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
        self._enabled = True

    def set_enabled(self, enable: bool):
        self._enabled = enable

    def enabled(self):
        return self._enabled

    def execute(self, ctx: WatchdOcrRuntimeContext):
        raise NotImplementedError

    @property
    def plugin_manager(self):
        return self._plugin_manager


class ImageGrabberStage(PipelineStage):
    def execute(self, ctx):
        log.info(
            'Starting Image Grabber Pipeline Stage...',
            extra={'title': LOG_PROCESSOR}
        )

        ctx.image = None  # Clean up

        image = ScreenGrabber.grab_screen_area(ctx.config.boundings)
        if not image:
            log.warning(
                'Screen grabber returned no image for boundings %s',
                ctx.config.boundings,
                extra={'title': LOG_PROCESSOR}
            )
            return

        # Call image process hook
        image = self.plugin_manager.call_hook(
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

    def execute(self, ctx):
        log.info(
            'Starting OCR Pipeline Stage...',
            extra={'title': LOG_PROCESSOR}
        )

        ctx.ocr.clear()  # Clean up

        # Skip OCR pipeline if ignore flag is set (created for hooks)
        if ctx.ocr.ignore:
            ctx.ocr.ignore = False
            return

        data = self._ocr.recognize(ctx.image)
        ctx.ocr.success = data.success

        if not data.success:
            return

        ctx.ocr.text = data.text
        ctx.ocr.total_confidence = data.confidence

        ctx.ocr.boxes = tuple(OcrBox(
            boundings=b.boundings,
            confidence=b.confidence
        ) for b in data.boxes)
        ctx.ocr.parts = [p.text for p in data.boxes]


class TranslationPipelineStage(PipelineStage):
    def __init__(self, plugin_manager, translator: Translator):
        super().__init__(plugin_manager)
        self._translator = translator

    def execute(self, ctx):
        ctx.translation.clear()  # Clean up

        # Skip if OCR pipeline if failed
        if not ctx.ocr.success:
            return

        text_adapter = OcrTranslatorTextAdapter()
        mapped_text = text_adapter.generate_mapped_string(
            full_text=ctx.ocr.text,
            parts=ctx.ocr.parts
        )

        data = self._translator.translate(
            text=mapped_text,
            source_lang=ctx.config.source_language,
            target_lang=ctx.config.target_language
        )

        ctx.translation.success = data.success
        if not data.success:
            log.error(
                'Translation failed. Reusing original text.',
                extra={'title': LOG_PROCESSOR}
            )

            ctx.translation.text = data.translated_text
            return

        # Generate translated boxes from output
        full_text, parts = text_adapter.unpack_mapped_string(data.translated_text)

        ctx.translation.text = full_text
        ctx.translation.parts = [p for _, p in zip(ctx.ocr.parts, parts)]


STRATEGY_STAGES: dict[PipelineStrategy, frozenset[str]] = {
    PipelineStrategy.ONLY_CONTEXT_CHANGE: frozenset(),
    PipelineStrategy.OCR_ONLY: frozenset({'image_grabber', 'ocr'}),
    PipelineStrategy.TRANSLATION_ONLY: frozenset({'translation'}),
    PipelineStrategy.OCR_TRANSLATION: frozenset({'image_grabber', 'ocr', 'translation'}),
}


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
        self._strategy = PipelineStrategy.OCR_TRANSLATION

    def execute(
        self,
        ctx: WatchdOcrRuntimeContext,
        strategy: PipelineStrategy
    ):
        # Call pipeline start hook
        self._plugin_manager.call_hook(
            id='watchdocr.processor_pipeline.start',
            data=ctx,
        )

        self._apply_strategy(strategy)

        for stage in self._stages.values():
            if stage.enabled():
                stage.execute(ctx)

        # Call text output hook
        ctx.translation.text = self._plugin_manager.call_hook(
            id='watchdocr.processor_pipeline.output_text',
            data=ctx.translation.text
        )

        # Call pipeline finish hook
        self._plugin_manager.call_hook(
            id='watchdocr.processor_pipeline.finish',
            data=ctx,
        )

    def current_strategy(self):
        return self._strategy

    def _apply_strategy(self, strategy):
        active = STRATEGY_STAGES[strategy]
        for name, stage in self._stages.items():
            stage.set_enabled(name in active)
        self._strategy = strategy


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
    _Sentinel = object()

    def __init__(self, pipeline: WatchdOcrPipeline):
        self._ctx = WatchdOcrRuntimeContext()
        self._pipeline = pipeline
        self._q = queue.Queue()
        self._th = None
        self._running = False
        self._output_callback = None
        self._status_callback = None
        self._area_preview_callback = None
        self._e = Event()
        self._e.set()

    def put(self, task: 'StrategyTask'):
        log.debug(
            'Queueing strategy: %s', task.strategy.name,
            extra={'title': LOG_PROCESSOR}
        )
        self._q.put(task)

    def start(self):
        log.info(
            'Starting WatchdOcrRunner background thread...',
            extra={'title': LOG_PROCESSOR}
        )
        self._running = True
        self._th = Thread(target=self._run, daemon=True)
        self._th.start()

    def stop(self):
        log.info(
            'Stopping WatchdOcrRunner background thread...',
            extra={'title': LOG_PROCESSOR}
        )
        self._running = False
        self._q.put(self._Sentinel)
        if self._th and self._th.is_alive():
            self._th.join()
        self._q.queue.clear()
        log.info(
            'WatchdOcrRunner background thread stopped.',
            extra={'title': LOG_PROCESSOR}
        )

    def is_running(self):
        return self._running

    def _run(self):
        while self._running:
            task: StrategyTask = self._q.get()

            if task is self._Sentinel:
                break

            self._ctx.update_config(task.context_data)

            if task.strategy != PipelineStrategy.ONLY_CONTEXT_CHANGE:
                self._send_status(WatchdOcrProcessorStatus.RECOGNIZING)
                self._e.clear()
                self._pipeline.execute(self._ctx, task.strategy)
                self._send_status(WatchdOcrProcessorStatus.IDLE)

                output = self.create_output_data()
                if self._output_callback:
                    self._output_callback(output)

                self._send_area_preview(self._ctx.image)
                self._e.set()

    def wait_for_exec_finish(self):
        self._e.wait()

    def clean_current_pipelines(self):
        self._q.queue.clear()

    def create_output_data(self):
        return WatchdOcrOutput(
            strategy=self._pipeline.current_strategy(),
            original_text=self._ctx.ocr.text,
            translated_text=self._ctx.translation.text,
            boxes=self._ctx.ocr.boxes,
            original_parts=self._ctx.ocr.parts,
            translated_parts=self._ctx.translation.parts,
            total_confidence=self._ctx.ocr.total_confidence
        )

    def context(self):
        return self._ctx.model_copy(deep=True)

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
        if self._area_preview_callback and self._ctx.image is not None:
            self._area_preview_callback(image)


class StrategyTask(BaseModel):
    model_config = ConfigDict(frozen=True)

    strategy: PipelineStrategy
    context_data: dict


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

    def stop(self):
        log.info(
            'Stopping WatchdOcrProcessor...',
            extra={'title': LOG_PROCESSOR}
        )
        self._runner.stop()

    def get_active(self):
        return self._runner.is_running()

    def queue_pipeline(self, strategy: PipelineStrategy, context_data: dict):
        log.info(
            'Queueing pipeline execution with strategy: %s',
            strategy.name,
            extra={'title': LOG_PROCESSOR}
        )

        task = StrategyTask(strategy=strategy, context_data=context_data)
        self._runner.put(task)

    def context(self):
        return self._runner.context()

    def wait_for_pipeline_finish(self):
        return self._runner.wait_for_exec_finish()

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
            'Cleaning current runner pipelines queue...',
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

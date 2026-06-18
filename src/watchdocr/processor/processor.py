from src.common.utils.logging import log
from src.common.event import EventSystem, IEvent
from src.common.plugin import PluginManager
from src.watchdocr.processor.ocr import Ocr
from src.watchdocr.processor.translator import Translator
from src.watchdocr.processor.image import grab_window_area
from src.watchdocr.processor.text import cleanup_text_simple
from dataclasses import dataclass, asdict, fields
from enum import IntEnum, auto
from threading import Thread
from PIL import Image
from typing import Callable
import queue


BOXED_TEXT_SEPARATOR1 = ' ⟦$⟧ '
BOXED_TEXT_SEPARATOR2 = '⟦$⟧'


@dataclass(slots=True)
class WatchdOcrRuntimeContext:
    boundings: tuple = (0, 0, 0, 0)
    image: Image.Image | None = None
    text: str = ''
    translated_text: str = ''
    source_language: str = ''
    target_language: str = ''
    boxes: tuple = tuple()
    confidence: float = 0.
    boxed_text: str = ''
    translated_boxes: tuple = tuple()


class PipelineStrategy(IntEnum):
    ONLY_CONTEXT_CHANGE = auto()
    OCR_ONLY = auto()
    TRANSLATION_ONLY = auto()
    OCR_TRANSLATION = auto()


@dataclass(slots=True)
class WatchdOcrOutput:
    strategy: PipelineStrategy
    text: str
    translated_text: str
    boxes: tuple
    confidence: float

    def to_dict(self):
        return asdict(self)


class PipelineStage:
    def __init__(self):
        self._enabled = True

    def set_enabled(self, enable: bool):
        self._enabled = enable

    def enabled(self):
        return self._enabled

    def execute(self, ctx: WatchdOcrRuntimeContext):
        raise NotImplementedError


class OcrPipelineStage(PipelineStage):
    def __init__(self, ocr: Ocr):
        super().__init__()
        self._ocr = ocr

    def execute(self, ctx):
        image = grab_window_area(ctx.boundings)
        ctx.image = image

        data = self._ocr.recognize(ctx.image)
        ctx.text = data.text
        ctx.translated_text = data.text
        ctx.confidence = data.confidence
        ctx.boxes = data.boxes
        ctx.boxed_text = BOXED_TEXT_SEPARATOR1.join(b[0] for b in data.boxes)
        ctx.translated_boxes = data.boxes


class TranslationPipelineStage(PipelineStage):
    def __init__(self, translator: Translator):
        super().__init__()
        self._translator = translator

    def execute(self, ctx):
        data = self._translator.translate(
            ctx.boxed_text,
            ctx.source_language,
            ctx.target_language
        )

        if not data.success:
            ctx.translated_text = data.translated_text
            ctx.translated_boxes = tuple()
            return

        if data.translated_text == '':
            texts = []
        else:
            texts = data.translated_text.split(BOXED_TEXT_SEPARATOR2)
        ctx.translated_text = cleanup_text_simple(' '.join(texts))

        boxes = []
        for i, (_, t) in enumerate(zip(ctx.boxes, texts)):
            boxes.append((t, ctx.boxes[i][1], ctx.boxes[i][2]))
        ctx.translated_boxes = tuple(boxes)


class WatchdOcrPipeline:
    def __init__(
        self,
        ctx: WatchdOcrRuntimeContext,
        ocr: Ocr,
        translator: Translator
    ):
        self._ctx = ctx
        self._stages: dict[str, PipelineStage] = {
            'ocr': OcrPipelineStage(ocr),
            'translation': TranslationPipelineStage(translator)
        }
        self._strategy = PipelineStrategy.OCR_TRANSLATION

    def provide_strategy(self, strategy: PipelineStrategy):
        match strategy:
            case PipelineStrategy.ONLY_CONTEXT_CHANGE:
                self._stages['ocr'].set_enabled(False)
                self._stages['translation'].set_enabled(False)
            case PipelineStrategy.OCR_ONLY:
                self._stages['ocr'].set_enabled(True)
                self._stages['translation'].set_enabled(False)
            case PipelineStrategy.TRANSLATION_ONLY:
                self._stages['ocr'].set_enabled(False)
                self._stages['translation'].set_enabled(True)
            case PipelineStrategy.OCR_TRANSLATION:
                self._stages['ocr'].set_enabled(True)
                self._stages['translation'].set_enabled(True)
        self._strategy = strategy

    def execute(self):
        for stage in self._stages.values():
            if stage.enabled():
                stage.execute(self._ctx)

    def current_strategy(self):
        return self._strategy


class WatchdOcrProcessorStatus(IntEnum):
    IDLE = 0
    RECOGNIZING = 1


class WatchdOcrRunner:
    def __init__(
        self,
        ctx: WatchdOcrRuntimeContext,
        pipeline: WatchdOcrPipeline
    ):
        self._ctx = ctx
        self._pipeline = pipeline
        self._q = queue.Queue()
        self._th = None
        self._running = False
        self._output_callback = None
        self._status_callback = None
        self._area_preview_callback = None

    def put(self, strategy: PipelineStrategy):
        self._q.put(strategy)

    def start(self):
        self._running = True
        self._th = Thread(target=self._run, daemon=True)
        self._th.start()

    def stop(self):
        self._running = False
        if self._th and self._th.is_alive():
            self._th.join()

    def is_running(self):
        return self._running

    def _run(self):
        while self._running:
            strategy: PipelineStrategy = self._q.get()
            self._pipeline.provide_strategy(strategy)

            if strategy != PipelineStrategy.ONLY_CONTEXT_CHANGE:
                self._send_status(WatchdOcrProcessorStatus.RECOGNIZING)
                self._pipeline.execute()
                self._send_status(WatchdOcrProcessorStatus.IDLE)

                output = self.create_output_data()
                if self._output_callback:
                    self._output_callback(output)

                self._send_area_preview(self._ctx.image)

    def create_output_data(self):
        return WatchdOcrOutput(
            strategy=self._pipeline.current_strategy(),
            text=self._ctx.text,
            translated_text=self._ctx.translated_text,
            boxes=self._ctx.translated_boxes,
            confidence=self._ctx.confidence
        )

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


class WatchdOcrProcessor:
    def __init__(
        self,
        plugins_manager: PluginManager,
        event_system: EventSystem
    ):
        self._eventsys = event_system
        self._ctx = WatchdOcrRuntimeContext()
        self._ocr = Ocr(plugins_manager)
        self._translator = Translator(plugins_manager)
        self._pipeline = WatchdOcrPipeline(self._ctx, self._ocr, self._translator)
        self._runner = WatchdOcrRunner(self._ctx, self._pipeline)
        self._runner.register_output_callback(self._on_output)
        self._runner.register_status_callback(self._on_status)
        self._runner.register_area_preview_callback(self._on_area_preview)

    def run(self):
        self._runner.start()

    def stop(self):
        self._runner.stop()

    def get_active(self):
        return self._runner.is_running()

    def queue_pipeline(self, strategy: PipelineStrategy, context_data: dict):
        self._update_context_data(context_data)
        self._runner.put(strategy)

    def context(self):
        return self._ctx

    def _update_context_data(self, data: dict):
        field_names = {f.name for f in fields(self._ctx)}
        for key, value in data.items():
            if key in field_names:
                setattr(self._ctx, key, value)
            else:
                log.warning('Invalid context field provided (%s). Ignore', key)

    def _on_output(self, data: WatchdOcrOutput):
        self._eventsys.dispatch(
            event=Events.PROCESSOR_RESULT_RECEIVED,
            data={'data': data.to_dict()}
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

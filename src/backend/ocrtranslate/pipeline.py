from src.backend.core.pipeline import (Pipeline,
                                       PipelineSpec,
                                       PipelineOutput,
                                       Stage,
                                       StageContext)
from src.backend.ocrtranslate.ocr import Ocr, OcrBox
from src.backend.ocrtranslate.translator import Translator
from src.backend.ocrtranslate.image import ScreenGrabber
from src.backend.ocrtranslate.adapter import OcrTranslatorTextAdapter
from PIL import Image


class ImageCaptureContext(StageContext):
    box: tuple[int, int, int, int] = (0, 0, 0, 0)
    image: Image.Image | None = None


class ImageCaptureStage(Stage):
    name = 'image_capture'
    context_model = ImageCaptureContext

    async def runnable(self, ctx: ImageCaptureContext, prev_ctx=None):
        image = ScreenGrabber.grab_screen_area(ctx.box)

        # Call image process hook
        image = self.plugins.call_hook(
            id='watchdocr.image_grabber_pipeline.image_process',
            data=image,
            ctx=ctx
        )

        ctx = ctx.model_copy(update={
            'image': image
        })
        return ctx


class OcrContext(StageContext):
    success: bool = False
    ignore: bool = False
    text: str = ''
    total_confidence: float = 0.
    boxes: tuple[OcrBox, ...] = tuple()
    parts: tuple[str, ...] = tuple()


class OcrStage(Stage):
    name = 'ocr'
    context_model = OcrContext

    async def runnable(
        self,
        ctx: OcrContext,
        prev_ctx: ImageCaptureContext = None
    ):
        # Skip OCR pipeline if ignore flag is set (created for hooks)
        if ctx.ignore:
            ctx.ignore = False
            return ctx

        ocr: Ocr = self.deps.ocr
        image = prev_ctx.image
        response = ocr.recognize(image)

        ctx.success = response.success
        if not response.success:
            return ctx

        ctx = ctx.model_copy(update={
            'text': response.text,
            'total_confidence': response.confidence,
            'boxes': tuple(OcrBox(
                coordinates=b.coordinates,
                confidence=b.confidence,
            ) for b in response.boxes),
            'parts': tuple(p.text for p in response.boxes)
        })

        return ctx


class TranslationContext(StageContext):
    success: bool = False

    source_language: str = ''
    target_language: str = ''

    translated_text: str = ''
    parts: tuple[str, ...] = ()


class TranslationStage(Stage):
    name = 'translation'
    context_model = TranslationContext

    async def runnable(
        self,
        ctx: TranslationContext,
        prev_ctx: OcrContext = None
    ):
        # Skip if OCR pipeline if failed
        if not prev_ctx.success:
            return

        translator: Translator = self.deps.translator

        text_adapter = OcrTranslatorTextAdapter()
        mapped_text = text_adapter.generate_mapped_string(
            full_text=prev_ctx.text,
            parts=prev_ctx.parts
        )

        response = translator.translate(
            text=mapped_text,
            source_lang=ctx.source_language,
            target_lang=ctx.target_language
        )

        ctx.success = response.success
        if not response.success:
            ctx.translated_text = response.translated_text
            return

        # Generate translated boxes from output
        full_text, parts = text_adapter.unpack_mapped_string(response.translated_text)

        ctx.translated_text = full_text
        ctx.parts = tuple(p for _, p in zip(prev_ctx.parts, parts))


class TranslationOutput(PipelineOutput):
    original_text: str = ''
    translated_text: str = ''
    boxes: tuple[OcrBox, ...] = tuple()
    original_parts = tuple[str, ...] = tuple()
    translated_parts = tuple[str, ...] = tuple()
    total_confidence: float = 0.


class OcrTranslationPipeline(Pipeline):
    spec = PipelineSpec(
        stages=[ImageCaptureContext, OcrStage, TranslationStage],
        output_model=TranslationOutput
    )

    async def handle_output(self, ctxs, output):
        output = output.model_copy(update={
            'original_text': ctxs['ocr'].text,
            'translated_text': ctxs['translation'].translated_text,
            'boxes': ctxs['ocr'].boxes,
            'original_parts': ctxs['ocr'].parts,
            'translated_parts': ctxs['translation'].parts,
            'total_confidence': ctxs['ocr'].total_confidence
        })
        return output

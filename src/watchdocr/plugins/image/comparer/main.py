from src.common.plugin import HookPlugin, hook, LaunchPlugin
from src.common.utils.logging import log
from src.watchdocr.processor.processor import WatchdOcrRuntimeContext
from PIL import Image
import imagehash


__plugin_meta__ = {
    'id': 'watchdocr-image-comparer',
    'name': 'ImageComparer',
    'version': (0, 1, 0)
}
__plugin_main__ = 'ImageComparerPlugin'


IMAGE_DIFF_TOLERANCE = 5
HASH_SIZE = 32
LOG_TITLE = f'{__plugin_meta__["name"]} Plugin'


class ImageComparerPlugin(LaunchPlugin, HookPlugin):

    async def on_startup(self):
        self._image_cache = None
        self._pending_image = None
        self._ocr_cache = None

    @hook('watchdocr.image_grabber_pipeline.image_process')
    def on_image_grabber_image(
        self,
        image: Image.Image,
        ctx: WatchdOcrRuntimeContext
    ):
        # Hash is cached only after pipeline finish,
        # cancelled pipelines must not affect it
        image_hash = imagehash.average_hash(image, HASH_SIZE)
        boundings = ctx.config.boundings
        self._pending_image = (image_hash, boundings)

        if self._image_cache is None:
            return image

        cached_hash, cached_boundings = self._image_cache

        # Similar content of another area is not the same image
        if cached_boundings != boundings:
            return image

        diff = cached_hash - image_hash

        # Return cached data if images are similar
        if diff <= IMAGE_DIFF_TOLERANCE and self._ocr_cache:
            log.info(
                'Similar images detected (tolerance <= %s), run pipeline optimization',
                IMAGE_DIFF_TOLERANCE,
                extra={'title': LOG_TITLE}
            )
            self._update_context(ctx)

        return image

    @hook('watchdocr.processor_pipeline.finish')
    def on_processor_pipeline_finish(self, ctx: WatchdOcrRuntimeContext):
        if self._pending_image is not None:
            self._image_cache = self._pending_image
            self._pending_image = None

        # Cache only OCR data, copying the whole context (with image) is expensive
        self._ocr_cache = ctx.ocr.model_copy(deep=True)
        return ctx

    def _update_context(self, ctx: WatchdOcrRuntimeContext):
        ctx.ocr.ignore = True
        ctx.ocr.success = self._ocr_cache.success
        ctx.ocr.text = self._ocr_cache.text
        ctx.ocr.total_confidence = self._ocr_cache.total_confidence
        ctx.ocr.boxes = self._ocr_cache.boxes
        ctx.ocr.parts = self._ocr_cache.parts

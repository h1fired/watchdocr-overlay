from src.common.plugin import HookPlugin, hook, LaunchPlugin
from src.common.utils.logging import log
from src.watchdocr.processor.processor import WatchdOcrRuntimeContext
from PIL import Image
import imagehash
import copy


__plugin_meta__ = {
    'id': 'watchdocr-image-comparer',
    'name': 'ImageComparer',
    'version': (0, 1, 0)
}
__plugin_main__ = 'ImageComparerPlugin'


IMAGE_DIFF_TOLERANCE = 1
HASH_SIZE = 32
LOG_TITLE = f'{__plugin_meta__["name"]} Plugin'


class ImageComparerPlugin(LaunchPlugin, HookPlugin):

    def on_startup(self):
        self._image_hash_cache = None
        self._ctx_cache = None

    @hook('watchdocr.image_grabber_pipeline.image_process')
    def on_image_grabber_image(
        self,
        image: Image.Image,
        ctx: WatchdOcrRuntimeContext
    ):
        if self._image_hash_cache is None:
            self._image_hash_cache = imagehash.average_hash(image, HASH_SIZE)
            return image

        hash1 = self._image_hash_cache
        hash2 = imagehash.average_hash(image, HASH_SIZE)
        diff = hash1 - hash2

        # Cache image
        self._image_hash_cache = imagehash.average_hash(image, HASH_SIZE)

        # Return cached data if images are similar
        if diff <= IMAGE_DIFF_TOLERANCE and self._ctx_cache:
            log.info(
                'Similar images detected (tolerance <= %s), run pipeline optimization',
                IMAGE_DIFF_TOLERANCE,
                extra={'title': LOG_TITLE}
            )

            ctx.ocr.ignore = True
            ctx.ocr.success = self._ctx_cache.ocr.success
            ctx.ocr.text = self._ctx_cache.ocr.text
            ctx.ocr.confidence = self._ctx_cache.ocr.confidence
            ctx.ocr.boxes = self._ctx_cache.ocr.boxes

        return image

    @hook('watchdocr.processor_pipeline.finish')
    def on_processor_pipeline_finish(self, ctx: WatchdOcrRuntimeContext):
        self._ctx_cache = copy.deepcopy(ctx)
        return ctx

from src.watchdocr.processor.context import WatchdOcrRuntimeContext
from src.watchdocr.plugins.image.comparer.main import ImageComparerPlugin
from PIL import Image


def create_image(black_width: int):
    image = Image.new('RGB', (64, 64), 'white')
    image.paste((0, 0, 0), (0, 0, black_width, 64))
    return image


async def test_cancelled_pipeline_does_not_update_image_hash():
    plugin = ImageComparerPlugin()
    await plugin.on_startup()

    # Finished pipeline
    ctx = WatchdOcrRuntimeContext()
    plugin.on_image_grabber_image(create_image(0), ctx)
    plugin.on_processor_pipeline_finish(ctx)
    committed_hash = plugin._image_hash_cache

    # Cancelled pipeline, finish hook is never called
    plugin.on_image_grabber_image(create_image(32), WatchdOcrRuntimeContext())

    assert plugin._image_hash_cache == committed_hash


async def test_similar_image_reuses_cached_ocr():
    plugin = ImageComparerPlugin()
    await plugin.on_startup()

    ctx = WatchdOcrRuntimeContext()
    plugin.on_image_grabber_image(create_image(16), ctx)
    ctx.ocr.success = True
    ctx.ocr.text = 'cached'
    plugin.on_processor_pipeline_finish(ctx)

    new_ctx = WatchdOcrRuntimeContext()
    plugin.on_image_grabber_image(create_image(16), new_ctx)

    assert new_ctx.ocr.ignore
    assert new_ctx.ocr.text == 'cached'

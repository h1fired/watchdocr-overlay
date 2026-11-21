from src.watchdocr.processor.context import WatchdOcrRuntimeContext
from src.watchdocr.plugins.image.comparer.main import ImageComparerPlugin
from PIL import Image


def create_image(black_width: int):
    image = Image.new('RGB', (64, 64), 'white')
    image.paste((0, 0, 0), (0, 0, black_width, 64))
    return image


def create_ctx(boundings=(0, 0, 64, 64)):
    ctx = WatchdOcrRuntimeContext()
    ctx.config.boundings = boundings
    return ctx


async def create_plugin_with_cache(text='cached', boundings=(0, 0, 64, 64)):
    plugin = ImageComparerPlugin()
    await plugin.on_startup()

    ctx = create_ctx(boundings)
    plugin.on_image_grabber_image(create_image(16), ctx)
    ctx.ocr.success = True
    ctx.ocr.text = text
    plugin.on_processor_pipeline_finish(ctx)
    return plugin


async def test_cancelled_pipeline_does_not_update_image_cache():
    plugin = ImageComparerPlugin()
    await plugin.on_startup()

    # Finished pipeline
    ctx = create_ctx()
    plugin.on_image_grabber_image(create_image(0), ctx)
    plugin.on_processor_pipeline_finish(ctx)
    committed = plugin._image_cache

    # Cancelled pipeline, finish hook is never called
    plugin.on_image_grabber_image(create_image(32), create_ctx())

    assert plugin._image_cache == committed


async def test_similar_image_reuses_cached_ocr():
    plugin = await create_plugin_with_cache()

    new_ctx = create_ctx()
    plugin.on_image_grabber_image(create_image(16), new_ctx)

    assert new_ctx.ocr.ignore
    assert new_ctx.ocr.text == 'cached'


async def test_similar_image_of_another_area_is_recognized():
    plugin = await create_plugin_with_cache()

    new_ctx = create_ctx(boundings=(100, 100, 64, 64))
    plugin.on_image_grabber_image(create_image(16), new_ctx)

    assert not new_ctx.ocr.ignore
    assert new_ctx.ocr.text == ''


async def test_different_image_is_recognized():
    plugin = await create_plugin_with_cache()

    new_ctx = create_ctx()
    plugin.on_image_grabber_image(create_image(48), new_ctx)

    assert not new_ctx.ocr.ignore

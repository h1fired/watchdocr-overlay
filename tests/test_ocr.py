from src.watchdocr.processor.scale import RecognitionScaler, quad_height
from src.watchdocr.processor.ocr import Ocr
from src.watchdocr.plugins.ocr import OcrPlugin, OcrData, OcrBoxData
from PIL import Image


AREA = (0, 0, 800, 400)
SIZE = (800, 400)


def box(height, y=0):
    return OcrBoxData(
        text='text',
        coordinates=(0, y, 100, y, 100, y + height, 0, y + height)
    )


def data(*boxes, success=True):
    return OcrData(success, 'text', tuple(boxes), 0.)


def create_scaler(mode='adaptive', text_height=None, area=AREA):
    scaler = RecognitionScaler(mode_provider=lambda: mode)
    if text_height:
        scaler.remember(area, data(box(text_height)))
    return scaler


# Text height
def test_quad_height_of_rotated_box():
    assert quad_height((0, 0, 100, 0, 106, 8, 6, 8)) == 10


def test_quad_height_of_missing_coordinates():
    assert quad_height(()) == 0


# Recognition scale
def test_scale_is_original_without_previous_recognition():
    assert create_scaler().scale_for(AREA, SIZE, 0) == 1.0


def test_adaptive_scale_shrinks_to_target_text_height():
    for text_height, scale in ((80, 0.25), (40, 0.5)):
        scaler = create_scaler(text_height=text_height)
        assert scaler.scale_for(AREA, SIZE, 0) == scale


def test_adaptive_scale_uses_smallest_text():
    scaler = create_scaler()
    scaler.remember(AREA, data(box(80), box(40, y=100), box(60, y=200)))

    assert scaler.scale_for(AREA, SIZE, 0) == 0.5


def test_adaptive_scale_never_enlarges():
    assert create_scaler(text_height=10).scale_for(AREA, SIZE, 0) == 1.0


def test_adaptive_scale_has_lower_limit():
    scaler = create_scaler(text_height=400)

    assert scaler.scale_for(AREA, (2000, 1000), 0) == 0.25


def test_adaptive_scale_keeps_backend_min_image_size():
    scaler = create_scaler(text_height=80)

    assert scaler.scale_for(AREA, (800, 100), 50) == 0.5


def test_adaptive_scale_ignored_for_another_area():
    scaler = create_scaler(text_height=80, area=(10, 10, 800, 400))

    assert scaler.scale_for(AREA, SIZE, 0) == 1.0


def test_adaptive_scale_reset_after_failed_recognition():
    scaler = create_scaler(text_height=80)
    scaler.remember(AREA, data(success=False))

    assert scaler.scale_for(AREA, SIZE, 0) == 1.0


def test_original_mode_disables_adaptive_scale():
    scaler = create_scaler(mode='original', text_height=80)

    assert scaler.scale_for(AREA, SIZE, 0) == 1.0


def test_max_resolution_limit_is_kept():
    scaler = create_scaler(text_height=10)

    assert scaler.scale_for(AREA, (3840, 960), 0) == 0.5


def test_retry_when_nothing_found_at_shrunk_scale():
    assert create_scaler().retry_scale(0.5, SIZE, data()) == 1.0


def test_no_retry_at_full_scale():
    assert create_scaler().retry_scale(1.0, SIZE, data()) is None


def test_no_retry_when_text_found():
    assert create_scaler().retry_scale(0.5, SIZE, data(box(20))) is None


# OCR backend
class FakeOcrPlugin(OcrPlugin):
    def __init__(self, empty_below_scale=0.):
        super().__init__()
        self.calls = []  # (image size, scale)
        self.empty_below_scale = empty_below_scale

    async def recognizable(self, image, scale):
        self.calls.append((image.size, scale))
        if scale < self.empty_below_scale:
            return data()
        # Coordinates are returned in original image space
        return data(box(40))


async def test_plugin_applies_given_scale():
    plugin = FakeOcrPlugin()

    await plugin.recognize(Image.new('RGB', SIZE), 0.5)

    assert plugin.calls == [((400, 200), 0.5)]


# OCR service
class FakePluginManager:
    def __init__(self, plugin):
        self.plugin = plugin

    def get_realizations(self, cls):
        return [self.plugin]


def create_ocr(plugin, mode='adaptive'):
    return Ocr(FakePluginManager(plugin), create_scaler(mode))


async def test_ocr_shrinks_next_recognition_of_same_area():
    plugin = FakeOcrPlugin()
    ocr = create_ocr(plugin)

    await ocr.recognize(Image.new('RGB', SIZE), AREA)
    await ocr.recognize(Image.new('RGB', SIZE), AREA)

    assert [scale for _, scale in plugin.calls] == [1.0, 0.5]


async def test_ocr_retries_full_image_when_nothing_found():
    plugin = FakeOcrPlugin()
    ocr = create_ocr(plugin)
    await ocr.recognize(Image.new('RGB', SIZE), AREA)
    plugin.empty_below_scale = 1.0

    result = await ocr.recognize(Image.new('RGB', SIZE), AREA)

    assert [scale for _, scale in plugin.calls] == [1.0, 0.5, 1.0]
    assert len(result.boxes) == 1


async def test_ocr_without_image_fails():
    ocr = create_ocr(FakeOcrPlugin())

    result = await ocr.recognize(None, AREA)

    assert not result.success

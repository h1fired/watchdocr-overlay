from src.common.plugin import DownloadResource, DownloadablePlugin
from src.watchdocr.plugins.ocr import OcrPlugin, OcrData, OcrBoxData
from src.watchdocr.plugins.ocr.windows_one.engine import (
    OcrEngine,
    OcrLine,
    MIN_IMAGE_SIZE
)
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import asyncio


__plugin_meta__ = {
    'id': 'watchdocr-ocr-windowsone',
    'name': 'WindowsOneOCR',
    'version': (0, 1, 0)
}
__plugin_main__ = 'WindowsOneOcrPlugin'


RESOURCE_URL = 'https://github.com/h1fired/watchdocr-overlay/releases/download/v0.1.0/watchdocr_windowsone_ocr_data.zip'
RESOURCE_SHA256 = '03c4b49f0f4e863b1027e19ae84575c2c399870818d9c56bfc347e09711f74bf'


class WindowsOneOcrPlugin(OcrPlugin, DownloadablePlugin):
    _id = 'windowsone_ocr'

    class Options(OcrPlugin.Options):
        min_image_size = MIN_IMAGE_SIZE

    async def on_startup(self):
        # Engine is created and used only in one dedicated thread,
        # so DLL calls are never executed in parallel
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix='WindowsOneOcr'
        )

    async def on_shutdown(self):
        self._executor.shutdown(wait=False, cancel_futures=True)

    async def on_after_download(self):
        dlls_path = self.get_resource_path()
        loop = asyncio.get_running_loop()
        self._api = await loop.run_in_executor(
            self._executor,
            lambda: OcrEngine(dlls_path=dlls_path)
        )

    def get_download_resource(self):
        return DownloadResource(
            url=RESOURCE_URL,
            sha256=RESOURCE_SHA256
        )

    def get_priority(self):
        return 1

    def get_provider_name(self):
        return 'WindowsOne'

    async def recognizable(self, image: Image.Image, scale: float):
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(self._executor, self._api.recognize, image)
        boxes = self._parse_boxes(res.lines, scale)
        return OcrData(True, res.text, tuple(boxes), 0., True)

    def _parse_boxes(self, rlines: tuple[OcrLine, ...], scale: float):
        boxes = []
        for line in rlines:
            words = line.words

            if words:
                confs = [w.confidence for w in words if w.confidence is not None]
                line_confidence = sum(confs) / len(confs) if confs else 0.
            elif line.boundings:
                line_confidence = 0.
            else:
                continue

            line_coordinates = tuple([int(b / scale) for b in line.boundings])

            box = OcrBoxData(
                text=line.text,
                coordinates=line_coordinates,
                confidence=line_confidence,
            )
            boxes.append(box)
        return boxes

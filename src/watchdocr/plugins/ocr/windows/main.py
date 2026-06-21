from src.watchdocr.plugins.ocr import OcrPlugin, OcrData
import winrt.windows.media.ocr as ocr
import winrt.windows.graphics.imaging as imaging
import winrt.windows.globalization as globalization
from winrt.windows.storage.streams import InMemoryRandomAccessStream, DataWriter
from PIL import Image
import asyncio
import io


__plugin_meta__ = {
    'id': 'watchdocr.ocr.windows',
    'name': 'WindowsOCR',
    'version': (0, 1, 0)
}
__plugin_main__ = 'WindowsOcrPlugin'


class WindowsOcrPlugin(OcrPlugin):
    def on_startup(self):
        self._async_loop = asyncio.new_event_loop()

    def get_priority(self):
        return 2

    def get_provider_name(self):
        return 'Windows'

    def recognize(self, image: Image.Image):
        try:
            image, scale = self.process_image(image)
            res = self._async_loop.run_until_complete(self._recognize(image))
            text = res.text
            boxes = self._parse_boxes(res.lines, scale)

            return OcrData(text, tuple(boxes), 0.)
        except Exception:
            return OcrData('', tuple(), 0)

    async def _recognize(self, image: Image.Image):
        buf = io.BytesIO()
        image.save(buf, format='BMP')
        data = buf.getvalue()

        stream = InMemoryRandomAccessStream()
        writer = DataWriter(stream)
        writer.write_bytes(data)
        await writer.store_async()
        await writer.flush_async()
        stream.seek(0)

        decoder = await imaging.BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()

        lang = globalization.Language('en-US')
        engine = ocr.OcrEngine.try_create_from_language(lang)
        buf.close()
        return await engine.recognize_async(bitmap)

    def _parse_boxes(self, rlines, scale: float):
        lines = []
        for line in self._winrt_to_list(rlines):
            words = self._winrt_to_list(line.words)
            x = min(w.bounding_rect.x for w in words)
            y = min(w.bounding_rect.y for w in words)
            x2 = max(w.bounding_rect.x + w.bounding_rect.width for w in words)
            y2 = max(w.bounding_rect.y + w.bounding_rect.height for w in words)
            lines.append((
                line.text,
                (
                    int(x / scale),
                    int(y / scale),
                    int(x2 / scale),
                    int(y2 / scale)
                ),
                0.
            ))
        return lines

    def _winrt_to_list(self, vector):
        return [vector.get_at(i) for i in range(vector.size)]

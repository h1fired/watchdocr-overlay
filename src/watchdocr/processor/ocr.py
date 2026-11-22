from src.common.plugin import PluginManager
from src.watchdocr.plugins.ocr import OcrPlugin, OcrData
from src.watchdocr.processor.scale import RecognitionScaler
from src.common.utils.logging import log
from config import settings
from PIL import Image


LOG_OCR = 'OCR'


class Ocr:
    def __init__(
        self,
        plugins_manager: PluginManager,
        scaler: RecognitionScaler | None = None
    ):
        self._plugins_manager = plugins_manager
        self._scaler = scaler or RecognitionScaler(
            mode_provider=lambda: settings.ocr_recognition_scale
        )

    async def recognize(
        self,
        image: Image.Image | None,
        area: tuple[int, int, int, int]
    ):
        api = self._get_backend()

        if image is None:
            return OcrData(
                success=False,
                text='Failed to recognize text! Error: no image',
                boxes=tuple(),
                confidence=0.
            )

        min_image_size = api.Options.min_image_size
        scale = self._scaler.scale_for(area, image.size, min_image_size)
        data = await api.recognize(image, scale)

        retry_scale = self._scaler.retry_scale(scale, image.size, data)
        if retry_scale is not None:
            log.debug(
                'No text at scale %.2f, retrying at %.2f',
                scale, retry_scale,
                extra={'title': LOG_OCR}
            )
            data = await api.recognize(image, retry_scale)

        self._scaler.remember(area, data)
        return data

    def _get_backend(self) -> OcrPlugin:
        apis = self._plugins_manager.get_realizations(OcrPlugin)
        if not len(apis):
            log.error(
                'No OCR backend plugins found!',
                extra={'title': LOG_OCR}
            )
            raise ValueError('OCR backend plugins not found')
        return sorted(apis, key=lambda e: e.get_priority())[0]

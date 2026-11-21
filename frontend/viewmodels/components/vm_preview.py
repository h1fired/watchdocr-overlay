from frontend.viewmodels.common.mvvm import QmlViewModel
from frontend.viewmodels.types.image import ImageProvider
from qt.core import Signal
from src.common.event import IEvent, EventData
from src.common.utils.logging import log
from src.watchdocr.processor.image import ScreenGrabber
from src.watchdocr.processor.processor import Events
from qasync import asyncSlot
from PIL import Image
import asyncio


class PreviewViewModel(QmlViewModel):
    _name = 'Preview'

    previewUpdated = Signal()
    previewAreaUpdated = Signal()

    def onLoaded(self):
        self._area_revision = 0
        self.getEventSystem().listen(self.onEvent)

    def onEvent(self, event: IEvent, data: EventData):
        match event:
            case Events.PROCESSOR_AREA_IMAGE_CHANGED:
                self._area_revision += 1
                asyncio.ensure_future(self.onPreviewAreaImage(data.image, self._area_revision))

    @asyncSlot()
    async def requestAllScreensPreview(self):
        image = await asyncio.to_thread(ScreenGrabber.grab_all_screens)
        if not image:
            return

        qimage = await asyncio.to_thread(ImageProvider.convertImage, image)

        from frontend.core import GuiCoreApplication
        providers = GuiCoreApplication().image_providers()
        provider = providers['preview_screens']
        provider.setQImage(qimage)
        self.previewUpdated.emit()

    async def onPreviewAreaImage(self, image: Image.Image | None, revision: int):
        if image is None:
            return

        try:
            # Conversion is done in thread, so UI isn't blocked
            qimage = await asyncio.to_thread(ImageProvider.convertImage, image)
        except Exception:
            log.exception('Failed to convert area preview image', extra={'title': 'Preview'})
            return

        # Newer image was received while converting
        if revision != self._area_revision:
            return

        from frontend.core import GuiCoreApplication
        providers = GuiCoreApplication().image_providers()
        provider = providers['preview_area']
        provider.setQImage(qimage)
        self.previewAreaUpdated.emit()

from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Signal
from src.common.event import IEvent, EventData
from src.watchdocr.processor.image import ScreenGrabber
from src.watchdocr.processor.processor import Events
from qasync import asyncSlot
import asyncio


class PreviewViewModel(QmlViewModel):
    _name = 'Preview'

    previewUpdated = Signal()
    previewAreaUpdated = Signal()

    def onLoaded(self):
        self.getEventSystem().listen(self.onEvent)

    def onEvent(self, event: IEvent, data: EventData):
        match event:
            case Events.PROCESSOR_AREA_IMAGE_CHANGED:
                self.onPreviewAreaImage(data.image)

    @asyncSlot()
    async def requestAllScreensPreview(self):
        image = await asyncio.to_thread(ScreenGrabber.grab_all_screens)
        if not image:
            return

        from frontend.core import GuiCoreApplication
        providers = GuiCoreApplication().image_providers()
        provider = providers['preview_screens']
        provider.setImage(image)
        self.previewUpdated.emit()

    def onPreviewAreaImage(self, image):
        from frontend.core import GuiCoreApplication
        providers = GuiCoreApplication().image_providers()
        provider = providers['preview_area']
        provider.setImage(image)
        self.previewAreaUpdated.emit()

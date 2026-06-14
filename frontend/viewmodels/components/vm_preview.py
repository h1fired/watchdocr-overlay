from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Signal, Slot
from src.common.event import IEvent, EventData
from src.watchdocr.processor.image import grab_all_screens
from src.watchdocr.processor.processor import Events


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
                self.previewAreaUpdated.emit()

    @Slot()
    def requestAllScreensPreview(self):
        image = grab_all_screens()

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

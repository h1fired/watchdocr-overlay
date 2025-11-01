from common.event import Event
from frontend.common.mvvm_qml import QmlViewModel
from src.grabber.service import ImageGrabberService
from qt.core import Signal, Slot


class PreviewViewModel(QmlViewModel):
    _name = 'Preview'

    previewUpdated = Signal()

    def onLoaded(self):
        Event.subscribe(
            system=self.events,
            event=ImageGrabberService.Events.IMAGE_ALL_SCREENS_CAPTURE,
            handler=self.onImageCapture
        )

    @Slot()
    def QmlRequestScreensPreviewImage(self):
        image_grabber_s = self.accessor.get(ImageGrabberService)
        image_grabber_s.grab_all_screens()

    def onImageCapture(self, e):
        from frontend.core import GuiCoreApplication
        providers = GuiCoreApplication().image_providers()
        provider = providers['preview_screens']
        provider.setImage(e.image)
        self.previewUpdated.emit()

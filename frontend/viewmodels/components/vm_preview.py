from frontend.viewmodels.common.mvvm import QmlViewModel
from frontend.qt.core import Signal, Slot
from src.backend.ocrtranslate.image import ScreenGrabber


class PreviewViewModel(QmlViewModel):
    _name = 'Preview'

    previewUpdated = Signal()
    previewAreaUpdated = Signal()

    @Slot()
    def requestAllScreensPreview(self):
        image = ScreenGrabber.grab_all_screens()
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

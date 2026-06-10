from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Signal, Slot
from src.watchdocr.processor.image import grab_all_screens


class PreviewViewModel(QmlViewModel):
    _name = 'Preview'

    previewUpdated = Signal()

    @Slot()
    def requestAllScreensPreview(self):
        image = grab_all_screens()

        from frontend.core import GuiCoreApplication
        providers = GuiCoreApplication().image_providers()
        provider = providers['preview_screens']
        provider.setImage(image)
        self.previewUpdated.emit()

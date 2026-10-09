from frontend.viewmodels.common.mvvm import QmlViewModel
from frontend.qt.core import Property, Signal


class OcrViewModel(QmlViewModel):
    _name = 'Ocr'

    providerNameChanged = Signal()

    def getProviderName(self):
        # TODO: Implement
        return "Dummy"

    providerName = Property(str, getProviderName, notify=providerNameChanged)

from frontend.viewmodels.common.mvvm import QmlViewModel
from src.watchdocr.api.ocr import OcrAPI
from qt.core import Property, Signal


class OcrViewModel(QmlViewModel):
    _name = 'Ocr'
    _needed_api = (OcrAPI,)

    providerNameChanged = Signal()

    def getProviderName(self):
        api = self.getApi(OcrAPI)
        return api.get_provider_name()

    providerName = Property(str, getProviderName, notify=providerNameChanged)

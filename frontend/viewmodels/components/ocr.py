from frontend.common.mvvm_qml import QmlViewModel
from src.tocr.service import OCRTranslateService
from qt.core import Signal, Property


class OcrViewModel(QmlViewModel):
    _name = 'Ocr'

    backendsUpdated = Signal()
    currentBackendUpdated = Signal()

    def onLoaded(self):
        ocr_translate_s = self.accessor.get(OCRTranslateService)
        ocr = ocr_translate_s.ocr()
        backends = ocr.backends()
        backends.objects.register(lambda _: self.backendsUpdated.emit())

    def onFullyLoaded(self):
        self.backendsUpdated.emit()
        self.currentBackendUpdated.emit()

    def getBackends(self):
        if not self.accessor:
            return list()
        ocr_translate_s = self.accessor.get(OCRTranslateService)
        ocr = ocr_translate_s.ocr()
        backends = ocr.backends()
        return [n.name for n in backends.objects.keys()]

    backends = Property(list, getBackends, notify=backendsUpdated)

    def getCurrentBackend(self):
        if not self.accessor:
            return ''
        ocr_translate_s = self.accessor.get(OCRTranslateService)
        ocr = ocr_translate_s.ocr()
        backends = ocr.backends()
        return backends.current().name

    def setCurrentBackend(self, backend: str):
        ocr_translate_s = self.accessor.get(OCRTranslateService)
        ocr = ocr_translate_s.ocr()
        backends = ocr.backends()
        cls = backends.get_by_name(backend)
        backends.set(cls)

    currentBackend = Property(str, getCurrentBackend, setCurrentBackend, notify=currentBackendUpdated)

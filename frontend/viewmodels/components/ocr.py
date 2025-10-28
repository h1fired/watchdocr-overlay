from frontend.common.mvvm_qml import QmlViewModel
from src.ocr.service import OcrService
from qt.core import Signal, Property


class OcrViewModel(QmlViewModel):
    _name = 'Ocr'

    backendsUpdated = Signal()
    currentBackendUpdated = Signal()

    def onLoaded(self):
        ocr_s = self.accessor.get(OcrService)
        backends = ocr_s.backends()
        backends.objects.register(lambda _: self.backendsUpdated.emit())

    def onFullyLoaded(self):
        self.backendsUpdated.emit()
        self.currentBackendUpdated.emit()

    def getBackends(self):
        if not self.accessor:
            return list()
        ocr_s = self.accessor.get(OcrService)
        backends = ocr_s.backends()
        return [n.name for n in backends.objects.keys()]

    backends = Property(list, getBackends, notify=backendsUpdated)

    def getCurrentBackend(self):
        if not self.accessor:
            return ''
        ocr_s = self.accessor.get(OcrService)
        backends = ocr_s.backends()
        return backends.current().name

    def setCurrentBackend(self, backend: str):
        ocr_s = self.accessor.get(OcrService)
        backends = ocr_s.backends()
        cls = backends.get_by_name(backend)
        backends.set(cls)

    currentBackend = Property(str, getCurrentBackend, setCurrentBackend, notify=currentBackendUpdated)

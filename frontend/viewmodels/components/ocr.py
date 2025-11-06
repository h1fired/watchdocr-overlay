from frontend.common.mvvm_qml import QmlViewModel
from src.ocr.service import OcrService
from src.ocr.ocr import mode_to_str, str_to_mode
from qt.core import Signal, Property


class OcrViewModel(QmlViewModel):
    _name = 'Ocr'

    backendsUpdated = Signal()
    currentBackendUpdated = Signal()
    modesUpdated = Signal()
    modeUpdated = Signal()

    def onLoaded(self):
        ocr_s = self.accessor.get(OcrService)
        backends = ocr_s.backends()
        backends.objects.register(lambda _: self.backendsUpdated.emit())

    def onFullyLoaded(self):
        self.backendsUpdated.emit()
        self.currentBackendUpdated.emit()
        self.modesUpdated.emit()
        self.modeUpdated.emit()

    def getBackends(self):
        if not self.accessor:
            return list()
        ocr_s = self.accessor.get(OcrService)
        backends = ocr_s.backends()
        return sorted([n.name for n in backends.objects.keys()])

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

    def getModes(self):
        if not self.accessor:
            return []
        ocr_s = self.accessor.get(OcrService)
        return [mode_to_str(m) for m in ocr_s.modes()]

    modes = Property('QVariantList', getModes, notify=modesUpdated)

    def getMode(self):
        if not self.accessor:
            return ''
        ocr_s = self.accessor.get(OcrService)
        return mode_to_str(ocr_s.current_mode())

    def setMode(self, arg__1: str):
        ocr_s = self.accessor.get(OcrService)
        ocr_s.change_mode(str_to_mode(arg__1))

    mode = Property(str, getMode, setMode, notify=modeUpdated)

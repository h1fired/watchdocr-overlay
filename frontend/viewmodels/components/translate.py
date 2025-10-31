from frontend.common.mvvm_qml import QmlViewModel
from src.translator.service import TranslationService
from qt.core import Signal, Property


class TranslationViewModel(QmlViewModel):
    _name = 'Translate'

    backendsUpdated = Signal()
    currentBackendUpdated = Signal()
    sourceLanguageUpdated = Signal()
    targetLanguageUpdated = Signal()

    def onLoaded(self):
        ocr_s = self.accessor.get(TranslationService)
        backends = ocr_s.backends()
        backends.objects.register(lambda _: self.backendsUpdated.emit())
        backends.current().register(lambda _: self.sourceLanguageUpdated.emit())
        backends.current().register(lambda _: self.targetLanguageUpdated.emit())

    def onFullyLoaded(self):
        self.backendsUpdated.emit()
        self.currentBackendUpdated.emit()
        self.sourceLanguageUpdated.emit()
        self.targetLanguageUpdated.emit()

    def getBackends(self):
        if not self.accessor:
            return list()
        ocr_s = self.accessor.get(TranslationService)
        backends = ocr_s.backends()
        return sorted([n.name for n in backends.objects.keys()])

    backends = Property(list, getBackends, notify=backendsUpdated)

    def getCurrentBackend(self):
        if not self.accessor:
            return ''
        ocr_s = self.accessor.get(TranslationService)
        backends = ocr_s.backends()
        return backends.current().value.name

    def setCurrentBackend(self, backend: str):
        ocr_s = self.accessor.get(TranslationService)
        backends = ocr_s.backends()
        cls = backends.get_by_name(backend)
        backends.set(cls)

    currentBackend = Property(str, getCurrentBackend, setCurrentBackend, notify=currentBackendUpdated)

    def getSourceLanguages(self):
        if not self.accessor:
            return []
        ocr_s = self.accessor.get(TranslationService)
        backend = ocr_s.backends().current().value
        return backend.source_languages().verbose()

    sourceLanguages = Property('QVariantList', getSourceLanguages, notify=sourceLanguageUpdated)

    def getTargetLanguages(self):
        if not self.accessor:
            return []
        ocr_s = self.accessor.get(TranslationService)
        backend = ocr_s.backends().current().value
        return backend.target_languages().verbose()

    targetLanguages = Property('QVariantList', getTargetLanguages, notify=targetLanguageUpdated)

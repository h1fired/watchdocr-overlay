from .backend import TranslationBackendManager, TranslationStatus
from .backend.deepl import DeeplTranslationBackend
from .backend.google import GoogleTranslationBackend


backends = [
    DeeplTranslationBackend,
    GoogleTranslationBackend
]


class Translator:
    def __init__(self):
        self._backends = TranslationBackendManager(backends)

    def translate(self, text: str, _from: str, to: str):
        backend = self._backends.current().value
        return backend.translate(text, _from, to)

    def backends(self):
        return self._backends

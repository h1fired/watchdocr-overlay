from .backend import TranslationBackendManager
from .backend.deepl import DeeplTranslationBackend
from .backend.google import GoogleTranslationBackend


backends = [
    DeeplTranslationBackend,
    GoogleTranslationBackend
]


class Translator:
    def __init__(self):
        self._backends = TranslationBackendManager(backends)

    def translate(self, text: str, translate_to: str):
        backend = self._backends.current()
        return backend.translate(text, translate_to)

    def backends(self):
        return self._backends

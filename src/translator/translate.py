from .backend.deepl import DeeplTranslationBackend


class Translator:
    def __init__(self, backend=DeeplTranslationBackend):
        self._backend = backend()
        self._backend.load()

    def translate(self, text: str, translate_to: str):
        return self._backend.translate(text, translate_to)

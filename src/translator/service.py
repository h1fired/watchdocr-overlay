from common.service import Service
from src.translator.translate import Translator


class TranslationService(Service):
    def on_init(self):
        self._translator = Translator()

    def translate(self, text: str, _from: str, to: str):
        return self._translator.translate(text, _from, to)

    def backends(self):
        return self._translator.backends()

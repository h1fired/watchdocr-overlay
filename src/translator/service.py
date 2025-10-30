from common.service import Service
from src.translator.translate import Translator


class TranslationService(Service):
    def on_init(self):
        self._translator = Translator()

    def translate(self, text: str, to: str = 'EN-US'):
        return self._translator.translate(text, to)

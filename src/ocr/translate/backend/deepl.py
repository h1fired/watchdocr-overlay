from . import TranslationBackend
from config import config
import deepl


API_KEY = config.DEEPL_API_KEY


class DeeplTranslationBackend(TranslationBackend):

    def load(self):
        self.client = deepl.DeepLClient(API_KEY)

    def translate(self, text, translate_to='EN'):
        result = self.client.translate_text(text, target_lang=translate_to)
        return result.text

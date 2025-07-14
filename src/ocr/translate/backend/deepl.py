from . import TranslationBackend
import deepl


API_KEY = '05445a92-e919-487e-9731-007952f66c32:fx'


class DeeplTranslationBackend(TranslationBackend):

    def load(self):
        self.client = deepl.DeepLClient(API_KEY)

    def translate(self, text):
        result = self.client.translate_text(text, target_lang='UK')
        return result.text

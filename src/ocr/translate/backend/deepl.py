from . import TranslationBackend
import deepl


API_KEY = ''


class DeeplTranslationBackend(TranslationBackend):

    def load(self):
        self.client = deepl.DeepLClient(API_KEY)

    def translate(self, text):
        result = self.client.translate_text(text, target_lang='UK')
        return result.text

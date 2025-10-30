from . import TranslationBackend, TranslationStatus
from config import config
import deepl


API_KEY = config.DEEPL_API_KEY


class DeeplTranslationBackend(TranslationBackend):
    name = 'Deepl'
    languages_repr = {
        'EN': 'EN-US',
        'UK': 'UK'
    }

    def __init__(self):
        super().__init__()
        self.client = deepl.DeepLClient(API_KEY)

    def translate(self, text, translate_to: str):
        language = self.languages_repr.get(translate_to, translate_to)
        try:
            result = self.client.translate_text(text, target_lang=language)
            if not result.text:
                raise ValueError('No translation')
        except Exception as e:
            return {'success': TranslationStatus.ERROR, 'text': repr(e)}
        return {'success': TranslationStatus.SUCCESS, 'text': result.text}

from . import TranslationBackend, TranslationStatus
from config import config
import deepl


API_KEY = config.DEEPL_API_KEY


class DeeplTranslationBackend(TranslationBackend):
    name = 'Deepl'
    languages_repr = {
        'AUTO': None,
        'AR': 'AR',
        'BG': 'BG',
        'CS': 'CS',
        'DA': 'DA',
        'DE': 'DE',
        'EL': 'EL',
        'EN': 'EN',
        'ES': 'ES',
        'ET': 'ET',
        'FI': 'FI',
        'FR': 'FR',
        'HE': 'HE',
        'HU': 'HU',
        'ID': 'ID',
        'IT': 'IT',
        'JA': 'JA',
        'KO': 'KO',
        'LT': 'LT',
        'LV': 'LV',
        'NB': 'NB',
        'NL': 'NL',
        'PL': 'PL',
        'PT': 'PT',
        'RO': 'RO',
        'SK': 'SK',
        'SL': 'SL',
        'SV': 'SV',
        'TH': 'TH',
        'TR': 'TR',
        'UK': 'UK',
        'VI': 'VI',
        'ZH': 'ZH'
    }

    def __init__(self):
        super().__init__()
        self.client = deepl.DeepLClient(API_KEY)

    def translate(self, text, _from: str, to: str):
        from_language = self.languages().convert(_from)
        to_language = self.languages().convert(to)

        try:
            result = self.client.translate_text(
                text,
                source_lang=from_language,
                target_lang=to_language
            )
            if not result.text:
                raise ValueError('No translation')
        except Exception as e:
            return {'success': TranslationStatus.ERROR, 'text': repr(e)}
        return {'success': TranslationStatus.SUCCESS, 'text': result.text}

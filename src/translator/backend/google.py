from src.translator.backend import TranslationBackend, TranslationStatus
import requests


URL = 'https://translate.googleapis.com/translate_a/single'
SOURCE_LANGUAGES = {
    'AUTO': 'auto',
    'AR': 'ar',
    'BN': 'bn',
    'BG': 'bg',
    'CA': 'ca',
    'ZH': 'zh-CN',
    'HR': 'hr',
    'CS': 'cs',
    'DA': 'da',
    'NL': 'nl',
    'EN': 'en',
    'ET': 'et',
    'FI': 'fi',
    'FR': 'fr',
    'DE': 'de',
    'EL': 'el',
    'GU': 'gu',
    'HE': 'he',
    'HI': 'hi',
    'HU': 'hu',
    'IS': 'is',
    'ID': 'id',
    'IT': 'it',
    'JA': 'ja',
    'KN': 'kn',
    'KO': 'ko',
    'LV': 'lv',
    'LT': 'lt',
    'ML': 'ml',
    'MR': 'mr',
    'NB': 'no',
    'FA': 'fa',
    'PL': 'pl',
    'PT': 'pt',
    'PA': 'pa',
    'RO': 'ro',
    'RU': 'ru',
    'SK': 'sk',
    'SL': 'sl',
    'ES': 'es',
    'SW': 'sw',
    'SV': 'sv',
    'TA': 'ta',
    'TE': 'te',
    'TH': 'th',
    'TR': 'tr',
    'UK': 'uk',
    'UR': 'ur',
    'VI': 'vi',
    'ZU': 'zu'
}
TARGET_LANGUAGES = {
    'AR': 'ar',
    'BN': 'bn',
    'BG': 'bg',
    'CA': 'ca',
    'ZH': 'zh-CN',
    'HR': 'hr',
    'CS': 'cs',
    'DA': 'da',
    'NL': 'nl',
    'EN': 'en',
    'ET': 'et',
    'FI': 'fi',
    'FR': 'fr',
    'DE': 'de',
    'EL': 'el',
    'GU': 'gu',
    'HE': 'he',
    'HI': 'hi',
    'HU': 'hu',
    'IS': 'is',
    'ID': 'id',
    'IT': 'it',
    'JA': 'ja',
    'KN': 'kn',
    'KO': 'ko',
    'LV': 'lv',
    'LT': 'lt',
    'ML': 'ml',
    'MR': 'mr',
    'NB': 'no',
    'FA': 'fa',
    'PL': 'pl',
    'PT': 'pt',
    'PA': 'pa',
    'RO': 'ro',
    'RU': 'ru',
    'SK': 'sk',
    'SL': 'sl',
    'ES': 'es',
    'SW': 'sw',
    'SV': 'sv',
    'TA': 'ta',
    'TE': 'te',
    'TH': 'th',
    'TR': 'tr',
    'UK': 'uk',
    'UR': 'ur',
    'VI': 'vi',
    'ZU': 'zu'
}


class GoogleTranslationBackend(TranslationBackend):
    name = 'Google'
    source_langs = SOURCE_LANGUAGES
    target_langs = TARGET_LANGUAGES

    def translate(self, text, _from: str, to: str):
        from_language = self.source_languages().convert(_from)
        to_language = self.target_languages().convert(to)

        try:
            params = {
                'client': 'gtx',
                'sl': from_language,
                'tl': to_language,
                'dt': 't',
                'q': text
            }
            response = requests.get(URL, params=params)
            text = ''.join(t[0] for t in response.json()[0])

            if not text:
                raise ValueError('No translation')
        except Exception as e:
            return {'status': TranslationStatus.ERROR, 'text': repr(e)}
        return {'status': TranslationStatus.SUCCESS, 'text': text}

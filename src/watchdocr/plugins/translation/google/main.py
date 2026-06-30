from src.watchdocr.plugins.translation import TranslatorPlugin, TranslationData
import requests


__plugin_meta__ = {
    'id': 'watchdocr.translator.google',
    'name': 'GoogleTranslator',
    'version': (0, 1, 0)
}
__plugin_main__ = 'GoogleTranslatorPlugin'


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
    'ORIG': 'orig',
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


class GoogleTranslatorPlugin(TranslatorPlugin):
    def on_startup(self):
        self.session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        self.session.headers.update(headers)

    def on_translate(self, text, _from, to):
        if text == '':
            return TranslationData(True, text, text)

        if to == 'ORIG':
            return TranslationData(True, text, text)

        from_language = self.source_languages()[_from]
        to_language = self.target_languages()[to]

        err_msg = 'Translation error: Unknown request error'
        try:
            params = {
                'client': 'gtx',
                'sl': from_language,
                'tl': to_language,
                'dt': 't',
                'q': text
            }
            response = self.session.get(URL, params=params, timeout=5)
            translated_text = ''.join(t[0] for t in response.json()[0])

            if not translated_text:
                raise ValueError('No translation')
            return TranslationData(True, text, translated_text)
        except requests.exceptions.Timeout:
            err_msg = 'Translation error: Network timeout'
        except requests.exceptions.ConnectionError:
            err_msg = 'Translation error: Network unavailable'
        except requests.exceptions.HTTPError:
            err_msg = 'Translation error: Server returned an error response'
        return TranslationData(False, err_msg, err_msg)

    def source_languages(self):
        return SOURCE_LANGUAGES

    def target_languages(self):
        return TARGET_LANGUAGES

    def get_provider_name(self):
        return 'Google'

    def get_priority(self):
        return 1

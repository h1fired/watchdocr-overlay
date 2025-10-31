from src.translator.backend import TranslationBackend, TranslationStatus
import requests


URL = 'https://translate.googleapis.com/translate_a/single'
SOURCE_LANGUAGES = {
    'AUTO': 'auto',
    'EN': 'en',
    'UK': 'uk'
}
TARGET_LANGUAGES = {
    'EN': 'en',
    'UK': 'uk'
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
            return {'success': TranslationStatus.ERROR, 'text': repr(e)}
        return {'success': TranslationStatus.SUCCESS, 'text': text}

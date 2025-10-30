from src.translator.backend import TranslationBackend, TranslationStatus
import requests


URL = 'https://translate.googleapis.com/translate_a/single'


class GoogleTranslationBackend(TranslationBackend):
    name = 'Google'
    languages_repr = {
        'EN': 'en',
        'UK': 'uk'
    }

    def translate(self, text, translate_to: str):
        language = self.languages_repr.get(translate_to, translate_to)
        try:
            params = {
                'client': 'gtx',
                'sl': 'en',
                'tl': language,
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

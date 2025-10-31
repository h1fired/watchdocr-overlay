from src.translator.backend import TranslationBackend, TranslationStatus
import requests


URL = 'https://translate.googleapis.com/translate_a/single'


class GoogleTranslationBackend(TranslationBackend):
    name = 'Google'
    languages_repr = {
        'AUTO': 'auto',
        'EN': 'en',
        'UK': 'uk'
    }

    def translate(self, text, _from: str, to: str):
        from_language = self.languages().convert(_from)
        to_language = self.languages().convert(to)

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

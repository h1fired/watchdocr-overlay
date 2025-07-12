import gettext as gt
from .utils.meta import Singleton
from .utils.logger import log


LANGUAGES = {
    'English': 'en',
    'Ukrainian': 'ua',
}


LANGUAGES_VERBOSE = {
    'English': 'English',
    'Ukrainian': 'Українська',
}


class Translator(metaclass=Singleton):
    def __init__(self):
        self._t = None

    def update_language(self, language: str, localedir: str):
        try:
            translation = gt.translation(
                'messages',
                localedir=localedir,
                languages=[LANGUAGES[language]]
            )
            translation.install()
            self._t = translation.gettext
        except FileNotFoundError as e:
            log.error(f'[TRANSLATE] {e}')
            self._t = gt.gettext

    def gettext(self, text: str):
        return self._t(text)


class TStr:
    def __init__(self, text: str):
        self._orig_text = text
        self._tran_text = text
        self.update()

    def get_original(self):
        return self._orig_text

    def get_translated(self):
        return self._tran_text

    def update(self):
        self._tran_text = Translator().gettext(self._orig_text)


def gettext(text: str):
    return Translator().gettext(text)


def gettext_obj(text: str):
    return TStr(text)

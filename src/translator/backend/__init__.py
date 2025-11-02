from common.observable import ObservableDict, ObservableVar
from common.utils import key_by_value
from src.translator.types import LANGUAGES_VERBOSE
from enum import IntEnum
from typing import Iterable


class TranslationStatus(IntEnum):
    ERROR = 0
    SUCCESS = 1


class TranslationDictionary:
    def __init__(self, languages: dict[str, str]):
        self._languages = languages
        self._verbose = {lang: LANGUAGES_VERBOSE[lang] for lang in languages.keys()}

    def verbose(self):
        return tuple(self._verbose.values())

    def all(self):
        return self._verbose

    def convert(self, language: str):
        return self._languages[language]

    def verbose_to_id(self, verbose: str):
        return key_by_value(self._verbose, verbose)


class TranslationBackend:
    name: str
    source_langs: dict
    target_langs: dict

    def __init__(self):
        if not hasattr(self, 'name'):
            raise ValueError('OCR backend should have name property')
        self._source_languages = TranslationDictionary(self.source_langs)
        self._target_languages = TranslationDictionary(self.target_langs)

    def translate(self, text: str, _from: str, to: str):
        raise NotImplementedError

    def source_languages(self):
        return self._source_languages

    def target_languages(self):
        return self._target_languages


class TranslationBackendManager:
    def __init__(self, backends: Iterable[type[TranslationBackend]]):
        self._objects = ObservableDict({b: b() for b in backends})
        self._objects[DummyTranslationBackend] = DummyTranslationBackend()
        self._current = ObservableVar(TranslationBackend, self._objects[DummyTranslationBackend])

    def register(self, backend: type[TranslationStatus]):
        if backend in self._objects.keys():
            raise KeyError('OCR backend already exists')
        self._objects[backend] = backend()

    def unregister(self, backend: type[TranslationStatus]):
        if backend not in self._objects.keys():
            raise KeyError('OCR backend does not exists')
        self._objects.pop(backend)

    def set(self, backend: type[TranslationStatus]):
        self._current.value = self._objects[backend]

    def get_by_name(self, backend: str):
        for b in self._objects.keys():
            if b.name == backend:
                return b
        raise KeyError('OCR backend does not exists')

    def current(self):
        return self._current

    @property
    def objects(self):
        return self._objects


class DummyTranslationBackend(TranslationBackend):
    name = '1_Dummy'
    source_langs = {'AUTO': 'AUTO'}
    target_langs = {'AUTO': 'AUTO'}

    def translate(self, text, _from, to):
        text = f'DUMMY TRANSLATED FROM {_from} TO {to}\n{text}'
        return {'success': TranslationStatus.SUCCESS, 'text': text}

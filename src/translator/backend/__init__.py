from common.observable import ObservableDict
from enum import IntEnum
from typing import Iterable


class TranslationStatus(IntEnum):
    ERROR = 0
    SUCCESS = 1


class TranslationBackend:
    name: str
    languages_repr: dict

    def __init__(self):
        if not hasattr(self, 'name'):
            raise ValueError('OCR backend should have name property')

    def translate(self, text: str, translate_to: str):
        raise NotImplementedError


class TranslationBackendManager:
    def __init__(self, backends: Iterable[type[TranslationBackend]]):
        self._objects = ObservableDict({b: b() for b in backends})
        self._objects[DummyTranslationBackend] = DummyTranslationBackend()
        self._current = self._objects[DummyTranslationBackend]

    def register(self, backend: type[TranslationStatus]):
        if backend in self._objects.keys():
            raise KeyError('OCR backend already exists')
        self._objects[backend] = backend()

    def unregister(self, backend: type[TranslationStatus]):
        if backend not in self._objects.keys():
            raise KeyError('OCR backend does not exists')
        self._objects.pop(backend)

    def set(self, backend: type[TranslationStatus]):
        self._current = self._objects[backend]

    def get_by_name(self, backend: str):
        for b in self._objects.keys():
            if b.name == backend:
                return b
        raise KeyError('OCR backend does not exists')

    def current(self) -> TranslationBackend:
        return self._current

    @property
    def objects(self):
        return self._objects


class DummyTranslationBackend(TranslationBackend):
    name = '1_Dummy'

    def translate(self, text, translate_to):
        text = f'DUMMY TRANSLATED TO {translate_to}: {text}'
        return {'success': TranslationBackend, 'text': text}

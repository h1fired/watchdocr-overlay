from common.observable import ObservableDict
from PIL import Image
from typing import Iterable
from enum import IntEnum


class OcrStatus(IntEnum):
    ERROR = 0
    SUCCESS = 1


class OcrBackend:
    name: str

    def __init__(self):
        if not hasattr(self, 'name'):
            raise ValueError('Translation backend should have name property')

    def recognize(self, image: Image.Image) -> dict[OcrStatus, str]:
        raise NotImplementedError


class OcrBackendManager:
    def __init__(self, backends: Iterable[type[OcrBackend]]):
        self._objects = ObservableDict({b: b() for b in backends})
        self._objects[DummyOcrBackend] = DummyOcrBackend()
        self._current = self._objects[DummyOcrBackend]

    def register(self, backend: type[OcrBackend]):
        if backend in self._objects.keys():
            raise KeyError('OCR backend already exists')
        self._objects[backend] = backend()

    def unregister(self, backend: type[OcrBackend]):
        if backend not in self._objects.keys():
            raise KeyError('OCR backend does not exists')
        self._objects.pop(backend)

    def set(self, backend: type[OcrBackend]):
        self._current = self._objects[backend]

    def get_by_name(self, backend: str):
        for b in self._objects.keys():
            if b.name == backend:
                return b
        raise KeyError('OCR backend does not exists')

    def current(self) -> OcrBackend:
        return self._current

    @property
    def objects(self):
        return self._objects


class DummyOcrBackend(OcrBackend):
    name = '1_Dummy'

    def recognize(self, image):
        text = 'Dummy OCR text for development testing.'
        return {'status': OcrStatus.SUCCESS, 'text': text}

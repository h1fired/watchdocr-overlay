from common.observable import ObservableDict
from PIL import Image
from typing import Iterable


class OCRBackend:
    name: str

    def __init__(self):
        if not hasattr(self, 'name'):
            raise ValueError('OCR backend should have _name property')

    def recognize(self, image: Image.Image) -> str:
        raise NotImplementedError


class OCRBackendManager:
    def __init__(self, backends: Iterable[type[OCRBackend]]):
        self._objects = ObservableDict({b: b() for b in backends})
        self._objects[DummyOCRBackend] = DummyOCRBackend()
        self._current = self._objects[DummyOCRBackend]

    def register(self, backend: type[OCRBackend]):
        if backend in self._objects.keys():
            raise KeyError('OCR backend already exists')
        self._objects[backend] = backend()

    def unregister(self, backend: type[OCRBackend]):
        if backend not in self._objects.keys():
            raise KeyError('OCR backend does not exists')
        self._objects.pop(backend)

    def set(self, backend: type[OCRBackend]):
        self._current = self._objects[backend]

    def get_by_name(self, backend: str):
        for b in self._objects.keys():
            if b.name == backend:
                return b
        raise KeyError('OCR backend does not exists')

    def current(self) -> OCRBackend:
        return self._current

    @property
    def objects(self):
        return self._objects


class DummyOCRBackend(OCRBackend):
    name = 'Dummy'

    def recognize(self, image):
        return "Dummy OCR text for development testing."

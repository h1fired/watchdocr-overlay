from enum import IntEnum


class TranslationStatus(IntEnum):
    ERROR = 0
    SUCCESS = 1


class TranslationBackend:

    def load(self):
        pass

    def translate(self, text: str, translate_to: str):
        raise NotImplementedError
